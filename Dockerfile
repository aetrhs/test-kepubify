# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and binary
COPY . .

# Make kepubify executable (for Linux; Windows .exe works via Wine/Mono but we use Linux binary)
RUN chmod +x bin/kepubify

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]