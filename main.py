import io
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import new_session, remove
from PIL import Image

# --- Configuration ---
# Specify the model to use
model_name = "isnet-general-use"
# -------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the rembg model on startup and store it in app.state.
    """
    print("服务器启动，正在加载 rembg 模型...")
    app.state.rembg_session = new_session(model_name)
    print("模型加载完成。")
    yield
    # Clean up resources if needed on shutdown
    print("服务器关闭。")
    app.state.rembg_session = None

# Create the FastAPI app with the lifespan event handler
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源的请求
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 请求头
)

@app.post("/remove")
async def remove_background_api(request: Request, file: UploadFile = File(...)):
    """
    API endpoint to remove the background from an uploaded image.
    """
    # Get the rembg session from app state
    session = request.app.state.rembg_session

    # Read the image data from the upload
    contents = await file.read()
    
    # Open the image using PIL
    input_image = Image.open(io.BytesIO(contents))
    
    # Remove the background
    output_image = remove(input_image, session=session)
    
    # Save the output image to a byte stream
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # Return the image as a streaming response
    return StreamingResponse(img_byte_arr, media_type="image/png")

@app.get("/")
def read_root():
    return {"message": "欢迎使用 rembg 背景移除服务器。请 POST 图片文件到 /remove 端点。"}

