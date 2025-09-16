import io
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import new_session, remove
from PIL import Image

# --- Configuration ---
# Specify the models to pre-load on startup
PRELOADED_MODELS = [
    "isnet-general-use",
    "u2net",
    "isnet-anime",
]
DEFAULT_MODEL = "isnet-general-use"
# -------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the rembg models on startup and store them in app.state.
    """
    print("服务器启动，正在加载 rembg 模型...")
    app.state.rembg_sessions = {}
    for model_name in PRELOADED_MODELS:
        try:
            print(f"  - 正在加载 {model_name}...")
            app.state.rembg_sessions[model_name] = new_session(model_name)
        except Exception as e:
            print(f"  - 加载模型 {model_name} 失败: {e}")
    
    if not app.state.rembg_sessions:
        print("警告：没有任何模型被成功加载，服务可能无法正常工作。")
    else:
        print(f"模型加载完成。可用模型: {list(app.state.rembg_sessions.keys())}")
    
    yield
    
    # Clean up resources if needed on shutdown
    print("服务器关闭。")
    app.state.rembg_sessions = None

# Create the FastAPI app with the lifespan event handler
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/models")
async def get_models(request: Request):
    """
    Returns a list of available, pre-loaded models.
    """
    if not hasattr(request.app.state, 'rembg_sessions') or not request.app.state.rembg_sessions:
        return {"models": []}
    return {"models": list(request.app.state.rembg_sessions.keys())}

@app.post("/remove")
async def remove_background_api(
    file: UploadFile = File(...),
    model: str = Form(DEFAULT_MODEL)
):
    """
    API endpoint to remove the background from an uploaded image.
    Accepts a 'model' form field to specify which model to use.
    """
    # Check if the requested model is available
    if model not in app.state.rembg_sessions:
        raise HTTPException(
            status_code=400, 
            detail=f"模型 '{model}' 不可用。可用模型: {list(app.state.rembg_sessions.keys())}"
        )

    # Get the appropriate session from app state
    session = app.state.rembg_sessions[model]

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