import json
import os
import random


class FallacyExampleGenerator:
    def __init__(self, data_path=None):
        if data_path is None:
            # Default to ../data relative to this file
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_path, "data")
        self.data_path = data_path

        # Load core data
        with open(os.path.join(data_path, "fallacies-data.json"), "r") as f:
            self.fallacies = {item["id"]: item for item in json.load(f)}

        with open(os.path.join(data_path, "dispute-grounding.json"), "r") as f:
            # Group grounding by fallacy_id
            self.grounding = {}
            for item in json.load(f):
                fid = item.get("fallacy_id")
                if fid not in self.grounding:
                    self.grounding[fid] = []
                self.grounding[fid].append(item)

    def generate(self, fallacy_id):
        if fallacy_id not in self.fallacies:
            raise ValueError(f"Unknown fallacy ID: {fallacy_id}")

        fallacy_data = self.fallacies[fallacy_id]

        # Dispatch to specific generator
        if fallacy_id == "cherry_picked_benchmarks":
            example = self._generate_cherry_picked()
        else:
            # Generic fallback or raise NotImplemented
            example = self._get_generic_example(fallacy_id)

        return {
            "id": fallacy_data["id"],
            "name": fallacy_data["name"],
            "description": fallacy_data["description"],
            "category": fallacy_data["category"],
            "ai_context": fallacy_data["ai_context"],
            "example": example,
        }

    def _generate_cherry_picked(self):
        # Get grounding data
        grounding_list = self.grounding.get("cherry_picked_benchmarks", [])
        if not grounding_list:
            raise ValueError("No grounding data found for cherry_picked_benchmarks")

        # Select one example (randomly or first one)
        # For now, just take the first one or random
        selected = random.choice(grounding_list)

        return {
            "title": selected["title"],
            "scenario": selected["scenario"],
            "ground_truth": selected["ground_truth"],
            "reality": selected["reality"],
            "dataset_references": selected["dataset_references"],
        }

    def _get_generic_example(self, fallacy_id):
        return {}
