# Dockerfile for the Rembg Server

# 1. Use an official Python runtime as a parent image
FROM python:3.13-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file into the container
COPY requirements.txt .

# 4. Install any needed packages specified in requirements.txt
# We also download the model files here to bake them into the image
RUN pip install --no-cache-dir -r requirements.txt && \
    rembg d isnet-general-use

# 5. Copy the rest of the application's code into the container
COPY . .

# 6. Expose the port the app runs on
EXPOSE 7000

# 7. Run Uvicorn server when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]