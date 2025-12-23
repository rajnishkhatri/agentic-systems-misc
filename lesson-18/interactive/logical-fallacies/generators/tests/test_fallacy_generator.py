import os

import pytest

from ..fallacy_example_generator import FallacyExampleGenerator


@pytest.fixture
def generator():
    # Assuming the data is relative to the generator file or passed in
    # tests/ -> generators/ -> logical-fallacies/
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_path, "data")
    return FallacyExampleGenerator(data_path=data_path)


def test_generator_initialization(generator):
    assert generator is not None


def test_generate_cherry_picked_benchmarks(generator):
    result = generator.generate("cherry_picked_benchmarks")

    assert result is not None
    assert result["id"] == "cherry_picked_benchmarks"
    assert "name" in result
    assert "description" in result
    assert "example" in result

    example = result["example"]
    assert "scenario" in example
    assert "ground_truth" in example
    assert "reality" in example
    assert "dataset_references" in example

    # Check that it pulled from the dispute-grounding.json
    assert "Dispute Classifier" in example["title"]
    assert "ReasonCodeClassifier" in example["scenario"]


def test_generate_unknown_fallacy(generator):
    with pytest.raises(ValueError):
        generator.generate("non_existent_fallacy")
