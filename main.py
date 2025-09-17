import io
import json
import logging
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

# Load configuration from JSON file
config = load_config()
MODEL_DESCRIPTIONS = config['models']
DEFAULT_MODEL = config['default_model']
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
    Returns a list of all available models with their descriptions.
    """
    models_with_descriptions = []
    for model_name in sessions_names:
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
    Creates a new session for each request for automatic cleanup.
    """
    # Check if the requested model is available
    if model not in sessions_names:
        raise HTTPException(
            status_code=400, 
            detail=f"模型 '{model}' 不可用。可用模型: {list(sessions_names)}"
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