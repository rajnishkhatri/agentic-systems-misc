import json
import os
import time
from enum import Enum
from dataclasses import dataclass, asdict

# Mock Redis/Storage
STATE_FILE = "dispute_state_store.json"

class DisputeState(str, Enum):
    CLASSIFY = "CLASSIFY"
    GATHER_EVIDENCE = "GATHER_EVIDENCE"
    VALIDATE = "VALIDATE"
    SUBMIT = "SUBMIT"
    MONITOR = "MONITOR"

@dataclass
class WorkflowContext:
    dispute_id: str
    state: DisputeState
    data: dict

class StateManager:
    def __init__(self, storage_file=STATE_FILE):
        self.storage_file = storage_file

    def save_state(self, context: WorkflowContext):
        data = asdict(context)
        with open(self.storage_file, "w") as f:
            json.dump(data, f)
        print(f"[Storage] Saved state: {context.state}")

    def load_state(self) -> WorkflowContext:
        if not os.path.exists(self.storage_file):
            return None
        
        with open(self.storage_file, "r") as f:
            data = json.load(f)
        
        return WorkflowContext(
            dispute_id=data["dispute_id"],
            state=DisputeState(data["state"]),
            data=data["data"]
        )

def run_test():
    # Clean up previous run
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

    print("--- Phase 1: Initial Execution ---")
    # 1. Start Process
    context = WorkflowContext(
        dispute_id="dsp_123", 
        state=DisputeState.CLASSIFY, 
        data={"amount": 100}
    )
    manager = StateManager()
    
    # 2. Transition to GATHER_EVIDENCE
    context.state = DisputeState.GATHER_EVIDENCE
    context.data["classified"] = True
    manager.save_state(context)
    
    print("Process crashing...")
    # Simulate crash by deleting object reference (in memory)
    del context
    del manager
    
    print("\n--- Phase 2: Recovery after Restart ---")
    # 3. Restart (New Instance)
    new_manager = StateManager()
    recovered_context = new_manager.load_state()
    
    if recovered_context:
        print(f"Recovered State: {recovered_context.state}")
        print(f"Recovered Data: {recovered_context.data}")
        
        # Verify
        if recovered_context.state == DisputeState.GATHER_EVIDENCE and recovered_context.data.get("classified"):
            print("SUCCESS: State recovered correctly.")
        else:
            print("FAILURE: State mismatch.")
    else:
        print("FAILURE: Could not load state.")
        
    # Cleanup
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

if __name__ == "__main__":
    run_test()

