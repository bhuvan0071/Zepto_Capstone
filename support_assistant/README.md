# Zepto policy support assistant

From this folder, run `pip install -r requirements.txt`, then `uvicorn main:app --reload --port 7860`. Default `MOCK_LLM=1` (also used when unset) makes no LLM calls and sets mock confidence to a fixed `1.0`. The app embeds the eight policy documents locally, persists vectors in `chroma_db/zepto_policy_chunks`, and runs a three-node LangGraph workflow. Optional real generation uses `MOCK_LLM=0` and `GROQ_API_KEY`; never commit secrets.

The captured raw responses for one policy query and one general query are in [example_responses.json](example_responses.json).

Build and run Docker from this folder with `docker build -t zepto-assistant .` and `docker run --rm -p 7860:7860 zepto-assistant`. From the repository root, use `docker build -f support_assistant/Dockerfile -t zepto-assistant support_assistant`.