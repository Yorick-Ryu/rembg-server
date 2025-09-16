# Rembg Background Removal Server

This project is a lightweight web server built using FastAPI that wraps the powerful [rembg](https://github.com/danielgatis/rembg) library. It provides simple API endpoints to remove the background from images using various pre-trained models.

It has been tested and confirmed to run smoothly on a server with **2 CPU cores and 2GB of RAM**.

## Features

-   Simple, multi-endpoint API with JSON configuration
-   Supports 15+ different AI models for background removal
-   Provides an endpoint to list all available models with descriptions
-   Efficiently pre-loads selected models on server startup
-   Dynamic model loading for non-preloaded models
-   Streams the processed image back to the client, minimizing server memory usage
-   Comprehensive logging with different log levels
-   JSON-based configuration management

## Installation

### Method 1: Direct Installation

1.  Clone this repository to your server.
2.  Install the necessary dependencies:

    ```bash
    pip install rembg[cpu,cli]
    ```

3.  Configure models in `models.json` file. The server will automatically download required models on first use.

### Method 2: Docker Installation

1.  Build the Docker image:
    ```bash
    docker build -t rembg-server .
    ```

2.  Run the container:
    ```bash
    docker run -d --name rembg-service -p 7000:7000 rembg-server
    ```

## Configuration

The server uses a `models.json` file for configuration. This file contains:

- **models**: All available models with their Chinese descriptions
- **preloaded_models**: Models to load on server startup (faster response)
- **default_model**: Default model when none is specified

Example `models.json`:
```json
{
  "models": {
    "silueta": "轻量化通用",
    "isnet-general-use": "通用",
    "isnet-anime": "针对动漫角色的高精度分割模型"
  },
  "preloaded_models": ["isnet-general-use", "silueta"],
  "default_model": "silueta"
}
```

## Usage

Run the server using `uvicorn`. The following command will start the server on port 7000 and make it accessible from your local network.

```bash
uvicorn main:app --host 0.0.0.0 --port 7000
```

## API Endpoints

### GET /

Returns a welcome message with basic information about the server.

-   **Method**: `GET`
-   **URL**: `/`

#### Example Response

```json
{
  "message": "欢迎使用 rembg 背景移除服务器。。"
}
```

### GET /models

Returns a list of all available models with their names and Chinese descriptions.

-   **Method**: `GET`
-   **URL**: `/models`

#### Example using cURL

```bash
curl http://your-server-ip:7000/models
```

#### Example Response

```json
{
  "models": [
    {
      "name": "isnet-general-use",
      "description": "通用"
    },
    {
      "name": "silueta", 
      "description": "轻量化通用"
    },
    {
      "name": "u2net",
      "description": "通用"
    },
    {
      "name": "isnet-anime",
      "description": "针对动漫角色的高精度分割模型"
    },
    {
      "name": "u2netp",
      "description": "u2net 模型的轻量级版本"
    }
  ]
}
```

#### Available Models

The server supports 15+ different AI models for various use cases. For a complete list of available models with detailed descriptions and download links, please visit the official rembg documentation:

**📋 [View All Available Models](https://github.com/danielgatis/rembg?tab=readme-ov-file#models)**

Popular models include:
- `u2net` - General purpose background removal
- `silueta` - Lightweight version (43MB)  
- `isnet-anime` - High-accuracy anime character segmentation
- `birefnet-portrait` - Specialized for portrait segmentation
- `sam` - Advanced model for any use case

### POST /remove

This is the main endpoint for removing the background from an image.

-   **Method**: `POST`
-   **URL**: `/remove`
-   **Content-Type**: `multipart/form-data`
-   **Form Data**:
    -   `file`: The image file you want to process. (Required)
    -   `model`: The name of the model to use for processing. (Optional, defaults to `silueta`). Must be one of the models from the `/models` endpoint.

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | Yes | - | Image file (JPG, PNG, etc.) |
| `model` | String | No | `silueta` | Model name to use for processing |

#### Response

-   **Success**: Returns the processed image as PNG file
-   **Error**: Returns JSON error message with HTTP error code

#### Example using cURL

**1. Using the default model (silueta):**

```bash
curl -X POST \
  -F "file=@/path/to/your/image.jpg" \
  http://your-server-ip:7000/remove \
  -o output.png
```

**2. Specifying a different model:**

```bash
curl -X POST \
  -F "file=@/path/to/your/anime-image.jpg" \
  -F "model=isnet-anime" \
  http://your-server-ip:7000/remove \
  -o output_anime.png
```

**3. Using a lightweight model for faster processing:**

```bash
curl -X POST \
  -F "file=@/path/to/your/image.jpg" \
  -F "model=u2netp" \
  http://your-server-ip:7000/remove \
  -o output_light.png
```

#### Error Responses

```json
{
  "detail": "模型 'invalid-model' 不可用。可用模型: ['isnet-general-use', 'silueta']"
}
```

## Performance Notes

- **Preloaded models** (`isnet-general-use`, `silueta`) respond faster as they're loaded at startup
- **Non-preloaded models** are loaded on first use, which may take longer initially
- The server automatically manages model memory and loading
- Docker deployment includes optimized model pre-loading

## Acknowledgments

This project is built on top of the excellent [rembg](https://github.com/danielgatis/rembg) library by [@danielgatis](https://github.com/danielgatis). We extend our sincere gratitude for creating and maintaining this powerful background removal tool that makes AI-powered image processing accessible to everyone.

**🙏 Special thanks to:**
- [danielgatis/rembg](https://github.com/danielgatis/rembg) - The core background removal library
- The rembg community and contributors  
- All the researchers behind the AI models (U²-Net, IS-Net, BiRefNet, SAM, etc.)
