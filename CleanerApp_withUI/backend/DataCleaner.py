#--------------------------
# IMPORT REQUIRED LIBRARIES
#--------------------------
import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine
import urllib
import sys
import math
import os
import time

#--------------------------
# DEFINE FUNCTIONS
#--------------------------

# Function to process date columns
def process_all_date_columns(df: pd.DataFrame):
    """
    Detect and process all date-like columns in a DataFrame.
    
    - Converts to datetime safely.
    - Prints earliest and latest dates.
    - Skips columns with no valid dates.
    
    Args:
        df (pd.DataFrame): The DataFrame to process.
    
    Returns:
        pd.DataFrame: DataFrame with processed date columns.
    """
    try:
        # Detect columns that are already datetime or have 'date'/'time' in their name
        candidate_cols = [
            col for col in df.columns
            if pd.api.types.is_datetime64_any_dtype(df[col])
            or 'date' in col.lower()
            or 'time' in col.lower()
        ]
        
        if not candidate_cols:
            print("⏭ No date-like columns found. Skipping.")
            return df
        
        for col in candidate_cols:
            print(f"\nProcessing column: '{col}'")
            
            # Convert to datetime safely
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
            valid_dates = df[col].dropna()
            if not valid_dates.empty:
                print(f"   Earliest date: {valid_dates.min()}")
                print(f"   Latest date:   {valid_dates.max()}")
            else:
                print(f"⚠ Column '{col}' contains no valid dates.")
        
        return df
    
    except Exception as e:
        print(f"Error processing date columns: {e}")
        return df


# Function to check for duplicates
def DuplicateCheck(
    df: pd.DataFrame, 
    #column_name: str, 
    return_values: bool = False
):
    """
    Checks if specified column has any duplicate values

    Parameters:
        df (pd.DataFrame): The DataFrame to check.
        column_name (str): The column name to check for duplicates.
        return_values (bool): If True, returns the duplicate values instead of just True/False.

    Returns:
        bool | pd.Series: 
            - If return_values=False: True if duplicates exist, False otherwise.
            - If return_values=True: Series of duplicate values (may be empty).
    
    """
    # Loop through columns using iloc
    for col_index in range(df.shape[1]):  # df.shape[1] = number of columns
        column_data = df.iloc[:, col_index]  # Select column by index
        column_name = df.columns[col_index]
    
    # Define output messages
        duplicate_msg = f"Check Failed: Duplicate(s) found in Column: '{column_name}'"
        no_duplicate_msg = f"Check Passed: No Duplicate(s) found in Column: '{column_name}'"
    
    # Define duplicates test
        duplicates = df[column_name].duplicated(keep=False)

        if return_values:
            # Return only the duplicate values (unique)
            return df.loc[duplicates, column_name].drop_duplicates().reset_index(drop=True)
        else:
            return duplicate_msg if duplicates.any() else no_duplicate_msg

# Function to clean date strings
def clean_date_string(s):
    if pd.isna(s):
        return s
    s = str(s) # Ensure string type
    s = s.strip().strip('"').strip("'") # Remove surrounding quotes and spaces
    return s

# Function to add a column calculating the difference between dates
def add_days_difference_column(df, start_col, end_col, output_col="days_diff", absolute=False):
        """
        Adds a new column with the number of days between two date columns.

        Parameters:
            df (pd.DataFrame): Input DataFrame.
            start_col (str): Start date column name.
            end_col (str): End date column name.
            output_col (str): Name of the output column.
            absolute (bool): If True, returns absolute day differences.

        Returns:
            pd.DataFrame: DataFrame with the new column.
        """
        # Convert to datetime, invalid formats become NaT
        df[start_col] = pd.to_datetime(df[start_col], errors='coerce')
        df[end_col] = pd.to_datetime(df[end_col], errors='coerce')

        # Calculate difference in days
        diff = (df[end_col] - df[start_col]).dt.days

        df[output_col] = diff
        return df

# Function to remove date issue rows to a csv file as 'quarantine'
def quarantine_dateGapIssues(df, column_name="result", output_file="cleaned.csv", removed_file="removed.csv", return_data=True):
    try:
        # Convert to numeric for safe comparison
        df[column_name] = pd.to_numeric(df[column_name], errors="coerce")
        
        # Separate negative and non-negative rows
        negative_df = df[df[column_name] < 0]
        positive_df = df[df[column_name] >= 0]

        # Save negative results
        negative_df.to_csv(removed_file, index=False)

        # Log counts
        print(f"Cleaned data kept in DataFrame: {len(positive_df)}")
        print(f"Removed negative records saved to: {removed_file} ({len(negative_df)} records removed)")

        if return_data:
            return positive_df#, negative_df

    except Exception as e:
        print(f"Error: {e}")





WATCH_FOLDER = "/data"
PROCESSED_FOLDER = "/data/processed"
WATCH_INTERVAL = int(os.getenv("WATCH_INTERVAL", 5))

os.makedirs(WATCH_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

print(f"📂 Backend processor started. Watching '{WATCH_FOLDER}' every {WATCH_INTERVAL}s...")

while True:
    try:
        files = [f for f in os.listdir(WATCH_FOLDER) if f.lower().endswith(".csv")]
        for filename in files:
            filepath = os.path.join(WATCH_FOLDER, filename)
            processed_path = os.path.join(PROCESSED_FOLDER, f"processed_{filename}")

            # Skip already processed files
            if os.path.exists(processed_path):
                continue

            try:
                print(f"🔍 Found file: {filename}")
                df = pd.read_csv(filepath)

                # Calculate completeness
                start_completeness = 100-(df.isnull().mean() * 100)

                # Remove NaN values
                df = df.dropna(how='all')

                # Remove any leading or trailing spaces from values
                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

                # Process all date columns in the dataframe
                df = process_all_date_columns(df)

                # Calculate final completeness
                end_completeness = 100-(df.isnull().mean() * 100)

                #--------------------------
                # OUTPUT CLEANED CSV FILE
                #--------------------------

                # Show completeness variance after transformations
                print("Starting Completeness (%):")
                print(start_completeness)

                print("Finishing Completeness (%):")
                print(end_completeness)

                # Output Cleaned csv file
                df.to_csv(processed_path, index=False)
                print(f"✅ Processed '{filename}' -> '{processed_path}'")

                os.remove(filepath)
                print(f"🗑️ Deleted original '{filename}' after processing.")
            except Exception as e:
                print(f"❌ Error processing '{filename}': {e}")
        time.sleep(WATCH_INTERVAL)
    except Exception as e:
        print(f"⚠️ Watch loop error: {e}")
        time.sleep(WATCH_INTERVAL)