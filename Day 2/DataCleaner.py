# import required libraries
import pandas as pd
import numpy as np


#--------------------------
# CUSTOMERS FILE PROCESSING
#--------------------------

# load csv file (Customers)
df1 = pd.read_csv(r'C:\Users\Admin\Downloads\03_Library SystemCustomers.csv')

# Calculate completeness
cust_start_completeness = 100-(df1.isnull().mean() * 100)

# Count NaN values in each column (DEPRECATED IN EXECUTABLE FILE)
# nan_counts = df1.isna().sum()

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

# load csv file (Books)
df2 = pd.read_csv(r'C:\Users\Admin\Downloads\03_Library Systembook.csv')


# Calculate completeness
book_start_completeness = 100-(df2.isnull().mean() * 100)

# Count NaN values in each column
# nan_counts = df2.isna().sum()

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

import re

# Function to clean date strings
def clean_date_string(s):
    if pd.isna(s):
        return s
    # Ensure string type
    s = str(s)
    # Remove surrounding quotes and spaces
    s = s.strip().strip('"').strip("'")
    return s

# Apply cleaning
df2['Book checkout'] = df2['Book checkout'].apply(clean_date_string)

# Convert to datetime
df2['Book checkout'] = pd.to_datetime(df2['Book checkout'], format='%d/%m/%Y', errors='coerce')

# Convert Return date column to datetime
df2['Book Returned'] = pd.to_datetime(df2['Book Returned'], format='%d/%m/%Y', errors='coerce')

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

    # Use absolute values if requested
    if absolute:
        diff = diff.abs()

    df[output_col] = diff
    return df


# Use add_days_difference_column function on Books df
if __name__ == "__main__":
    df2 = add_days_difference_column(df2, "Book checkout", "Book Returned", "days_between", absolute=True)

# Convert ID columns to integers instead of floats
import math
df2['Id'] = [int(x) for x in df2['Id']]
df2['Customer ID'] = [int(x) for x in df2['Customer ID']]

# Calculate final completeness
book_end_completeness = 100-(df2.isnull().mean() * 100)

#--------------------------
# OUTPUT TO CSV FILES
#--------------------------

df1.to_csv(r'C:\Users\Admin\Desktop\DE5M5\CustomersCleaned.csv', index=False)
df2.to_csv(r'C:\Users\Admin\Desktop\DE5M5\BooksCleaned.csv', index=False)

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

from sqlalchemy import create_engine
import urllib
import sys

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
    print("❌ Failed to export DataFrame to SQL Server.")
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
    print("❌ Failed to export DataFrame to SQL Server.")
    print("Error details:", e)
    sys.exit(1)