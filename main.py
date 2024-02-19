from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,File,UploadFile
from fastapi.responses import FileResponse
from PIL import Image
import io
import cv2
import os
import numpy as np
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from time import sleep
import uvicorn


app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/uploadImage")
async def upload_image(file: bytes = File(...)):
    image = Image.open(io.BytesIO(file))
    for file in os.listdir('./images'):
        if file.endswith('.jpg'):
            print(file)
            os.remove(F"./images/{file}") 
    image.save(F"./images/temp.jpg")   
    await process()
    
    return {"fileName":"hello"}

@app.get("/getOriginalImage")
async def get_OriginalImage():
    image_path = Path("./images/temp.jpg")
    return FileResponse(image_path)

@app.get("/getProcessedImage")
async def get_ProcessedImage():
    image_path = Path("./images/processed.jpg")
    return FileResponse(image_path)

@app.get("/getResultImage")
async def get_ResultImage():
    image_path = Path("./images/enhanced.jpg")
    return FileResponse(image_path)
    

async def process():
    try:
        input_image_path = "./images/temp.jpg"
        original_image = cv2.imread(input_image_path)
        converted_image = cv2.convertScaleAbs(original_image)
        enhanced_image = cv2.detailEnhance(converted_image, sigma_s=70, sigma_r=0.6)
        gray_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
        blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
        edges = cv2.Canny(blurred_image, 30, 100)
        edges = cv2.resize(edges, (enhanced_image.shape[1], enhanced_image.shape[0]))
        edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        ir_enhanced = cv2.addWeighted(enhanced_image, 1, edges_color, 1, 0)
        cv2.imwrite("./images/processed.jpg",edges)
        cv2.imwrite("./images/enhanced.jpg",ir_enhanced)

    except Exception as e:
        print("Error")



@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

