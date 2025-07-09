#!/bin/bash

# Define supported models
SUPPORTED_MODELS=(
    "llama3.1:8b"
    "llama3.1:70b"
    "codellama:latest"
    "deepseek-coder:latest"
    "qwen2.5-coder:latest"
)

# Get the model from environment variable or use default
MODEL="${OLLAMA_MODEL:-llama3.1:8b}"

# Check if model is supported
is_supported=false
for supported in "${SUPPORTED_MODELS[@]}"; do
    if [[ "$MODEL" == "$supported" ]]; then
        is_supported=true
        break
    fi
done

if [[ "$is_supported" == false ]]; then
    echo "Error: Model '$MODEL' is not in the list of pre-configured models."
    echo "Supported models are:"
    for model in "${SUPPORTED_MODELS[@]}"; do
        echo "  - $model"
    done
    echo ""
    echo "To use a different model, you need to:"
    echo "1. Add it to the supported models list in the Dockerfile"
    echo "2. Rebuild the image"
    exit 1
fi

# Start Ollama
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until ollama list &>/dev/null; do
    sleep 1
done

# Pull the specified model
echo "Pulling model: $MODEL"
ollama pull "$MODEL"

# Keep Ollama running
wait $OLLAMA_PID