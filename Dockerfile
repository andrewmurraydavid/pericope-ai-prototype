# Use Python 3.11 LTS as the parent image
FROM python:3.11-slim

ARG CHROMA_HOST
ENV CHROMA_HOST=$CHROMA_HOST

ARG CHROMA_PORT
ENV CHROMA_PORT=$CHROMA_PORT

ARG CHROMA_SSL
ENV CHROMA_SSL=$CHROMA_SSL

ARG MODEL_NAME
ENV MODEL_NAME=$MODEL_NAME

ARG COLLECTION_NAME
ENV COLLECTION_NAME=$COLLECTION_NAME

# Set the working directory in the docker container
WORKDIR /app

# Copy the current directory (on your machine) to the container at /app
COPY . /app
COPY models /app/models

# List the contents of /app/models
RUN ls -la /app/models

# Install git-lfs
RUN apt-get update && apt-get install -y git-lfs

# RUN git lfs install
RUN git lfs pull --include="models/all-distilroberta-v1/*"

# Install Flask and any other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Comment these out until we know how to get the model files into the container
# # Download all the required model files to make app boot faster
# RUN python initialize-model.py

# # recopy the current directory to the container at /app
# COPY . /app

# Make port 5000 available to the outside world
EXPOSE 5000

# Define environment variable to ensure Flask runs in production mode
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Run the Flask app
CMD ["flask", "run"]
