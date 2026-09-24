"""Offline-first policy assistant with sentence-transformers, Chroma, LangGraph and FastAPI."""
import os, json
from pathlib import Path
from typing import TypedDict, List
ROOT=Path(__file__).resolve().parent
os.environ.setdefault("HF_HOME",str(ROOT/"model_cache"))
import chromadb
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, START, END
from fastapi import FastAPI
from pydantic import BaseModel, Field

DOCS=ROOT/"docs"; DB=ROOT/"chroma_db"; COLLECTION="zepto_policy_chunks"
KEYWORDS=("delivery","return","refund","membership","tracking","cancel","gift card","support hours")
class AskRequest(BaseModel): query:str
class AskResponse(BaseModel):
    answer:str
    sources:List[str]
    confidence:float=Field(ge=0,le=1)
class State(TypedDict,total=False):
    query:str; intent:str; answer:str; sources:List[str]; confidence:float; context:List[str]; ids:List[str]

PROMPT_TEMPLATE="""ROLE: Zepto policy support assistant.
CONTEXT: Use only these policy excerpts: {context}
TASK: Answer the question accurately and cite relevant source IDs.
FORMAT: Return JSON with answer (string), sources (array of IDs), confidence (0 to 1).
LENGTH: At most 3 concise sentences.
NEGATIVE CONSTRAINT: Do not answer using information not present in the provided context. Say when unsupported.
FEW-SHOT EXAMPLE:
Question: When can I cancel?
Context: [doc_05] Orders can be cancelled free before status changes to Packed.
JSON: {{"answer":"You can cancel free of cost before the order is Packed.","sources":["doc_05"],"confidence":0.9}}
Customer question: {query}
Return JSON only."""
_client=_collection=_model=None

def initialize_index():
    global _client,_collection,_model
    _model=SentenceTransformer("all-MiniLM-L6-v2")
    _client=chromadb.PersistentClient(path=str(DB))
    _collection=_client.get_or_create_collection(COLLECTION,metadata={"hnsw:space":"cosine"})
    if _collection.count()==0:
        docs=[]; ids=[]; metas=[]
        for p in sorted(DOCS.glob("doc_*.txt")):
            ids.append(p.stem); docs.append(p.read_text(encoding="utf-8").strip()); metas.append({"document_id":p.stem})
        _collection.add(ids=ids,documents=docs,metadatas=metas,embeddings=_model.encode(docs,normalize_embeddings=True).tolist())

def mock_enabled(): return os.getenv("MOCK_LLM","1")!="0"

def llm_json(prompt):
    """Optional Groq endpoint with schema correction retry, maximum three attempts."""
    import requests
    key=os.getenv("GROQ_API_KEY")
    if not key: raise RuntimeError("Set GROQ_API_KEY when MOCK_LLM=0")
    error=None
    for attempt in range(3):
        extra="" if attempt==0 else " Previous output was invalid; correct it to valid JSON with answer, sources, confidence."
        response=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {key}"},
          json={"model":os.getenv("GROQ_MODEL","llama-3.1-8b-instant"),"messages":[{"role":"user","content":prompt+extra}],"temperature":0},timeout=30)
        response.raise_for_status(); raw=response.json()["choices"][0]["message"]["content"]
        try: return AskResponse.model_validate_json(raw).model_dump()
        except Exception as exc: error=exc
    raise ValueError(f"Schema validation failed after 3 attempts: {error}")

def classify_intent(state:State)->State:
    q=state["query"]
    if mock_enabled(): intent="policy_question" if any(k in q.lower() for k in KEYWORDS) else "general_question"
    else:
        result=llm_json(f"Classify as policy_question or general_question. Put the label in answer, return JSON. Query: {q}")
        intent="policy_question" if "policy_question" in result["answer"].lower() else "general_question"
    return {"intent":intent}

def retrieve_and_answer(state:State)->State:
    q=state["query"]; vec=_model.encode([q],normalize_embeddings=True).tolist()
    result=_collection.query(query_embeddings=vec,n_results=3,include=["documents","metadatas","distances"])
    docs=result["documents"][0]; ids=[m["document_id"] for m in result["metadatas"][0]]
    if mock_enabled():
        answer="Based on the retrieved context: "+docs[0][:200]
        return {"answer":answer,"sources":ids,"confidence":1.0,"context":docs,"ids":ids}
    prompt=PROMPT_TEMPLATE.format(context="\n".join(f"[{i}] {d}" for i,d in zip(ids,docs)),query=q)
    try: out=llm_json(prompt)
    except Exception as exc: out={"answer":f"ERROR: {exc}","sources":ids,"confidence":0.0}
    out["sources"]=ids
    return {**out,"context":docs,"ids":ids}

def direct_answer(state:State)->State:
    if mock_enabled(): return {"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}
    try:
        out=llm_json(PROMPT_TEMPLATE.format(context="No policy context was retrieved.",query=state["query"])); out["sources"]=[]; return out
    except Exception as exc: return {"answer":f"ERROR: {exc}","sources":[],"confidence":0.0}

def route(state:State): return "retrieve_and_answer" if state["intent"]=="policy_question" else "direct_answer"
builder=StateGraph(State)
builder.add_node("classify_intent",classify_intent); builder.add_node("retrieve_and_answer",retrieve_and_answer); builder.add_node("direct_answer",direct_answer)
builder.add_edge(START,"classify_intent")
builder.add_conditional_edges("classify_intent",route,{"retrieve_and_answer":"retrieve_and_answer","direct_answer":"direct_answer"})
builder.add_edge("retrieve_and_answer",END); builder.add_edge("direct_answer",END); graph=builder.compile()
app=FastAPI(title="Zepto Policy Assistant")
@app.on_event("startup")
def startup(): initialize_index()
@app.post("/ask",response_model=AskResponse)
def ask(req:AskRequest):
    if _collection is None: initialize_index()
    result=graph.invoke({"query":req.query})
    return AskResponse(answer=result["answer"],sources=result.get("sources",[]),confidence=result.get("confidence",1.0))
if __name__=="__main__":
    initialize_index()
    for question in ["What is the delivery fee?","Tell me a joke"]:
        print(json.dumps(ask(AskRequest(query=question)).model_dump()))
