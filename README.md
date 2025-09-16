# Rembg Background Removal Server

This project is a lightweight web server built using FastAPI that wraps the powerful [rembg](https://github.com/danielgatis/rembg) library. It provides simple API endpoints to remove the background from images using various pre-trained models.

It has been tested and confirmed to run smoothly on a server with **2 CPU cores and 2GB of RAM**.

## Features

-   Simple, multi-endpoint API.
-   Supports dynamic model selection for background removal.
-   Provides an endpoint to list all available models.
-   Efficiently pre-loads multiple models on server startup.
-   Streams the processed image back to the client, minimizing server memory usage.

## Installation

1.  Clone this repository to your server.
2.  Install the necessary dependencies using `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```
3.  Ensure the models you want to use are downloaded. You can add them to the `PRELOADED_MODELS` list in `main.py` and they will be downloaded on first run, or download them manually:
    ```bash
    rembg d isnet-general-use isnet-anime u2net
    ```

## Usage

Run the server using `uvicorn`. The following command will start the server on port 7000 and make it accessible from your local network.

```bash
uvicorn main:app --host 0.0.0.0 --port 7000
```

## API Endpoints

### GET /models

Returns a list of the models that are currently loaded and available for processing.

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
    "isnet-general-use",
    "u2net",
    "isnet-anime"
  ]
}
```

### POST /remove

This is the main endpoint for removing the background from an image.

-   **Method**: `POST`
-   **URL**: `/remove`
-   **Form Data**:
    -   `file`: The image file you want to process. (Required)
    -   `model`: The name of the model to use for processing. (Optional, defaults to `isnet-general-use`). Must be one of the models returned by the `/models` endpoint.

#### Example using cURL

**1. Using the default model:**

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

Replace `/path/to/your/image.jpg` with the actual path to your input image and `your-server-ip` with the IP address of the server running the application. The processed image with the background removed will be saved to the specified output file.
