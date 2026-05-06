import unittest
import pandas as pd
from datetime import datetime, date
from DataCleaner import add_days_difference_column, clean_date_string, quarantine_dateGapIssues
import tempfile
import os

#----------------------
# SET UP TEST DATAFRAME
#----------------------

class TestOperations(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "start": ["2024-01-01", "2024-02-28", "2024-03-01", "2024-04-06", "2024-05-10"],
            "end":   ["2024-01-10", "2024-03-01", "2024-03-21", "2024-05-03", "2024-05-06"],
            "id": [1, 2, 3, 4, 5],
            "days_between": [10, -5, 0, 7, -2],
            "name": ["Alice", "Bob", "Charlie", "David", "Eve"]
        })


#--------------------------------
# TEST add_days_difference_column
#--------------------------------

    def test_normalDiff(self):
        result = add_days_difference_column(self.df.copy(), "start", "end")
        self.assertListEqual(result["days_diff"].tolist(), [9, 2, 20, 27, -4],"Date Difference is incorrect"
        )

#--------------------------------
# TEST clean_date_string
#--------------------------------

    def test_CleanDate(self):
        selected_date = self.df["start"].iloc[0]
        date2 = pd.to_datetime(date(2024,1,1))#, format='%Y-%m-%d')
        cleaned_date = pd.to_datetime(clean_date_string(selected_date))#.apply(clean_date_string)
        self.assertEqual(cleaned_date, date2,"Dates are not the same")


#--------------------------------
# TEST quarantine_dateGapIssues
#--------------------------------

    def test_quarantine_dateGapIssues(self):
        # Test that negatives are saved to CSV and positives returned as DataFrame.
        with tempfile.TemporaryDirectory() as tmpdir:
            removed_file_path = os.path.join(tmpdir, "removed.csv")

            # Run the function
            positive_df = quarantine_dateGapIssues(
                self.df,
                column_name="days_between",
                removed_file=removed_file_path
            )

            # Check positive_df content
            expected_positive_ids = [1, 3, 4]  # IDs with positive days_between
            self.assertListEqual(list(positive_df["id"]), expected_positive_ids)

            # Check that CSV file exists
            self.assertTrue(os.path.exists(removed_file_path))

            # Check negative CSV content
            negative_df = pd.read_csv(removed_file_path)
            expected_negative_ids = [2, 5] # IDs with negative days_between
            self.assertListEqual(list(negative_df["id"]), expected_negative_ids)


#--------------------
# RUN TESTS
#--------------------

if __name__ == "__main__":
    unittest.main()