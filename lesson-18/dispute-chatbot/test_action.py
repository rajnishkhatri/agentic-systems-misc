import chainlit as cl

@cl.on_chat_start
async def start():
    actions = [
        cl.Action(name="test_action", payload={"value": "test"}, label="Test Action")
    ]
    await cl.Message(content="Test Action", actions=actions).send()

@cl.action_callback("test_action")
async def on_test(action: cl.Action):
    print(f"Action received: {action}")
    print(f"Action type: {type(action)}")
    print(f"Payload: {action.payload}")
    print(f"Payload type: {type(action.payload)}")
    await cl.Message(content=f"Payload: {action.payload}").send()



