from pathlib import Path
import sqlite3

# Define the database file path
db_path = Path("example.db")

#----------------------------------
# SET UP DATABASE & TABLE IN SQLITE
#----------------------------------
try:
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