import unittest
import pandas as pd
from datetime import datetime, date
from DataCleaner import add_days_difference_column, clean_date_string

class TestOperations(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "start": ["2024-01-01", "2024-02-28", "2024-05-10"],
            "end":   ["2024-01-10", "2024-03-01", "2024-05-06"]
        })

    def test_normalDiff(self):
        result = add_days_difference_column(self.df.copy(), "start", "end")
        self.assertListEqual(result["days_diff"].tolist(), [9, 2, -4],"Date Difference is incorrect"
        )
    
    def test_CleanDate(self):
        selected_date = self.df["start"].iloc[0]
        date2 = pd.to_datetime(date(2024,1,1))#, format='%Y-%m-%d')
        cleaned_date = pd.to_datetime(clean_date_string(selected_date))#.apply(clean_date_string)
        self.assertEqual(cleaned_date, date2,"Dates are not the same")

if __name__ == "__main__":
    unittest.main()