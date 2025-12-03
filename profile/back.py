from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import time
from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5000",
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.post("/upload")
async def upload_document(document: UploadFile = File(...)):
    # Генеруємо унікальну назву файла
    timestamp = str(int(time.time()))
    file_extension = os.path.splitext(document.filename)[1]
    filename = timestamp + file_extension

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Зберігаємо файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(document.file, buffer)

    return JSONResponse({
        "message": "Файл збережено",
        "filename": filename,
        "path": f"/uploads/{filename}"
    })
