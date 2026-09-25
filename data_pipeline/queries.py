import sqlite3
import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DB_FILE = DATA_DIR / "books.db"
OUTPUT_DIR = DATA_DIR / "query_results"

OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# SQL QUERIES
# ---------------------------------------------------------

queries = {

    # Query 1:
    # SELECT + WHERE
    "query_1_select_where": """
        SELECT title, price_gbp, rating
        FROM books
        WHERE rating >= 4
        ORDER BY rating DESC
    """,

    # Query 2:
    # ORDER BY + LIMIT
    "query_2_order_limit": """
        SELECT title, price_gbp, rating
        FROM books
        ORDER BY price_gbp DESC
        LIMIT 10
    """,

    # Query 3:
    # DISTINCT
    "query_3_distinct": """
        SELECT DISTINCT category_name
        FROM categories
        ORDER BY category_name
    """,

    # Query 4:
    # BETWEEN
    "query_4_between": """
        SELECT title, price_gbp, rating
        FROM books
        WHERE price_gbp BETWEEN 10 AND 30
        ORDER BY price_gbp
    """,

    # Query 5:
    # JOIN
    "query_5_join": """
        SELECT
            b.title,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock,
            c.category_name
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY b.rating DESC, c.category_name, b.title
        LIMIT 10
    """
}


# ---------------------------------------------------------
# SAVE SQL QUERIES
# ---------------------------------------------------------

def save_sql_queries():

    sql_file = OUTPUT_DIR / "queries.sql"

    with open(sql_file, "w", encoding="utf-8") as file:

        for name, query in queries.items():

            file.write(f"-- {name}\n")
            file.write(query.strip())
            file.write("\n\n")

    print(f"SQL queries saved to:\n{sql_file}")


# ---------------------------------------------------------
# RUN SQL QUERIES
# ---------------------------------------------------------

def run_sql_queries(connection):

    print("\n" + "=" * 60)
    print("RUNNING SQL QUERIES")
    print("=" * 60)

    results = {}

    for name, query in queries.items():

        print("\n" + "-" * 60)
        print(name)
        print("-" * 60)

        df = pd.read_sql_query(
            query,
            connection
        )

        results[name] = df

        print(df.to_string(index=False))

        # Save output
        output_file = OUTPUT_DIR / f"{name}.csv"

        df.to_csv(
            output_file,
            index=False,
            encoding="utf-8-sig"
        )

    return results


# ---------------------------------------------------------
# READ RESULTS USING pd.read_sql()
# ---------------------------------------------------------

def demonstrate_read_sql(connection):

    print("\n" + "=" * 60)
    print("PANDAS pd.read_sql() RESULTS")
    print("=" * 60)

    query_1 = """
        SELECT title, price_gbp, rating
        FROM books
        WHERE rating >= 4
        ORDER BY rating DESC
        LIMIT 5
    """

    query_2 = """
        SELECT title, price_gbp, in_stock
        FROM books
        WHERE price_gbp BETWEEN 10 AND 30
        ORDER BY price_gbp
        LIMIT 5
    """

    result_1 = pd.read_sql(
        query_1,
        connection
    )

    result_2 = pd.read_sql(
        query_2,
        connection
    )

    print("\nResult 1:")
    print(result_1.to_string(index=False))

    print("\nResult 2:")
    print(result_2.to_string(index=False))

    return result_1, result_2


# ---------------------------------------------------------
# SQL JOIN VS PANDAS MERGE
# ---------------------------------------------------------

def compare_sql_join_and_pandas_merge(connection):

    print("\n" + "=" * 60)
    print("SQL JOIN VS PANDAS MERGE")
    print("=" * 60)

    # -----------------------------------------------------
    # SQL JOIN
    # -----------------------------------------------------

    sql_join = """
        SELECT
            b.title,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock,
            c.category_name
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY b.rating DESC, c.category_name, b.title
        LIMIT 10
    """

    sql_result = pd.read_sql(
        sql_join,
        connection
    )

    # -----------------------------------------------------
    # LOAD TABLES INTO DATAFRAMES
    # -----------------------------------------------------

    books_df = pd.read_sql(
        """
        SELECT
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        FROM books
        """,
        connection
    )

    categories_df = pd.read_sql(
        """
        SELECT
            category_id,
            category_name
        FROM categories
        """,
        connection
    )

    # -----------------------------------------------------
    # PANDAS MERGE
    # -----------------------------------------------------

    pandas_result = pd.merge(
        books_df,
        categories_df,
        on="category_id",
        how="inner"
    )

    pandas_result = pandas_result[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category_name"
        ]
    ]

    pandas_result = (
        pandas_result
        .sort_values(
            by=[
                "rating",
                "category_name",
                "title"
            ],
            ascending=[
                False,
                True,
                True
            ]
        )
        .head(10)
        .reset_index(drop=True)
    )

    sql_result = sql_result.reset_index(drop=True)

    # -----------------------------------------------------
    # DISPLAY SQL RESULT
    # -----------------------------------------------------

    print("\nSQL JOIN result:")
    print(sql_result.to_string(index=False))

    # -----------------------------------------------------
    # DISPLAY PANDAS MERGE RESULT
    # -----------------------------------------------------

    print("\nPandas merge result:")
    print(pandas_result.to_string(index=False))

    # -----------------------------------------------------
    # COMPARE
    # -----------------------------------------------------

    match = sql_result.equals(
        pandas_result
    )

    print("\nDo SQL JOIN and Pandas merge match?")
    print(match)

    return sql_result, pandas_result


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("SQL AND PANDAS QUERY DEMONSTRATION")
    print("=" * 60)

    # Connect to database
    connection = sqlite3.connect(DB_FILE)

    try:

        # Save SQL queries
        save_sql_queries()

        # Run all 5 SQL queries
        run_sql_queries(connection)

        # Demonstrate pd.read_sql()
        demonstrate_read_sql(connection)

        # Compare JOIN and merge
        compare_sql_join_and_pandas_merge(
            connection
        )

    finally:

        connection.close()

    print("\n" + "=" * 60)
    print("QUERY PROCESS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()