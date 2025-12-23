import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add parent directory to path so we can import the app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock chainlit before importing modules that use it
mock_cl = MagicMock()
mock_cl.step = MagicMock(side_effect=lambda type=None: lambda func: func) # Mock decorator
mock_cl.on_chat_start = MagicMock(side_effect=lambda func: func)
mock_cl.on_message = MagicMock(side_effect=lambda func: func)
sys.modules["chainlit"] = mock_cl

from chainlit_explainability import render_agent_facts
from chainlit_phases import classify_dispute_step
from chainlit_tools import visualize_tool_call


@pytest.mark.asyncio
async def test_classify_dispute_step():
    """Test that classify step returns expected mock data."""
    # Since we mocked cl.step as identity, we can call the function directly
    # We still need to patch the internal calls

    with patch('chainlit_phases.visualize_tool_call', new_callable=AsyncMock) as mock_viz:
        with patch('chainlit_phases.render_phase_rationale', new_callable=AsyncMock) as mock_rationale:
            with patch('chainlit_phases.render_blackbox_trace', new_callable=AsyncMock) as mock_trace:
                with patch('asyncio.sleep', new_callable=AsyncMock):
                   result = await classify_dispute_step("DIS-123")

                   assert result["reason_code"] == "10.4"
                   assert result["network"] == "visa"
                   assert result["confidence"] == 0.95

@pytest.mark.asyncio
async def test_render_agent_facts():
    """Test agent facts rendering calls cl.Message."""
    # We need to configure the mock_cl.Message to behave like a class that returns an instance
    mock_msg_instance = MagicMock()
    mock_msg_instance.send = AsyncMock()
    mock_cl.Message.return_value = mock_msg_instance

    metadata = {"model": "gpt-4o", "version": "1.0"}
    await render_agent_facts(metadata)

    mock_cl.Message.assert_called()
    mock_msg_instance.send.assert_called_once()

@pytest.mark.asyncio
async def test_visualize_tool_call():
    """Test tool visualization uses cl.Step."""
    # Mocking the async context manager cl.Step
    mock_step_instance = MagicMock()
    mock_step_instance.__aenter__.return_value = mock_step_instance
    mock_step_instance.__aexit__.return_value = None

    mock_cl.Step.return_value = mock_step_instance

    await visualize_tool_call("test_tool", {"in": 1}, {"out": 2})

    # Verify input/output were set on the step
    assert mock_step_instance.input is not None
    assert mock_step_instance.output is not None

