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
from datetime import datetime

#--------------------------
# DEFINE FUNCTIONS
#--------------------------

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
        rows_removed = len(negative_df)

        # Log counts
        print(f"Cleaned data kept in DataFrame: {len(positive_df)}")
        print(f"Removed negative records saved to: {removed_file} ({len(negative_df)} records removed)")

        if return_data:
            return positive_df, rows_removed, negative_df

    except Exception as e:
        print(f"Error: {e}")


#--------------------------
# CUSTOMERS FILE PROCESSING
#--------------------------

# Define fileName_1
FileName_1 = '03_Library SystemCustomers.csv'

# load csv file (Customers)
df1 = pd.read_csv(rf"{FileName_1}")

# Calculate completeness
cust_start_completeness = 100-(df1.isnull().mean() * 100)

# Remove NaN values
df1 = df1.dropna(how='all')

# Check for duplicate IDs
if df1['Customer ID'].duplicated().any():
    print(f"Check Failed: Duplicate ID found")
else:
    print(f"Check Passed: No Duplicate ID found.")

# Check for duplicate Names
if df1['Customer Name'].duplicated().any():
    print(f"Check Failed: Duplicate Name found")
else:
    print(f"Check Passed: No Duplicate Name found.")

# Calculate completeness
cust_end_completeness = 100-(df1.isnull().mean() * 100)


#--------------------------
# BOOKS FILE PROCESSING
#--------------------------

# Define fileName_2
FileName_2 = '03_Library Systembook.csv'

# load csv file (Books)
df2 = pd.read_csv(rf"{FileName_2}")

# Calculate completeness
book_start_completeness = 100-(df2.isnull().mean() * 100)

# Remove NaN values
df2 = df2.dropna()

# Check for duplicate IDs
if df2['Id'].duplicated().any():
    print(f"Check Failed: Duplicate ID found")
else:
    print(f"Check Passed: No Duplicate ID found.")

# Capitalize each word of the book names for every row
df2['Books'] = df2['Books'].str.title()

# Remove any leading or trailing spaces from book names
df2 = df2.map(lambda x: x.strip() if isinstance(x, str) else x)

# Apply cleaning
df2['Book checkout'] = df2['Book checkout'].apply(clean_date_string)

# Convert to datetime
df2['Book checkout'] = pd.to_datetime(df2['Book checkout'], format='%d/%m/%Y', errors='coerce')

# Convert Return date column to datetime
df2['Book Returned'] = pd.to_datetime(df2['Book Returned'], format='%d/%m/%Y', errors='coerce')

# Use add_days_difference_column function on Books df:
df2 = add_days_difference_column(df2, "Book checkout", "Book Returned", "days_between", absolute=True)

# Convert ID columns to integers instead of floats
df2['Id'] = [int(x) for x in df2['Id']]
df2['Customer ID'] = [int(x) for x in df2['Customer ID']]

# Run quarantine function on Books df
df2, rows_removed, var3 = quarantine_dateGapIssues(
    df2,
    column_name = "days_between",
    removed_file = "removed_bookRecords.csv"
)

# Calculate final completeness
book_end_completeness = 100-(df2.isnull().mean() * 100)

#--------------------------
# OUTPUT TO CSV FILES
#--------------------------

# df1.to_csv(r'cleanedFiles\CustomersCleaned.csv', index=False)
# df2.to_csv(r'cleanedFiles\BooksCleaned.csv', index=False)

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
# CREATE METRICS DATAFRAME
#--------------------------
# Create a DataFrame as a dictionary
metrics_df = pd.DataFrame({
    'TimeStamp': datetime.now(),
    'FileName_1': FileName_1,
    'FileName_2': FileName_2,
    'RowsRemoved': rows_removed,
    'CustStartCompleteness' : cust_start_completeness,
    'CustEndCompleteness' : cust_end_completeness,
    'BooksStartCompleteness' : book_start_completeness,
    'BooksEndCompleteness' : book_end_completeness
})


#--------------------------
# OUTPUT TO SQL DATABASE
#--------------------------

# SQL Server connection details
server = r'STUDENT01'      
database = 'libraryProject' 

# Define table for Customers data
table_name = 'ProcessingLog'

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
    metrics_df.to_sql(
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
        if_exists='append',  # 'replace' overwrites, 'append' adds rows
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