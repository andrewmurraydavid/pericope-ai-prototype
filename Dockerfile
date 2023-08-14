# Use Python 3.11 LTS as the parent image
FROM python:3.11-slim

# Set the working directory in the docker container
WORKDIR /app

# Copy the current directory (on your machine) to the container at /app
COPY . /app

# Install Flask and any other dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Download all the required model files to make app boot faster
RUN python initialize-model.py

# recopy the current directory to the container at /app
COPY . /app

# Make port 5000 available to the outside world
EXPOSE 5000

# Define environment variable to ensure Flask runs in production mode
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Run the Flask app
CMD ["flask", "run"]
