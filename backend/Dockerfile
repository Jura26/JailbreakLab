# Use official PyTorch image with CPU support
FROM pytorch/pytorch:2.9.0-cuda12.8-cudnn9-runtime

# Set working directory
WORKDIR /app

# Copy only requirements first (to leverage Docker cache)
COPY requirements.txt .

# Install Python dependencies (excluding torch, already in base image)
RUN pip install --no-cache-dir -r requirements.txt

# Download only the stopwords corpus at build time
RUN python -m nltk.downloader -d /usr/share/nltk_data stopwords

# Make sure nltk can find the corpus
ENV NLTK_DATA=/usr/share/nltk_data

ENV PYTHONPATH=/app

# Copy the rest of the backend code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
