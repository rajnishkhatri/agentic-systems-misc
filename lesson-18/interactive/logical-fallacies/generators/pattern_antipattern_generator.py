import json
import os


class PatternAntiPatternGenerator:
    def __init__(self, data_path=None):
        if data_path is None:
            # Default to ../data relative to this file
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_path, "data")
        self.data_path = data_path
        
        with open(os.path.join(data_path, "patterns-anti-patterns.json"), 'r') as f:
            self.patterns = json.load(f)
            self.pattern_map = {p["fallacy_id"]: p for p in self.patterns}

    def get_pattern_pair(self, fallacy_id):
        return self.pattern_map.get(fallacy_id)

