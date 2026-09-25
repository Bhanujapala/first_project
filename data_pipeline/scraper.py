import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://books.toscrape.com/"
MAX_PAGES = 5

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = DATA_DIR / "raw_books.csv"


# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    )
})


# ============================================================
# TEXT ENCODING
# ============================================================

def fix_text_encoding(text):

    if text is None:
        return None

    text = str(text).strip()

    replacements = {
        "Â£": "£",
        "â€™": "'",
        "â€˜": "'",
        "â€œ": '"',
        "â€\x9d": '"',
        "â€“": "–",
        "â€”": "—",
        "â€¦": "...",
        "Â": "",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text.strip()


# ============================================================
# SCRAPE ONE BOOK LISTING PAGE
# ============================================================

def scrape_listing_page(page_url):

    print("=" * 60)
    print(f"Scraping page {page_url}")
    print("=" * 60)

    try:

        response = session.get(
            page_url,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

    except requests.RequestException as e:

        print(f"Page request failed: {page_url}")
        print(f"Error: {e}")

        return []

    books = []

    book_containers = soup.select(
        "article.product_pod"
    )

    print(
        f"Books found: {len(book_containers)}"
    )

    for index, book in enumerate(
        book_containers,
        start=1
    ):

        try:

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            title_tag = book.select_one(
                "h3 a"
            )

            if title_tag:

                title = title_tag.get(
                    "title",
                    ""
                )

                title = fix_text_encoding(
                    title
                )

            else:

                title = None

            # ------------------------------------------------
            # BOOK URL
            # ------------------------------------------------

            if (
                title_tag
                and title_tag.get("href")
            ):

                book_url = urljoin(
                    page_url,
                    title_tag["href"]
                )

            else:

                book_url = None

            # ------------------------------------------------
            # PRICE
            # ------------------------------------------------

            price_tag = book.select_one(
                "p.price_color"
            )

            if price_tag:

                price = price_tag.get_text(
                    strip=True
                )

                price = fix_text_encoding(
                    price
                )

            else:

                price = None

            # ------------------------------------------------
            # STAR RATING
            # ------------------------------------------------

            rating_tag = book.select_one(
                "p.star-rating"
            )

            if rating_tag:

                classes = rating_tag.get(
                    "class",
                    []
                )

                rating_words = {
                    "One",
                    "Two",
                    "Three",
                    "Four",
                    "Five"
                }

                star_rating = next(
                    (
                        item
                        for item in classes
                        if item in rating_words
                    ),
                    None
                )

            else:

                star_rating = None

            # ------------------------------------------------
            # AVAILABILITY
            # ------------------------------------------------

            availability_tag = book.select_one(
                "p.instock.availability"
            )

            if availability_tag:

                availability = (
                    availability_tag.get_text(
                        " ",
                        strip=True
                    )
                )

            else:

                availability = None

            # ------------------------------------------------
            # SAVE RECORD
            # ------------------------------------------------

            books.append({
                "title": title,
                "book_url": book_url,
                "price": price,
                "star_rating": star_rating,
                "availability": availability,
                "category": None
            })

            print(
                f"  Book {index}: {title}"
            )

        except Exception as e:

            print(
                f"  Skipping book {index}: {e}"
            )

    print()

    return books


# ============================================================
# DISCOVER CATEGORY PAGES
# ============================================================

def get_category_pages():

    print("=" * 60)
    print("DISCOVERING CATEGORY PAGES")
    print("=" * 60)

    try:

        response = session.get(
            BASE_URL,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

    except requests.RequestException as e:

        print(
            f"Could not load home page: {e}"
        )

        return {}

    category_pages = {}

    # The website has a category sidebar.
    category_links = soup.select(
        "div.side_categories ul li ul li a"
    )

    for link in category_links:

        category_name = link.get_text(
            " ",
            strip=True
        )

        category_url = link.get(
            "href"
        )

        if not category_url:
            continue

        category_url = urljoin(
            BASE_URL,
            category_url
        )

        category_name = fix_text_encoding(
            category_name
        )

        category_pages[
            category_name
        ] = category_url

    print(
        f"Category pages found: "
        f"{len(category_pages)}"
    )

    for category, url in category_pages.items():

        print(
            f"  {category}: {url}"
        )

    print()

    return category_pages


# ============================================================
# BUILD BOOK -> CATEGORY MAPPING
# ============================================================

def build_category_mapping(category_pages):

    print("=" * 60)
    print("BUILDING BOOK -> CATEGORY MAPPING")
    print("=" * 60)

    book_category_map = {}

    for category, category_url in category_pages.items():

        print(
            f"Scraping category: {category}"
        )

        current_url = category_url

        while current_url:

            try:

                response = session.get(
                    current_url,
                    timeout=15
                )

                response.raise_for_status()

                soup = BeautifulSoup(
                    response.content,
                    "html.parser"
                )

            except requests.RequestException as e:

                print(
                    f"  Failed: {current_url}"
                )

                print(
                    f"  Error: {e}"
                )

                break

            book_containers = soup.select(
                "article.product_pod"
            )

            for book in book_containers:

                title_tag = book.select_one(
                    "h3 a"
                )

                if not title_tag:
                    continue

                href = title_tag.get(
                    "href"
                )

                if not href:
                    continue

                book_url = urljoin(
                    current_url,
                    href
                )

                book_category_map[
                    book_url
                ] = category

            # ------------------------------------------------
            # NEXT PAGE
            # ------------------------------------------------

            next_link = soup.select_one(
                "li.next a"
            )

            if next_link:

                next_href = next_link.get(
                    "href"
                )

                if next_href:

                    current_url = urljoin(
                        current_url,
                        next_href
                    )

                else:

                    current_url = None

            else:

                current_url = None

    print(
        f"\nBook-category mappings created: "
        f"{len(book_category_map)}"
    )

    print()

    return book_category_map


# ============================================================
# ASSIGN CATEGORIES TO BOOKS
# ============================================================

def assign_categories(
    books,
    book_category_map
):

    print("=" * 60)
    print("ASSIGNING CATEGORIES")
    print("=" * 60)

    missing_categories = 0

    for book in books:

        book_url = book.get(
            "book_url"
        )

        category = book_category_map.get(
            book_url
        )

        book["category"] = category

        if category is None:

            missing_categories += 1

            print(
                f"Category not found: "
                f"{book['title']}"
            )

    print(
        f"\nMissing categories: "
        f"{missing_categories}"
    )

    return books


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # STEP 1: SCRAPE FIRST 5 PAGES
    # ========================================================

    all_books = []

    for page_number in range(
        1,
        MAX_PAGES + 1
    ):

        if page_number == 1:

            page_url = BASE_URL

        else:

            page_url = urljoin(
                BASE_URL,
                f"catalogue/page-{page_number}.html"
            )

        books = scrape_listing_page(
            page_url
        )

        all_books.extend(
            books
        )

    # ========================================================
    # STEP 2: DISCOVER CATEGORIES
    # ========================================================

    category_pages = get_category_pages()

    # ========================================================
    # STEP 3: BUILD BOOK/CATEGORY MAPPING
    # ========================================================

    book_category_map = (
        build_category_mapping(
            category_pages
        )
    )

    # ========================================================
    # STEP 4: ASSIGN CATEGORIES
    # ========================================================

    all_books = assign_categories(
        all_books,
        book_category_map
    )

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        all_books
    )

    # Remove helper column before saving
    df = df[
        [
            "title",
            "price",
            "star_rating",
            "availability",
            "category"
        ]
    ]

    # ========================================================
    # SAVE CSV
    # ========================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("=" * 60)
    print("SCRAPING COMPLETED")
    print("=" * 60)

    print(
        f"Total books scraped: {len(df)}"
    )

    print(
        f"Total categories: "
        f"{df['category'].nunique()}"
    )

    # ========================================================
    # CATEGORY COUNTS
    # ========================================================

    print("\nCategory counts:")

    print(
        df["category"].value_counts(
            dropna=False
        )
    )

    # ========================================================
    # MISSING VALUES
    # ========================================================

    print("\nMissing values:")

    print(
        df.isnull().sum()
    )

    # ========================================================
    # FIRST 5 RECORDS
    # ========================================================

    print("\nFirst 5 records:")

    print(
        df.head().to_string(
            index=False
        )
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    print(
        f"\nRaw data saved to:"
    )

    print(
        OUTPUT_FILE
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()