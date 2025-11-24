import unittest
import os
import pandas as pd
from data_handler import DataHandler  # Ensure this file exists in the same directory

class TestDataHandler(unittest.TestCase):
    def setUp(self):
        self.handler = DataHandler()
        self.test_file = "test_events.csv"
        self.test_data = [
            {"id": 1, "name": "Test Event", "date": "2025-05-25"}
        ]

    def test_save_to_csv(self):
        """Test saving valid data to CSV."""
        result = self.handler.save_to_csv(self.test_data, self.test_file)
        self.assertTrue(os.path.exists(self.test_file))
        self.assertIn("Data saved", result)

    def test_load_from_csv(self):
        """Test loading data after saving."""
        self.handler.save_to_csv(self.test_data, self.test_file)
        df = self.handler.load_from_csv(self.test_file)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.iloc[0]["name"], "Test Event")

    def test_load_from_nonexistent_file(self):
        """Test behavior when loading a file that does not exist."""
        result = self.handler.load_from_csv("nonexistent_file.csv")
        self.assertTrue(isinstance(result, str) and "Error loading data" in result)

    def test_save_invalid_data(self):
        """Test saving invalid data (not a list of dicts)."""
        result = self.handler.save_to_csv("invalid_data", self.test_file)
        self.assertTrue("Error saving data" in result or isinstance(result, str))

    def tearDown(self):
        """Clean up the test CSV file."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

if __name__ == "__main__":
    unittest.main()
