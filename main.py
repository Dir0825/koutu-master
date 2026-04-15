# Deta Space deployment
# https://deta.space

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from PIL import Image
import io
import uuid

try:
    from rembg import remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "抠图大师 API", "rembg": HAS_REMBG}

@app.get("/api/status")
async def status():
    return {"status": "ready", "rembg": HAS_REMBG}

@app.post("/api/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        input_data = await file.read()
        input_img = Image.open(io.BytesIO(input_data)).convert('RGBA')

        if HAS_REMBG:
            output_img = remove(input_img)
        else:
            output_img = simple_remove_bg(input_img)

        output_buffer = io.BytesIO()
        output_img.save(output_buffer, format='PNG')
        output_data = output_buffer.getvalue()

        return Response(content=output_data, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}

def simple_remove_bg(img):
    import numpy as np
    arr = np.array(img)
    bg_color = arr[0, 0]
    diff = np.abs(arr[:, :, :3].astype(int) - bg_color[:3].astype(int))
    distance = np.sqrt(np.sum(diff ** 2, axis=2))
    threshold = 50
    mask = distance < threshold
    arr[:, :, 3] = np.where(mask, 0, 255)
    return Image.fromarray(arr)
