# Rembg Background Removal Server

This project is a lightweight web server built using FastAPI that wraps the powerful [rembg](https://github.com/danielgatis/rembg) library. It provides simple API endpoints to remove the background from images using various pre-trained models.

It has been tested and confirmed to run smoothly on a server with **2 CPU cores and 2GB of RAM**.

## Features

- Simple, multi-endpoint API with JSON configuration
- Supports 15+ different AI models for background removal
- Model enable/disable configuration for flexible deployment
- Session auto-cleanup after each request (no model pre-loading)
- Streams the processed image back to the client, minimizing server memory usage
- Comprehensive logging with different log levels
- JSON-based configuration management
- Direct Python execution with command-line arguments

## Installation

### Method 1: Direct Installation

1. Clone this repository to your server.
2. Install the necessary dependencies:

    ```bash
    pip install rembg[cpu,cli]
    ```

3. Configure models in `models.json` file. The server will automatically download required models on first use.

### Method 2: Docker Installation

1. Build the Docker image:
    ```bash
    docker build -t rembg-server .
    ```

2. Run the container:
    ```bash
    docker run -d --name rembg-service -p 7001:7001 rembg-server
    ```

3. Run with custom port:
    ```bash
    docker run -d -p 8080:8080 -e PORT=8080 --name rembg-service rembg-server
    ```

## Configuration

The server uses a `models.json` file for configuration. This file contains:

- **models**: Array of model configurations with name, description, and enabled status
- **default_model**: Default model when none is specified

Example `models.json`:
```json
{
  "models": [
    {
      "name": "u2net",
      "desc": "通用",
      "enabled": false
    },
    {
      "name": "silueta",
      "desc": "轻量级通用",
      "enabled": true
    },
    {
      "name": "isnet-general-use",
      "desc": "通用",
      "enabled": true
    },
    {
      "name": "isnet-anime",
      "desc": "动漫",
      "enabled": true
    }
  ],
  "default_model": "silueta"
}
```

### Model Configuration

- **enabled: true** - Model is available via API and can be used
- **enabled: false** - Model is disabled and won't appear in `/models` endpoint
- Only enabled models consume memory and are accessible via the API

## Usage

### Local Development

Run the server using the built-in Python script:

```bash
# Default port 7001
python main.py

# Custom port
python main.py -p 8080

# Custom host and port
python main.py --host 127.0.0.1 -p 8080

# View help
python main.py --help
```

### Command Line Options

```
usage: main.py [-h] [-p PORT] [--host HOST]

rembg 背景移除服务器

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  服务器端口 (默认: 7001)
  --host HOST           服务器主机地址 (默认: 0.0.0.0)
```

## API Endpoints

### GET /

Returns a welcome message with basic information about the server.

- **Method**: `GET`
- **URL**: `/`

#### Example Response

```json
{
  "message": "欢迎使用 rembg 背景移除服务器。"
}
```

### GET /models

Returns a list of enabled models with their names and descriptions.

- **Method**: `GET`
- **URL**: `/models`

#### Example using cURL

```bash
curl http://your-server-ip:7001/models
```

#### Example Response

```json
{
  "models": [
    {
      "name": "silueta",
      "desc": "轻量级通用"
    },
    {
      "name": "isnet-general-use",
      "desc": "通用"
    },
    {
      "name": "isnet-anime",
      "desc": "动漫"
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

- **Method**: `POST`
- **URL**: `/remove`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `file`: The image file you want to process. (Required)
  - `model`: The name of the model to use for processing. (Optional, defaults to `silueta`). Must be one of the enabled models from the `/models` endpoint.

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | Yes | - | Image file (JPG, PNG, etc.) |
| `model` | String | No | `silueta` | Model name to use for processing |

#### Response

- **Success**: Returns the processed image as PNG file
- **Error**: Returns JSON error message with HTTP error code

#### Example using cURL

**1. Using the default model (silueta):**

```bash
curl -X POST \
  -F "file=@/path/to/your/image.jpg" \
  http://your-server-ip:7001/remove \
  -o output.png
```

**2. Specifying a different model:**

```bash
curl -X POST \
  -F "file=@/path/to/your/anime-image.jpg" \
  -F "model=isnet-anime" \
  http://your-server-ip:7001/remove \
  -o output_anime.png
```

**3. Using a general-use model:**

```bash
curl -X POST \
  -F "file=@/path/to/your/image.jpg" \
  -F "model=isnet-general-use" \
  http://your-server-ip:7001/remove \
  -o output_general.png
```

#### Error Responses

```json
{
  "detail": "模型 'invalid-model' 不可用或未启用。可用模型: ['silueta', 'isnet-general-use', 'isnet-anime']"
}
```

## Performance Notes

- **Session Auto-Cleanup**: Each request creates a new session that's automatically garbage collected after use
- **No Pre-loading**: Models are loaded on-demand, reducing memory usage when idle
- **Memory Efficient**: Only enabled models are available, reducing overall memory footprint
- **Docker Optimization**: Docker image pre-downloads commonly used models for faster first-time usage

## Docker Configuration

The Docker image includes several optimizations:

- **Pre-downloaded Models**: `silueta`, `isnet-general-use`, `isnet-anime`
- **Environment Variables**: Use `PORT` to customize the listening port
- **Default Port**: 7001 (configurable via environment variable)

### Docker Examples

```bash
# Build and run on default port 7001
docker build -t rembg-server .
docker run -d -p 7001:7001 --name rembg rembg-server

# Run on custom port 8080
docker run -d -p 8080:8080 -e PORT=8080 --name rembg rembg-server

# Run with volume mount for custom models.json
docker run -d -p 7001:7001 -v ./models.json:/app/models.json --name rembg rembg-server
```

## Acknowledgments

This project is built on top of the excellent [rembg](https://github.com/danielgatis/rembg) library by [@danielgatis](https://github.com/danielgatis). We extend our sincere gratitude for creating and maintaining this powerful background removal tool that makes AI-powered image processing accessible to everyone.

**🙏 Special thanks to:**
- [danielgatis/rembg](https://github.com/danielgatis/rembg) - The core background removal library
- The rembg community and contributors  
- All the researchers behind the AI models (U²-Net, IS-Net, BiRefNet, SAM, etc.)