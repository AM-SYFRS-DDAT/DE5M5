#----------------------------------
# *** THIS FILE IS INCOMPLETE ***
#----------------------------------

from pathlib import Path
import sqlite3
import csv
import requests
import io

# Define the database file path
db_path = Path("example.db")

# Define csv file url
csv_url = "https://www.data.gov.uk/dataset/56a898b9-8a3f-4c5f-8932-a03d958e0a43/ons-postcode-directory-november-2025-for-the-uk-hosted-table/datafile/8b41a98e-573d-4697-8c22-20f6da276307/preview"

#----------------------------------
# DOWNLOAD CSV FILE AND CONVERT
#----------------------------------

try:
    # Download csv file
    response = requests.get(csv_url, timeout=10)
    response.raise_for_status()  # Raise error if download failed

    # Convert the CSV text into a file-like object for csv.DictReader
    csv_file_like = io.StringIO(response.text)

#----------------------------------
# SET UP DATABASE & TABLE IN SQLITE
#----------------------------------

    # Connect to the SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT NOT NULL,
            year_published INTEGER CHECK(year_published >= 1400)
        )
    """)

#----------------------------------
# ADD DATA TO BOOKS TABLE
#----------------------------------

    # Define data
    books = [
        ("Little Women", 1868),
        ("1984", 1949),
        ("Canterbury Tales", 1400)
    ]

    # Insert data
    cursor.executemany("INSERT INTO books (book, year_published) VALUES (?, ?)", books)

    # Commit changes
    conn.commit()
    print(f"Data inserted successfully into {db_path.resolve()}")

#----------------------------------
# READ BACK THE DATA (BOOKS TABLE)
#----------------------------------

    # Read back the data and print it to check insertion worked 
    cursor.execute("SELECT id, book, year_published FROM books")
    rows = cursor.fetchall()

    print("\nCurrent books owned:")
    for row in rows:
        print(f"ID: {row[0]}, Book: {row[1]}, Year Published: {row[2]}")

#----------------------------------
# HANDLE EXCEPTIONS
#----------------------------------

# Print an error message if something went wrong
except sqlite3.Error as e:
    print(f"SQLite error: {e}")

#----------------------------------
# CLOSE CONNECTION
#----------------------------------

finally:
    if conn:
        conn.close()