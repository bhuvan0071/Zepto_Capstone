# Zepto Data & AI Platform — Capstone

One repository with three connected modules. Python 3.11+ is recommended. Install dependencies per module from that module's `requirements.txt`. The support assistant downloads `all-MiniLM-L6-v2` on first run; the scraper and Seaborn loader also need network access once. The required LLM path is fully offline: `MOCK_LLM` defaults to `1`.

## Run

From this repository root:

```powershell
python -m pip install -r data_pipeline/requirements.txt
python data_pipeline/pipeline.py
python -m pip install -r analytics/requirements.txt
python analytics/analysis.py
python -m pip install -r support_assistant/requirements.txt
cd support_assistant
uvicorn main:app --reload --port 7860
```

The data pipeline fetches the first five catalogue pages and writes `data_pipeline/books_clean.csv`, `books.sqlite`, and `query_results.md`. Its fixed conversion rate is **1 GBP = 105.50 INR**. Numeric parse failures are median-imputed; unusable title/category/stock records are dropped. The SQLite schema separates categories and books by a foreign key.

The analytics script calls `sns.load_dataset('titanic')` once and immediately writes `analytics/titanic.csv` as the offline fallback. It generates figures, a detailed interpretation/metrics report, and `best_pipeline.joblib`. The EDA missing-data policy is <5% drop affected rows, 5–30% median/mode imputation, and >30% an explicit `Missing` category. For modeling, preprocessing is fit on training partitions through scikit-learn pipelines; SMOTE is applied only after training-fold transformation. Run the script again to regenerate all outputs. `titanic.csv` can be read directly with pandas when offline.

The assistant indexes the eight text documents in local ChromaDB collection `zepto_policy_chunks`, embedding them with sentence-transformers. `initialize_index()` performs document loading/chunking/embedding. LangGraph routes through `classify_intent` to either `retrieve_and_answer` (real vector retrieval, top 3) or `direct_answer`. In default mock mode, intent uses the required keyword heuristic, policy replies quote the top retrieved document, and general replies use a fixed response. With `MOCK_LLM=0`, intent and response generation use the optional Groq-compatible endpoint and `GROQ_API_KEY`; retrieval remains active for policy questions. The prompt includes role, context, task, format, length, a negative grounding constraint, and a few-shot example. FastAPI validates every response as `{answer, sources, confidence}`.

## Check the API

```powershell
curl.exe -X POST http://localhost:7860/ask -H "Content-Type: application/json" -d "{\"query\":\"What is the delivery fee?\"}"
curl.exe -X POST http://localhost:7860/ask -H "Content-Type: application/json" -d "{\"query\":\"Tell me a joke\"}"
```

Mock mode policy example (sources/confidence are deterministic from retrieval; exact confidence can vary slightly by embedding library version):

```json
{"answer":"Based on the retrieved context: Delivery Policy: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order vol","sources":["doc_01","doc_05","doc_02"],"confidence":0.5226026177406311}
```

Mock mode general example:

```json
{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}
```

## Docker

From the repository root, build with `docker build -f support_assistant/Dockerfile -t zepto-assistant .` and run with `docker run --rm -p 7860:7860 zepto-assistant`. The model is downloaded on first startup. The container serves `POST /ask` on port 7860.

## Git workflow

Before publication, create a feature branch, make at least two commits on it, and merge it into `main`. This checkout may not have a Git remote configured; push the finished single repository publicly and submit that one URL.
