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

#--------------------------
# DEFINE FUNCTIONS
#--------------------------

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

                # Check if each column has duplicates
                print(DuplicateCheck(df))

                # Remove any leading or trailing spaces from values
                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

                # Apply cleaning
                df['Book checkout'] = df['Book checkout'].apply(clean_date_string)

                # Convert to datetime
                df['Book checkout'] = pd.to_datetime(df['Book checkout'], format='%d/%m/%Y', errors='coerce')

                # Convert Return date column to datetime
                df2['Book Returned'] = pd.to_datetime(df2['Book Returned'], format='%d/%m/%Y', errors='coerce')

                # Use add_days_difference_column function on Books df:
                df2 = add_days_difference_column(df2, "Book checkout", "Book Returned", "days_between", absolute=True)

                # Convert ID columns to integers instead of floats
                df2['Id'] = [int(x) for x in df2['Id']]
                df2['Customer ID'] = [int(x) for x in df2['Customer ID']]

                # Run quarantine function on Books df
                df2 = quarantine_dateGapIssues(
                    df2,
                    column_name = "days_between",
                    removed_file = "removed_bookRecords.csv"
                )

                # Calculate final completeness
                book_end_completeness = 100-(df2.isnull().mean() * 100)

                #--------------------------
                # OUTPUT TO CSV FILES
                #--------------------------

                df1.to_csv(r'cleanedFiles\CustomersCleaned.csv', index=False)
                df2.to_csv(r'cleanedFiles\BooksCleaned.csv', index=False)

                # Show completeness variance after transformations
                print("Customer Starting Completeness (%):")
                print(cust_start_completeness)

                print("Customer Finishing Completeness (%):")
                print(cust_end_completeness)

                print("Books Starting Completeness (%):")
                print(book_start_completeness)

                print("Books Finishing Completeness (%):")
                print(book_end_completeness)

                #--------------------------
                # OUTPUT TO SQL DATABASE
                #--------------------------

                # SQL Server connection details
                server = r'STUDENT01'      
                database = 'libraryProject' 

                # Define table for Customers data
                table_name = 'Customers'

                try:
                    # Build ODBC connection string
                    connection_string = (
                        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                        f"SERVER={server};"
                        f"DATABASE={database};"
                        f"Trusted_Connection=yes;"
                    )

                    # Encode for SQLAlchemy
                    connection_uri = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(connection_string)

                    # Create SQLAlchemy engine
                    engine = create_engine(connection_uri, fast_executemany=True)

                    # Export DataFrame to SQL Server
                    df1.to_sql(
                        name=table_name,
                        con=engine,
                        if_exists='replace',  # 'replace' overwrites, 'append' adds rows
                        index=False
                    )

                    print(f"✅ DataFrame successfully exported to table '{table_name}' in database '{database}'.")
                    print("You can now view it in SSMS.")

                except Exception as e:
                    print("Failed to export DataFrame to SQL Server.")
                    print("Error details:", e)
                    sys.exit(1)


                # Define table for Books data
                table_name = 'Books'

                try:
                    # Build ODBC connection string
                    connection_string = (
                        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                        f"SERVER={server};"
                        f"DATABASE={database};"
                        f"Trusted_Connection=yes;"
                    )

                    # Encode for SQLAlchemy
                    connection_uri = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(connection_string)

                    # Create SQLAlchemy engine
                    engine = create_engine(connection_uri, fast_executemany=True)

                    # Export DataFrame to SQL Server
                    df2.to_sql(
                        name=table_name,
                        con=engine,
                        if_exists='replace',  # 'replace' overwrites, 'append' adds rows
                        index=False
                    )

                    print(f"✅ DataFrame successfully exported to table '{table_name}' in database '{database}'.")
                    print("You can now view it in SSMS.")

                except Exception as e:
                    print("Failed to export DataFrame to SQL Server.")
                    print("Error details:", e)
                    sys.exit(1)