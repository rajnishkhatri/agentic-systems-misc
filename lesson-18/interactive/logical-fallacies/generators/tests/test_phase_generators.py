import os

import pytest

from ..phase_data_generators import PhaseDataGenerator


@pytest.fixture
def generator():
    # tests/ -> generators/ -> logical-fallacies/
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_path, "data")
    return PhaseDataGenerator(data_path=data_path)

def test_get_all_phases(generator):
    phases = generator.get_phases()
    assert len(phases) == 6
    assert phases[0]["phase"] == "UNDERSTAND"
    assert phases[5]["phase"] == "COUNTER"
    
def test_get_phase_by_name(generator):
    phase = generator.get_phase("PLAN")
    assert phase is not None
    assert phase["phase"] == "PLAN"
    assert "strategy" in phase["description"].lower()

def test_get_phase_invalid(generator):
    phase = generator.get_phase("INVALID_PHASE")
    assert phase is None

