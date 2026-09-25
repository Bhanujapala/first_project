import sqlite3
import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "cleaned_books.csv"
DB_FILE = DATA_DIR / "books.db"


# ---------------------------------------------------------
# CREATE DATABASE
# ---------------------------------------------------------

def create_database():

    # Read cleaned data
    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    print("=" * 60)
    print("CREATING SQLITE DATABASE")
    print("=" * 60)

    print(f"\nCleaned rows loaded: {len(df)}")

    # Connect to SQLite
    connection = sqlite3.connect(DB_FILE)

    # Enable foreign keys
    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    # -----------------------------------------------------
    # DROP OLD TABLES
    # -----------------------------------------------------

    cursor.execute("DROP TABLE IF EXISTS books")
    cursor.execute("DROP TABLE IF EXISTS categories")

    # -----------------------------------------------------
    # CREATE CATEGORIES TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL
        )
    """)

    # -----------------------------------------------------
    # CREATE BOOKS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL,
            in_stock INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        )
    """)

    # -----------------------------------------------------
    # INSERT CATEGORIES
    # -----------------------------------------------------

    categories = (
        df["category"]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    cursor.executemany(
        """
        INSERT INTO categories (category_name)
        VALUES (?)
        """,
        [(category,) for category in categories]
    )

    # -----------------------------------------------------
    # CREATE CATEGORY → ID MAPPING
    # -----------------------------------------------------

    cursor.execute("""
        SELECT category_id, category_name
        FROM categories
    """)

    category_map = {
        category_name: category_id
        for category_id, category_name in cursor.fetchall()
    }

    # -----------------------------------------------------
    # INSERT BOOKS
    # -----------------------------------------------------

    book_records = []

    for _, row in df.iterrows():

        category_id = category_map[row["category"]]

        book_records.append((
            row["title"],
            float(row["price_gbp"]),
            float(row["price_inr"]),
            int(row["rating"]),
            int(bool(row["in_stock"])),
            category_id
        ))

    cursor.executemany(
        """
        INSERT INTO books (
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        book_records
    )

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    connection.commit()

    # -----------------------------------------------------
    # VERIFY DATABASE
    # -----------------------------------------------------

    cursor.execute("SELECT COUNT(*) FROM books")
    book_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM categories")
    category_count = cursor.fetchone()[0]

    print(f"\nBooks inserted: {book_count}")
    print(f"Categories inserted: {category_count}")

    print("\nDatabase tables:")

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)

    for table in cursor.fetchall():
        print(f"  - {table[0]}")

    connection.close()

    print("\nDatabase saved to:")
    print(DB_FILE)

    print("\n" + "=" * 60)
    print("DATABASE CREATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    create_database()