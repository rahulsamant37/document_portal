import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from src.document_ingestion.data_ingestion import (
    DocHandler,
    DocumentComparator,
    ChatIngestor,
)
from src.document_analyzer.data_analysis import DocumentAnalyzer
from src.document_compare.document_comparator import DocumentComparatorLLM
from src.document_chat.retrieval import ConversationalRAG
from utils.document_ops import FastAPIFileAdapter,read_pdf_via_handler
from logger import GLOBAL_LOGGER as log
# from exception.custom_exception import DocumentPortalException

FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index")
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "index")  # <--- keep consistent with save_local()

app = FastAPI(title="Document Portal API", version="0.1")

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    log.info("Serving UI homepage", client_host=request.client.host if request.client else "unknown")
    resp = templates.TemplateResponse("index.html", {"request": request})
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.get("/health")
def health() -> Dict[str, str]:
    log.info("Health check requested")
    return {"status": "ok", "service": "document-portal"}

# ---------- ANALYZE ----------
@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)) -> Any:
    try:
        log.info("Received file for analysis", filename=file.filename, content_type=file.content_type)
        dh = DocHandler()
        saved_path = dh.save_pdf(FastAPIFileAdapter(file))
        text = read_pdf_via_handler(dh, saved_path)
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_document(text)
        log.info("Document analysis complete", filename=file.filename, result_keys=list(result.keys()) if isinstance(result, dict) else "non-dict")
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        log.error("Error during document analysis", 
                 filename=file.filename, 
                 error=str(e), 
                 error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

# ---------- COMPARE ----------
@app.post("/compare")
async def compare_documents(reference: UploadFile = File(...), actual: UploadFile = File(...)) -> Any:
    try:
        log.info("Comparing files", 
                reference_file=reference.filename, 
                actual_file=actual.filename,
                reference_type=reference.content_type,
                actual_type=actual.content_type)
        dc = DocumentComparator()
        ref_path, act_path = dc.save_uploaded_files(
            FastAPIFileAdapter(reference), FastAPIFileAdapter(actual)
        )
        _ = ref_path, act_path
        combined_text = dc.combine_documents()
        comp = DocumentComparatorLLM()
        df = comp.compare_documents(combined_text)
        log.info("Document comparison completed", 
                session_id=dc.session_id, 
                comparison_rows=len(df) if hasattr(df, '__len__') else "unknown")
        return {"rows": df.to_dict(orient="records"), "session_id": dc.session_id}
    except HTTPException:
        raise
    except Exception as e:
        log.error("Comparison failed", 
                 reference_file=reference.filename, 
                 actual_file=actual.filename,
                 error=str(e), 
                 error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {e}")

# ---------- CHAT: INDEX ----------
@app.post("/chat/index")
async def chat_build_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5),
) -> Any:
    try:
        filenames = [f.filename for f in files]
        log.info("Indexing chat session", 
                session_id=session_id, 
                file_count=len(files),
                filenames=filenames,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                k=k)
        wrapped = [FastAPIFileAdapter(f) for f in files]
        # this is my main class for storing a data into VDB
        # created a object of ChatIngestor
        ci = ChatIngestor(
            temp_base=UPLOAD_BASE,
            faiss_base=FAISS_BASE,
            use_session_dirs=use_session_dirs,
            session_id=session_id or None,
        )
        # NOTE: ensure your ChatIngestor saves with index_name="index" or FAISS_INDEX_NAME
        # e.g., if it calls FAISS.save_local(dir, index_name=FAISS_INDEX_NAME)
        ci.built_retriver(  # if your method name is actually build_retriever, fix it there as well
            wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k
        )
        log.info("Index created successfully", 
                session_id=ci.session_id, 
                final_k=k,
                use_session_dirs=use_session_dirs)
        return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}
    except HTTPException:
        raise
    except Exception as e:
        log.error("Chat index building failed", 
                 session_id=session_id,
                 file_count=len(files) if files else 0,
                 error=str(e), 
                 error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")

# ---------- CHAT: QUERY ----------
@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
) -> Any:
    try:
        log.info("Received chat query", 
                question=question[:100] + "..." if len(question) > 100 else question,
                session_id=session_id,
                use_session_dirs=use_session_dirs,
                k=k)
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when use_session_dirs=True")

        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE  # type: ignore
        if not os.path.isdir(index_dir):
            log.warning("FAISS index not found", 
                       index_dir=index_dir, 
                       session_id=session_id,
                       use_session_dirs=use_session_dirs)
            raise HTTPException(status_code=404, detail=f"FAISS index not found at: {index_dir}")

        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_dir, k=k, index_name=FAISS_INDEX_NAME)  # build retriever + chain
        response = rag.invoke(question, chat_history=[])
        log.info("Chat query handled successfully", 
                session_id=session_id,
                response_length=len(str(response)) if response else 0)

        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG"
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("Chat query failed", 
                 question=question[:50] + "..." if len(question) > 50 else question,
                 session_id=session_id,
                 error=str(e), 
                 error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

# command for executing the fast api
# uvicorn api.main:app --port 8000 --reload    
#uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload