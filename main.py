import io
import json
import logging
import argparse
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import new_session, remove
from rembg.sessions import sessions_names
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

def get_enabled_models(config):
    """
    Get list of enabled models from configuration.
    """
    enabled_models = {}
    enabled_model_names = []
    
    for model in config['models']:
        if model.get('enabled', True):  # Default to enabled if not specified
            enabled_models[model['name']] = model.get('desc', 'No description available.')
            enabled_model_names.append(model['name'])
    
    return enabled_models, enabled_model_names

# Load configuration from JSON file
config = load_config()
MODEL_DESCRIPTIONS, ENABLED_MODEL_NAMES = get_enabled_models(config)
DEFAULT_MODEL = config['default_model']

# Validate that default model is enabled
if DEFAULT_MODEL not in ENABLED_MODEL_NAMES:
    logger.warning(f"默认模型 '{DEFAULT_MODEL}' 未启用，使用第一个启用的模型")
    if ENABLED_MODEL_NAMES:
        DEFAULT_MODEL = ENABLED_MODEL_NAMES[0]
    else:
        logger.error("没有启用的模型！")
        raise ValueError("No enabled models found in configuration")

logger.info(f"启用的模型: {ENABLED_MODEL_NAMES}")
logger.info(f"默认模型: {DEFAULT_MODEL}")
# -------------------

# Create the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/models")
async def get_models():
    """
    Returns a list of enabled models with their descriptions.
    """
    models_with_descriptions = []
    for model_name in ENABLED_MODEL_NAMES:
        # Double check that the model exists in rembg sessions
        if model_name in sessions_names:
            model_info = {
                "name": model_name,
                "desc": MODEL_DESCRIPTIONS.get(model_name, "No description available.")
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
    Creates a new session for each request for automatic cleanup.
    """
    # Check if the requested model is enabled and available
    if model not in ENABLED_MODEL_NAMES:
        raise HTTPException(
            status_code=400, 
            detail=f"模型 '{model}' 不可用或未启用。可用模型: {ENABLED_MODEL_NAMES}"
        )
    
    # Double check that the model exists in rembg sessions
    if model not in sessions_names:
        raise HTTPException(
            status_code=400, 
            detail=f"模型 '{model}' 在rembg中不存在。"
        )

    # Read the image data from the upload
    contents = await file.read()
    
    # Open the image using PIL
    input_image = Image.open(io.BytesIO(contents))
    
    # Create a new session for this request (will be automatically garbage collected after use)
    session = new_session(model)
    
    try:
        # Remove the background
        output_image = remove(input_image, session=session)
        
        # Save the output image to a byte stream
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Return the image as a streaming response
        return StreamingResponse(img_byte_arr, media_type="image/png")
    finally:
        # Session will be automatically garbage collected when it goes out of scope
        # No explicit cleanup needed as ONNX Runtime handles resource cleanup
        pass

@app.get("/")
def read_root():
    return {"message": "欢迎使用 rembg 背景移除服务器。"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="rembg 背景移除服务器")
    parser.add_argument(
        "-p", "--port", 
        type=int, 
        default=7001, 
        help="服务器端口 (默认: 7001)"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0", 
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"启动 rembg 背景移除服务器...")
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        log_level="info",
        reload=False
    )