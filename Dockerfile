# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and binary
COPY . .

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]