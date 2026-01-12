# Use official PyTorch image with CPU support
FROM pytorch/pytorch:2.9.0-cuda12.8-cudnn9-runtime

# Set working directory
WORKDIR /app

# Copy only requirements first (to leverage Docker cache)
COPY requirements.txt .

# Install Python dependencies (excluding torch, already in base image)
RUN pip install --no-cache-dir -r requirements.txt

# Accept the token as build arg
ARG GUARDRAILS_API_KEY


# Set it as env var
ENV GUARDRAILS_API_KEY=${GUARDRAILS_API_KEY}

# Configure Guardrails with the token
RUN guardrails configure --enable-metrics --enable-remote-inferencing  --token $GUARDRAILS_API_KEY

# Now install the validator
RUN guardrails hub install hub://guardrails/detect_jailbreak


# Download only the stopwords corpus at build time
RUN python -m nltk.downloader -d /usr/share/nltk_data \
    stopwords \
    wordnet \
    punkt \
    punkt_tab \
    averaged_perceptron_tagger \
    averaged_perceptron_tagger_eng \
    omw-1.4

# Make sure nltk can find the corpus
ENV NLTK_DATA=/usr/share/nltk_data

ENV PYTHONPATH=/app

# Copy the rest of the backend code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
