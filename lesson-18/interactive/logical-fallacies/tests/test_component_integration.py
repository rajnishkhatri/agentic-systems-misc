import json
from pathlib import Path

import pytest

# Paths
BASE_DIR = Path("lesson-18/interactive/logical-fallacies")
DATA_DIR = BASE_DIR / "data"
COMPONENTS_DIR = BASE_DIR / "components"

def load_json(filename):
    path = DATA_DIR / filename
    assert path.exists(), f"{filename} not found"
    with open(path, "r") as f:
        return json.load(f)

def test_components_exist():
    """Verify all React components exist."""
    components = [
        "FallacyCard.jsx",
        "PatternAntiPatternCard.jsx",
        "PolyaPhaseFlow.jsx",
        "WorkedExampleBreakdown.jsx",
        "QuizMode.jsx"
    ]
    for comp in components:
        assert (COMPONENTS_DIR / comp).exists(), f"{comp} missing"

def test_fallacy_card_contract():
    """Verify FallacyCard data contract."""
    data = load_json("fallacies-data.json")
    assert isinstance(data, list)
    assert len(data) > 0
    
    for item in data:
        # FallacyCard expects: category, name, description, ai_context
        assert "category" in item
        assert "name" in item
        assert "description" in item
        assert "ai_context" in item
        assert "id" in item # Used for key

def test_pattern_card_contract():
    """Verify PatternAntiPatternCard data contract."""
    data = load_json("patterns-anti-patterns.json")
    for item in data:
        # PatternAntiPatternCard expects: anti_pattern, pattern
        assert "anti_pattern" in item
        assert "pattern" in item
        
        ap = item["anti_pattern"]
        assert "title" in ap
        assert "description" in ap
        assert "red_flags" in ap
        assert isinstance(ap["red_flags"], list)
        assert "code_smell" in ap
        
        p = item["pattern"]
        assert "title" in p
        assert "description" in p
        assert "best_practices" in p
        assert isinstance(p["best_practices"], list)
        assert "code_template" in p

def test_polya_phase_flow_contract():
    """Verify PolyaPhaseFlow data contract."""
    data = load_json("polya-phases.json")
    phases = ["UNDERSTAND", "PLAN", "TASKS", "EXECUTE", "REFLECT", "COUNTER"]
    
    found_phases = [p["phase"] for p in data]
    assert found_phases == phases
    
    for item in data:
        assert "phase" in item
        assert "icon" in item
        assert "description" in item
        assert "key_elements" in item
        assert isinstance(item["key_elements"], list)

def test_worked_example_contract():
    """Verify WorkedExampleBreakdown data contract."""
    data = load_json("dispute-grounding.json")
    for item in data:
        # WorkedExampleBreakdown expects: title, scenario, ground_truth, reality, dataset_references
        assert "title" in item
        assert "scenario" in item
        assert "ground_truth" in item
        assert "reality" in item
        assert "dataset_references" in item
        assert isinstance(item["dataset_references"], list)

def test_hw_methods_contract():
    """Verify HW Counter Methods data contract."""
    data = load_json("hw-counter-methods.json")
    for item in data:
        # Used in PatternAntiPatternCard footer or Counter phase
        assert "hw_method" in item
        assert "technique" in item
        assert "description" in item
        assert "code_reference" in item

if __name__ == "__main__":
    # Allow running directly
    pytest.main([__file__])

