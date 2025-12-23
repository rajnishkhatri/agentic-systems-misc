import chainlit as cl
from backend.orchestrators.ui_orchestrator import UIOrchestrator

@cl.on_chat_start
async def start():
    """
    Initializes the session and sends a welcome message with Network Selection.
    """
    cl.user_session.set("dispute_state", "INIT")
    cl.user_session.set("selected_network", None)  # Initialize

    # Initialize UI Orchestrator
    # We create a new instance for each session
    orchestrator = UIOrchestrator()
    cl.user_session.set("orchestrator", orchestrator)
    
    welcome_message = """
    # 🛡️ Dispute Resolution Agent
    
    Welcome! I can help you resolve merchant disputes for Visa (Fraud 10.4 & PNR 13.1).
    
    **First, please select the Card Network for this dispute:**
    """
    
    # Create Actions for Network Selection
    actions = [
        cl.Action(name="network_select", payload={"value": "visa"}, label="Visa"),
        cl.Action(name="network_select", payload={"value": "mastercard"}, label="Mastercard"),
        cl.Action(name="network_select", payload={"value": "amex"}, label="American Express"),
        cl.Action(name="network_select", payload={"value": "discover"}, label="Discover")
    ]
    
    await cl.Message(content=welcome_message, actions=actions).send()


@cl.action_callback("network_select")
async def on_network_select(action: cl.Action):
    """Handle network selection."""
    # Debugging payload structure
    print(f"DEBUG: Action received: {action}")
    print(f"DEBUG: Payload type: {type(action.payload)}")
    print(f"DEBUG: Payload content: {action.payload}")

    # Defensive payload extraction
    if isinstance(action.payload, dict):
        network = action.payload.get("value")
    else:
        # Fallback if payload is flattened or different type
        network = action.payload

    if not network:
         await cl.Message(content="❌ **Error:** Could not determine selected network. Please try again.").send()
         return

    cl.user_session.set("selected_network", network)
    
    # Confirm selection and ask for description
    await cl.Message(content=f"✅ **Selected Network:** {action.label}\n\nNow, please describe the dispute in detail (e.g., 'I was charged twice for the same item').").send()
    
    # Remove buttons from previous message (optional UI cleanup)
    # await action.remove()


@cl.on_message
async def main(message: cl.Message):
    """
    Main orchestrator loop using State Machine.
    """
    # 1. Validate Network Selection
    selected_network = cl.user_session.get("selected_network")
    
    if not selected_network:
        # Re-prompt if they type without selecting
        actions = [
            cl.Action(name="network_select", payload={"value": "visa"}, label="Visa"),
            cl.Action(name="network_select", payload={"value": "mastercard"}, label="Mastercard"),
            cl.Action(name="network_select", payload={"value": "amex"}, label="American Express"),
            cl.Action(name="network_select", payload={"value": "discover"}, label="Discover")
        ]
        await cl.Message(content="⚠️ **Please select a network first** before describing the issue:", actions=actions).send()
        return

    orchestrator: UIOrchestrator = cl.user_session.get("orchestrator")
    
    # Prepare task input with explicit network
    # In a real app, we might parse the input to distinguish ID vs description
    task = {
        "task_id": message.id,
        "dispute_id": message.content.strip().split()[0] if "DIS-" in message.content else "DIS-UNKNOWN",
        "description": message.content,
        "network": selected_network  # INJECTED FROM SESSION
    }
    
    await cl.Message(content=f"🔄 **Starting Resolution Workflow**\nNetwork: {selected_network.title()}\nInput: {message.content[:100]}...").send()

    
    try:
        # Execute the full state machine workflow
        # The UIOrchestrator will handle visualization of each phase via cl.Step
        result = await orchestrator.execute(task)
        
        final_state = result["final_state"]
        final_output = result["final_output"]
        
        # Display final result
        if result["status"] == "success":
            response_content = f"""## ✅ Workflow Completed
            
**Final State:** {final_state}

**Outcome:**
```json
{final_output}
```
"""
            await cl.Message(content=response_content).send()
        else:
            await cl.Message(content=f"❌ **Workflow Failed**\nError: {result.get('error')}").send()
             
    except Exception as e:
        await cl.Message(content=f"❌ **System Error**: {str(e)}").send()
