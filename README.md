# Rembg Background Removal Server

This project is a lightweight web server built using FastAPI that wraps the powerful [rembg](https://github.com/danielgatis/rembg) library. It provides a simple API endpoint to remove the background from images.

It has been tested and confirmed to run smoothly on a server with **2 CPU cores and 2GB of RAM**.

## Features

-   Simple, single-endpoint API.
-   Uses the `isnet-general-use` model from `rembg`.
-   Efficiently pre-loads the model on server startup.
-   Streams the processed image back to the client, minimizing server memory usage.

## Installation

1.  Clone this repository to your server.
2.  Install the necessary dependencies

    ```bash
    pip install "rembg[cpu,cli]"
    ```

## Usage

Run the server using `uvicorn`. The following command will start the server on port 7000 and make it accessible from your local network.

```bash
uvicorn main:app --host 0.0.0.0 --port 7000
```

## API Endpoint

### POST /remove

This is the main endpoint for removing the background from an image.

-   **Method**: `POST`
-   **URL**: `/remove`
-   **Form Data**: `file`: The image file you want to process.

#### Example using cURL

You can test the endpoint from your command line using `curl`:

```bash
curl -X POST -F "file=@/path/to/your/image.jpg" http://your-server-ip:7000/remove -o output.png
```

Replace `/path/to/your/image.jpg` with the actual path to your input image and `your-server-ip` with the IP address of the server running the application. The processed image with the background removed will be saved as `output.png`.
