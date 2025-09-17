import io
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import new_session, remove
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
def load_config():
    """
    Load configuration from models.json file.
    """
    try:
        with open('models.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Validate required fields
            if 'models' not in data:
                raise ValueError("Missing 'models' field in models.json")
            if 'preloaded_models' not in data:
                raise ValueError("Missing 'preloaded_models' field in models.json")
            if 'default_model' not in data:
                raise ValueError("Missing 'default_model' field in models.json")
                
            return data
    except FileNotFoundError:
        logger.error("找不到 models.json 文件")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"models.json 文件格式错误: {e}")
        raise
    except ValueError as e:
        logger.error(f"models.json 配置错误: {e}")
        raise

# Load configuration from JSON file
config = load_config()
MODEL_DESCRIPTIONS = config['models']
PRELOADED_MODELS = config['preloaded_models']
DEFAULT_MODEL = config['default_model']
# -------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the rembg models on startup and store them in app.state.
    """
    logger.info("服务器启动，正在加载 rembg 模型...")
    app.state.rembg_sessions = {}
    for model_name in PRELOADED_MODELS:
        try:
            logger.info(f"  - 正在加载 {model_name}...")
            app.state.rembg_sessions[model_name] = new_session(model_name)
        except Exception as e:
            logger.error(f"  - 加载模型 {model_name} 失败: {e}")
    
    if not app.state.rembg_sessions:
        logger.warning("没有任何模型被成功加载，服务可能无法正常工作。")
    else:
        logger.info(f"模型加载完成。可用模型: {list(app.state.rembg_sessions.keys())}")
    
    yield
    
    # Clean up resources if needed on shutdown
    logger.info("服务器关闭。")
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
    Returns a list of available, pre-loaded models with their descriptions.
    """
    if not hasattr(request.app.state, 'rembg_sessions') or not request.app.state.rembg_sessions:
        return {"models": []}
    
    models_with_descriptions = []
    for model_name in request.app.state.rembg_sessions.keys():
        model_info = {
            "name": model_name,
            "description": MODEL_DESCRIPTIONS.get(model_name, "No description available.")
        }
        models_with_descriptions.append(model_info)
    
    return {"models": models_with_descriptions}

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
    return {"message": "欢迎使用 rembg 背景移除服务器。"}