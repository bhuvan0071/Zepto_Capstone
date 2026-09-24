# Zepto policy support assistant

Run `pip install -r requirements.txt`, then `uvicorn main:app --reload --port 7860` from this folder. Default `MOCK_LLM=1` (also used when unset) is deterministic and does not call an LLM. The app embeds the exact eight policy documents locally, persists vectors in `chroma_db/zepto_policy_chunks`, then runs a three-node LangGraph workflow. Optional real generation uses `MOCK_LLM=0` and `GROQ_API_KEY`; never commit secrets. Build Docker from repository root: `docker build -f support_assistant/Dockerfile -t zepto-assistant .`.


The two raw responses captured from local POST /ask calls are saved in xample_responses.json.
