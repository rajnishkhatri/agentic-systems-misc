import json
import os


class PhaseDataGenerator:
    def __init__(self, data_path=None):
        if data_path is None:
            # Default to ../data relative to this file
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_path, "data")
        self.data_path = data_path

        with open(os.path.join(data_path, "polya-phases.json"), "r") as f:
            self.phases = json.load(f)
            self.phase_map = {p["phase"]: p for p in self.phases}

    def get_phases(self):
        return self.phases

    def get_phase(self, phase_name):
        return self.phase_map.get(phase_name)
