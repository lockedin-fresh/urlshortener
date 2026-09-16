# Base image — slim keeps the image small
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first (Docker layer caching trick —
# if requirements.txt hasn't changed, Docker skips reinstalling on rebuilds)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app code
COPY . .

# Flask will run on this port inside the container
EXPOSE 5000

# Command to start the app
CMD ["python", "app.py"]
