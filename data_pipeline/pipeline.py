"""Scrape Books to Scrape, normalize the records, and demonstrate SQL/pandas."""
from __future__ import annotations

import re
import sqlite3
import time
import io
import sys
from contextlib import redirect_stdout
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/"
RATE = 105.50
ROOT = Path(__file__).resolve().parent
DB = ROOT / "books.sqlite"
RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
HEADERS = {"User-Agent": "ZeptoCapstoneEducationalScraper/1.0"}


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def scrape() -> pd.DataFrame:
    """Fetch the first five catalogue pages (normally 100 books)."""
    links = []
    for page in range(1, 6):
        url = BASE if page == 1 else f"{BASE}catalogue/page-{page}.html"
        soup = get_soup(url)
        for card in soup.select("article.product_pod"):
            href = card.select_one("h3 a")["href"]
            links.append(requests.compat.urljoin(url, href))

    def parse_book(url):
        detail = get_soup(url)
        category = detail.select("ul.breadcrumb li a")[-1].get_text(strip=True)
        rating_node = detail.select_one("p.star-rating")
        rating_text = next((c for c in rating_node.get("class", []) if c != "star-rating"), "")
        return {"title": detail.select_one("div.product_main h1").get_text(strip=True),
                "price": detail.select_one("p.price_color").get_text(strip=True), "star_rating": rating_text,
                "availability": detail.select_one("p.instock.availability").get_text(" ", strip=True),
                "category": category}
    with ThreadPoolExecutor(max_workers=10) as pool:
        rows = list(pool.map(parse_book, links))
    return pd.DataFrame(rows)


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df["price_gbp"] = pd.to_numeric(df["price"].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
    df["rating"] = df["star_rating"].map(RATING).astype("float")
    df["in_stock"] = df["availability"].astype(str).str.contains("In stock", case=False, na=False).astype("boolean")
    # Unparseable numeric fields use the observed median; categorical identity and stock failures are dropped.
    for col in ("price_gbp", "rating"):
        df[col] = df[col].fillna(df[col].median())
    df = df.dropna(subset=["title", "category", "in_stock"]).copy()
    df["rating"] = df["rating"].round().clip(1, 5).astype("int64")
    df["price_inr"] = (df["price_gbp"] * RATE).round(2)
    df["in_stock"] = df["in_stock"].astype(bool)
    return df[["title", "price_gbp", "price_inr", "rating", "in_stock", "category"]]


QUERIES = {
    "where_order_limit": "SELECT title, price_gbp, rating FROM books WHERE in_stock = 1 ORDER BY rating DESC, price_gbp DESC LIMIT 10",
    "distinct_categories": "SELECT DISTINCT category_name FROM categories ORDER BY category_name",
    "rating_between": "SELECT title, rating FROM books WHERE rating BETWEEN 4 AND 5 ORDER BY rating DESC, title LIMIT 10",
    "category_in": "SELECT title, category_name FROM books JOIN categories USING(category_id) WHERE category_name IN ('Travel', 'Mystery', 'Historical Fiction') ORDER BY category_name, title LIMIT 15",
    "join_top_books": "SELECT c.category_name, b.title, b.rating, b.price_gbp FROM books b JOIN categories c USING(category_id) ORDER BY c.category_name, b.rating DESC, b.price_gbp DESC, b.title LIMIT 20",
}


def load_database(df: pd.DataFrame) -> None:
    with sqlite3.connect(DB) as con:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript("DROP TABLE IF EXISTS books; DROP TABLE IF EXISTS categories; CREATE TABLE categories(category_id INTEGER PRIMARY KEY, category_name TEXT UNIQUE NOT NULL); CREATE TABLE books(book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, price_gbp REAL NOT NULL, price_inr REAL NOT NULL, rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5), in_stock INTEGER NOT NULL CHECK(in_stock IN (0,1)), category_id INTEGER NOT NULL REFERENCES categories(category_id));")
        cats = sorted(df.category.unique())
        con.executemany("INSERT INTO categories(category_name) VALUES (?)", [(x,) for x in cats])
        ids = dict(con.execute("SELECT category_name, category_id FROM categories").fetchall())
        con.executemany("INSERT INTO books(title,price_gbp,price_inr,rating,in_stock,category_id) VALUES (?,?,?,?,?,?)",
                        [(r.title, float(r.price_gbp), float(r.price_inr), int(r.rating), int(r.in_stock), ids[r.category]) for r in df.itertuples()])


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raw = scrape()
    df = clean(raw)
    if len(df) < 60 or df.category.nunique() < 3:
        raise RuntimeError(f"Expected >=60 books and >=3 categories; got {len(df)} rows, {df.category.nunique()} categories")
    df.to_csv(ROOT / "books_clean.csv", index=False)
    load_database(df)
    output = [f"Rows: {len(df)} | categories: {df.category.nunique()} | GBP→INR rate: {RATE:.2f}"]
    results = {}
    with sqlite3.connect(DB) as con:
        for name, sql in QUERIES.items():
            res = pd.read_sql_query(sql, con)
            results[name] = res
            output += [f"\n## {name}\nSQL: {sql}\n{res.to_string(index=False)}"]
        category_frame = pd.DataFrame({"category_id": range(1, len(df.category.unique()) + 1), "category": sorted(df.category.unique())})
        book_frame = df.merge(category_frame, on="category", how="left")
        pandas_join = book_frame.sort_values(["category", "rating", "price_gbp", "title"], ascending=[True, False, False, True]).copy()
        sql_join = results["join_top_books"].rename(columns={"category_name": "category"})
        # Reproduce the SQL join directly from in-memory books and category DataFrames.
        pandas_join = book_frame.sort_values(["category", "rating", "price_gbp", "title"], ascending=[True, False, False, True]).head(20)
        output += ["\n## Join equivalence (SQL / pandas merge)", f"Equivalent: {sql_join.equals(pandas_join[['category','title','rating','price_gbp']].reset_index(drop=True))}",
                   "SQL result:\n" + sql_join.to_string(index=False), "pandas merge result:\n" + pandas_join[["category","title","rating","price_gbp"]].to_string(index=False)]
    (ROOT / "query_results.md").write_text("\n\n".join(output), encoding="utf-8")
    print("\n\n".join(output))


if __name__ == "__main__":
    main()
