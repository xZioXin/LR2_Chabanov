import unittest
import os
import json
import tempfile
from main import ElectricityCounter, DAY_RATE, NIGHT_RATE, ROLLOVER_DAY, ROLLOVER_NIGHT

class TestElectricityCounter(unittest.TestCase):

    def setUp(self):
        self.data_file_path = os.path.join(tempfile.gettempdir(), "test_counters_data.json")

        self.initial_data = {
            "counters": {
                "counter1": {"day": 1000, "night": 500, "last_date": "2023-01-01"},
                "counter2": {"day": 2000, "night": 1000, "last_date": "2023-01-01"}
            },
            "bills": []
        }

        with open(self.data_file_path, 'w') as f:
            json.dump(self.initial_data, f)

        import main
        main.DATA_FILE = self.data_file_path

        self.counter = ElectricityCounter()

    def tearDown(self):
        if os.path.exists(self.data_file_path):
            os.remove(self.data_file_path)

    def test_new_counter(self):
        result = self.counter.process_counter("counter_new", 100, 50, "2023-01-02")
        self.assertEqual(result['status'], "new_counter")

    def test_update_existing_counter(self):
        result = self.counter.process_counter("counter1", 1100, 600, "2023-01-02")
        self.assertEqual(result['status'], "processed")

    def test_lower_both_values(self):
        result = self.counter.process_counter("counter1", 100, 100, "2023-01-02")
        self.assertEqual(result['status'], "processed")
        self.assertTrue(result.get('rollover_applied', False))

    def test_lower_day_values(self):
        result = self.counter.process_counter("counter1", 100, 600, "2023-01-02")
        self.assertEqual(result['status'], "processed")
        self.assertTrue(result.get('rollover_applied', False))

    def test_lower_night_values(self):
        result = self.counter.process_counter("counter1", 1100, 100, "2023-01-02")
        self.assertEqual(result['status'], "processed")
        self.assertTrue(result.get('rollover_applied', False))

    def test_history_storage(self):
        initial_bills_count = len(self.counter.counters["bills"])
        self.counter.process_counter("counter1", 1100, 600, "2023-01-02")
        self.assertEqual(len(self.counter.counters["bills"]), initial_bills_count + 1)

if __name__ == '__main__':
    unittest.main()
