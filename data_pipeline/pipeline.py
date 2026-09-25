import subprocess
import sys
from pathlib import Path


# Get the folder where this pipeline.py file is located
BASE_DIR = Path(__file__).resolve().parent


def run_script(script_name):
    """Run another Python script from the data_pipeline folder."""

    script_path = BASE_DIR / script_name

    print("\n" + "=" * 60)
    print(f"RUNNING: {script_name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        check=False
    )

    if result.returncode != 0:
        print(f"\nERROR: {script_name} failed.")
        sys.exit(result.returncode)

    print(f"\nCOMPLETED: {script_name}")


def main():
    print("=" * 60)
    print("DATA PIPELINE - END TO END EXECUTION")
    print("=" * 60)

    # Step 1: Scrape books
    run_script("scraper.py")

    # Step 2: Clean data
    run_script("cleaner.py")

    # Step 3: Create SQLite database
    run_script("database.py")

    # Step 4: Run SQL and Pandas queries
    run_script("queries.py")

    print("\n" + "=" * 60)
    print("DATA PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print("\nGenerated files:")
    print("  - data/raw_books.csv")
    print("  - data/cleaned_books.csv")
    print("  - data/books.db")
    print("  - data/query_results/queries.sql")


if __name__ == "__main__":
    main()