import pytest
import json
import os
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
FALLACIES_FILE = DATA_DIR / "fallacies-data.json"
PATTERNS_FILE = DATA_DIR / "patterns-anti-patterns.json"
DISPUTE_FILE = DATA_DIR / "dispute-grounding.json"
HW_METHODS_FILE = DATA_DIR / "hw-counter-methods.json"
PHASES_FILE = DATA_DIR / "polya-phases.json"

@pytest.fixture
def load_json():
    def _load(path):
        with open(path, 'r') as f:
            return json.load(f)
    return _load

def test_data_files_exist():
    assert FALLACIES_FILE.exists()
    assert PATTERNS_FILE.exists()
    assert DISPUTE_FILE.exists()
    assert HW_METHODS_FILE.exists()
    assert PHASES_FILE.exists()

def test_fallacies_integrity(load_json):
    fallacies = load_json(FALLACIES_FILE)
    ids = [f['id'] for f in fallacies]
    assert len(ids) == len(set(ids)), "Fallacy IDs must be unique"
    
def test_patterns_integrity(load_json):
    patterns = load_json(PATTERNS_FILE)
    fallacies = load_json(FALLACIES_FILE)
    fallacy_ids = {f['id'] for f in fallacies}
    
    for p in patterns:
        assert 'fallacy_id' in p
        assert p['fallacy_id'] in fallacy_ids, f"Pattern references unknown fallacy_id: {p['fallacy_id']}"
        assert 'pattern' in p
        assert 'anti_pattern' in p

def test_dispute_integrity(load_json):
    disputes = load_json(DISPUTE_FILE)
    fallacies = load_json(FALLACIES_FILE)
    fallacy_ids = {f['id'] for f in fallacies}
    
    for d in disputes:
        assert 'fallacy_id' in d
        assert d['fallacy_id'] in fallacy_ids, f"Dispute references unknown fallacy_id: {d['fallacy_id']}"
        
def test_hw_methods_integrity(load_json):
    methods = load_json(HW_METHODS_FILE)
    fallacies = load_json(FALLACIES_FILE)
    fallacy_ids = {f['id'] for f in fallacies}
    
    for m in methods:
        assert 'fallacy_id' in m
        assert m['fallacy_id'] in fallacy_ids, f"HW Method references unknown fallacy_id: {m['fallacy_id']}"

def test_phases_integrity(load_json):
    phases = load_json(PHASES_FILE)
    expected_phases = {"UNDERSTAND", "PLAN", "TASKS", "EXECUTE", "REFLECT", "COUNTER"}
    phase_ids = {p['phase'] for p in phases}
    
    assert phase_ids == expected_phases, f"Phases mismatch. Expected {expected_phases}, got {phase_ids}"

if __name__ == "__main__":
    pytest.main([__file__])

