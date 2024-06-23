# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install bash, curl, and other dependencies
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    build-essential \
    && apt-get clean

# Install Rust and Cargo
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
