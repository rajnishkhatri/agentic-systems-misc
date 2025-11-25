"""Generate a 50-turn mock conversation and show compression output.

Run:
    python scripts/mock_conversation_demo.py
"""

from __future__ import annotations

from backend.sessions.context_compressor import ContextCompressor


def build_mock_conversation() -> list[dict]:
    """Create 50 turns mixing protected constraints and compressible chatter."""
    protected_turns = {0, 12, 25, 37}
    events: list[dict] = []

    for turn in range(50):
        role = "user" if turn % 2 == 0 else "assistant"
        event_type = (
            "initial_objective"
            if turn == 0
            else "constraint"
            if turn in protected_turns - {0}
            else "clarification"
            if role == "user"
            else "explanation"
        )
        content_overrides = {
            0: "Initial objective: Map karma yoga study plan",
            12: "Constraint: Always cite chapter/verse",
            25: "Constraint: Keep answers under 200 tokens",
            37: "Constraint: Summaries should be bulletized",
        }
        content = content_overrides.get(turn, f"{role.title()} turn {turn}: discussing karma yoga detail")

        events.append(
            {
                "turn": turn,
                "role": role,
                "event_type": event_type,
                "content": content,
                "is_protected": turn in protected_turns,
            }
        )

    return events


def main() -> None:
    """Build mock conversation, compress, and print readable output."""
    compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)
    events = build_mock_conversation()
    print("Original Events")
    for event in events:
        print(event)
    
    compressed = compressor.compress(events)

    print(f"Original events: {len(events)}")
    print(f"Compressed events: {len(compressed)}\\n")

    print("Compressed output:") 
    for event in compressed:
        print(event)


if __name__ == "__main__":
    main()

