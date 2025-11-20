#!/usr/bin/env python3
"""
TDD phase management script for /tdd command.

Provides phase-specific guidance for Test-Driven Development workflow:
- RED: Write failing test
- GREEN: Minimal implementation
- REFACTOR: Improve code quality
- STATUS: Display current phase and guidance
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class TDDPhaseManager:
    """Manages TDD phase state and provides phase-specific guidance."""

    STATE_FILE = Path(".claude/.tdd-state.json")
    VALID_PHASES = ["red", "green", "refactor", "status"]

    def __init__(self):
        """Initialize TDD phase manager."""
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        """Load TDD phase state from file.

        Returns:
            State dictionary with current phase and history
        """
        if not self.STATE_FILE.exists():
            return {
                "current_phase": None,
                "last_updated": None,
                "history": [],
            }

        try:
            with open(self.STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Return default state if file is corrupted
            return {
                "current_phase": None,
                "last_updated": None,
                "history": [],
            }

    def _save_state(self) -> None:
        """Save TDD phase state to file."""
        # Ensure .claude directory exists
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(self.STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def _add_to_history(self, phase: str, test_name: str | None = None) -> None:
        """Add phase transition to history.

        Args:
            phase: Phase name (red/green/refactor)
            test_name: Optional test name for RED phase
        """
        entry: dict[str, Any] = {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
        }

        if test_name:
            entry["test_name"] = test_name

        self.state["history"].append(entry)

        # Keep only last 10 entries
        if len(self.state["history"]) > 10:
            self.state["history"] = self.state["history"][-10:]

    def red(self, test_name: str | None = None) -> str:
        """Enter RED phase - Write failing test.

        Args:
            test_name: Optional test name to track

        Returns:
            Guidance message for RED phase
        """
        self.state["current_phase"] = "red"
        self.state["last_updated"] = datetime.now().isoformat()
        self._add_to_history("red", test_name)
        self._save_state()

        return """🔴 RED Phase Active

Write a failing test for the next behavior.

Reminders:
✅ ONE failing test only
✅ Naming: test_should_[result]_when_[condition]()
✅ Run test to confirm it fails
❌ NO implementation code

Next step: Run pytest to verify failure → /tdd green"""

    def green(self) -> str:
        """Enter GREEN phase - Write minimal code to pass test.

        Returns:
            Guidance message for GREEN phase
        """
        self.state["current_phase"] = "green"
        self.state["last_updated"] = datetime.now().isoformat()
        self._add_to_history("green")
        self._save_state()

        return """🟢 GREEN Phase Active

Write minimal code to make the test pass.

Reminders:
✅ Minimal code only (no extras)
✅ Run test to confirm it passes
❌ NO test modifications
❌ NO additional features

Next step: Run pytest to verify pass → /tdd refactor"""

    def refactor(self) -> str:
        """Enter REFACTOR phase - Improve code quality.

        Returns:
            Guidance message for REFACTOR phase
        """
        self.state["current_phase"] = "refactor"
        self.state["last_updated"] = datetime.now().isoformat()
        self._add_to_history("refactor")
        self._save_state()

        return """🔵 REFACTOR Phase Active

Improve code quality. Keep tests passing.

Reminders:
✅ Apply defensive coding (type hints, validation, error handling)
✅ Improve readability and DRY
✅ Run pytest after EACH change
✅ All tests must stay green

Defensive coding checklist:
  [ ] Type hints on all functions
  [ ] Input validation with guard clauses
  [ ] Specific exception handling
  [ ] Descriptive error messages

Next step: When done → /tdd red (next behavior)"""

    def status(self) -> str:
        """Display current phase and guidance.

        Returns:
            Status message with current phase and history
        """
        if not self.state["current_phase"]:
            return """📊 TDD Status

No active phase. Start with:
  /tdd red    - Write failing test
  /tdd green  - Minimal implementation
  /tdd refactor - Improve code quality

TDD Workflow: RED → GREEN → REFACTOR → RED (next behavior)"""

        # Phase emoji mapping
        phase_emoji = {
            "red": "🔴 RED",
            "green": "🟢 GREEN",
            "refactor": "🔵 REFACTOR",
        }

        # Get phase-specific guidance
        phase_guidance = {
            "red": """Write a failing test for the next behavior.

Reminders:
✅ ONE failing test only
✅ Naming: test_should_[result]_when_[condition]()
✅ Run test to confirm it fails
❌ NO implementation code

Next step: Run pytest to verify failure → /tdd green""",
            "green": """Write minimal code to make the test pass.

Reminders:
✅ Minimal code only (no extras)
✅ Run test to confirm it passes
❌ NO test modifications
❌ NO additional features

Next step: Run pytest to verify pass → /tdd refactor""",
            "refactor": """Improve code quality. Keep tests passing.

Reminders:
✅ Apply defensive coding (type hints, validation, error handling)
✅ Improve readability and DRY
✅ Run pytest after EACH change
✅ All tests must stay green

Defensive coding checklist:
  [ ] Type hints on all functions
  [ ] Input validation with guard clauses
  [ ] Specific exception handling
  [ ] Descriptive error messages

Next step: When done → /tdd red (next behavior)""",
        }

        current_phase = self.state["current_phase"]
        last_updated = self.state.get("last_updated", "Unknown")

        # Format timestamp
        if last_updated and last_updated != "Unknown":
            try:
                dt = datetime.fromisoformat(last_updated)
                last_updated_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                last_updated_str = last_updated
        else:
            last_updated_str = "Unknown"

        status_msg = f"""📊 TDD Status

Current Phase: {phase_emoji.get(current_phase, current_phase.upper())}
Last Updated: {last_updated_str}

Phase Guidance:
{phase_guidance.get(current_phase, "Unknown phase")}

---

Phase History:"""

        # Add history
        if self.state["history"]:
            for entry in self.state["history"][-5:]:  # Show last 5
                phase = entry["phase"]
                timestamp = entry.get("timestamp", "")
                test_name = entry.get("test_name")

                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime("%H:%M:%S")
                    except ValueError:
                        time_str = timestamp
                else:
                    time_str = "Unknown"

                phase_display = phase_emoji.get(phase, phase.upper())

                if test_name:
                    status_msg += f"\n{phase_display}  → {time_str} ({test_name})"
                else:
                    status_msg += f"\n{phase_display}  → {time_str}"

            # Mark current phase
            if self.state["history"]:
                status_msg += " (current)"
        else:
            status_msg += "\nNo history yet."

        status_msg += "\n\nTDD Workflow: RED → GREEN → REFACTOR → RED (next behavior)"

        return status_msg


def main() -> None:
    """Main entry point for /tdd command.

    Usage:
        python tdd.py [phase] [test_name]

    Args:
        phase: Optional phase to enter (red/green/refactor/status)
        test_name: Optional test name for RED phase tracking
    """
    manager = TDDPhaseManager()

    # Default to status if no phase provided
    phase = sys.argv[1] if len(sys.argv) > 1 else "status"
    phase = phase.lower()

    # Validate phase
    if phase not in manager.VALID_PHASES:
        print(f"❌ Invalid phase: {phase}")
        print(f"   Valid phases: {', '.join(manager.VALID_PHASES)}")
        print("\nUsage: /tdd [red|green|refactor|status]")
        sys.exit(1)

    # Execute phase command
    if phase == "red":
        test_name = sys.argv[2] if len(sys.argv) > 2 else None
        print(manager.red(test_name))
    elif phase == "green":
        print(manager.green())
    elif phase == "refactor":
        print(manager.refactor())
    elif phase == "status":
        print(manager.status())


if __name__ == "__main__":
    main()
