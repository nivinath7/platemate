from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from rag.ingestion import combine_elements_into_chunks, embed, store
from rag.retrieval import retrieve, generate
from unstructured.partition.pdf import partition_pdf
from pydantic import BaseModel
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    user_id: str
    history: list = []

@app.post("/ingest")

async def ingest(file: UploadFile = File(...), user_id: str = Form(...)):

    with open(f"temp_{file.filename}", "wb") as f:
        content = await file.read()
        f.write(content)
    
    elements = partition_pdf(filename=f"temp_{file.filename}", strategy='hi_res')
    chunks = combine_elements_into_chunks(elements, source=file.filename, user_id=user_id)
    embedded_chunks = embed(chunks)
    store(embedded_chunks)

    os.remove(f"temp_{file.filename}")

    return {"message": "PDF ingested successfully", "filename": file.filename}


    
@app.post("/chat")
async def chat(request: ChatRequest):

    results = retrieve(request.query, request.user_id)
    # print(results)
    # print(f"QUERY: {request.query}")
    # print(f"DOCUMENTS: {results['documents']}")

    history = [{"role" : m["role"], "content" : m["content"]} for m in request.history]

    llm_output = generate(request.query, results, history)

    conversation_chunk = {
        "user_query" : request.query,
        "llm_output" : llm_output
    }

    request.history.append(conversation_chunk)
    
    return {"answer" : llm_output}