# Data pipeline

Run `python pipeline.py` after `pip install -r requirements.txt`. It scrapes the first five catalogue pages, giving 100 books, cleans values and computes INR at the fixed assignment rate 105.50 per GBP. `query_results.md` records all query strings, outputs, and the SQL/pandas join check. Parse failures in numeric values use median imputation; missing identity/category/availability is dropped because it cannot be reliably reconstructed.

Generated run: 100 books across 29 categories. All five SQL examples executed, and the SQL join matched the equivalent in-memory `pd.merge` result.
