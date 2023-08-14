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
COPY . /app

# Install git-lfs
RUN apt update && apt install -y git-lfs

RUN rm -rf .git/hooks
RUN git lfs install
RUN git lfs install --skip-smudge
RUN which git-lfs

# RUN git lfs install
RUN GIT_TRACE=1 git-lfs fetch && git-lfs pull

# List the contents of /app/models
RUN ls -la /app/models/all-distilroberta-v1

# Install Flask and any other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the outside world
EXPOSE 5000

# Define environment variable to ensure Flask runs in production mode
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Run the Flask app
CMD ["flask", "run"]
