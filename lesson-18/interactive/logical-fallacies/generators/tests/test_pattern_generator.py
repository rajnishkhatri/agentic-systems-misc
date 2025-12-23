import os

import pytest

from ..pattern_antipattern_generator import PatternAntiPatternGenerator


@pytest.fixture
def generator():
    # tests/ -> generators/ -> logical-fallacies/
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_path, "data")
    return PatternAntiPatternGenerator(data_path=data_path)


def test_get_pattern_pair(generator):
    pair = generator.get_pattern_pair("cherry_picked_benchmarks")
    assert pair is not None
    assert pair["fallacy_id"] == "cherry_picked_benchmarks"

    assert "anti_pattern" in pair
    assert "pattern" in pair

    ap = pair["anti_pattern"]
    assert "title" in ap
    assert "description" in ap
    assert "red_flags" in ap
    assert "code_smell" in ap

    p = pair["pattern"]
    assert "title" in p
    assert "description" in p
    assert "best_practices" in p
    assert "code_template" in p


def test_get_pattern_pair_invalid(generator):
    pair = generator.get_pattern_pair("INVALID_ID")
    assert pair is None
