import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.upload import router as upload_router
from routes.jobs import router as jobs_router
from routes.stems import router as stems_router
from routes.export import router as export_router

load_dotenv()

app = FastAPI(title="Music Tool API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(jobs_router)
app.include_router(stems_router)
app.include_router(export_router)


@app.get("/health")
def health():
    return {"status": "ok"}
