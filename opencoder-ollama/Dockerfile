FROM node:20-slim

# Install required dependencies including Python for uv
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Install opencode globally
RUN npm install -g opencode-ai@latest

# Clone and set up scientific-mcps (includes ADIOS MCP)
WORKDIR /root
RUN git clone https://github.com/iowarp/scientific-mcps.git

# Set up the MCP with uv
WORKDIR /root/scientific-mcps
RUN uv sync

# Create workspace and config directories
RUN mkdir -p /workspace /root/.config/opencode

# Create OpenCode configuration file
RUN echo '{\n\
  "$schema": "https://opencode.ai/config.json",\n\
  "theme": "opencode",\n\
  "provider": {\n\
    "ollama": {\n\
      "npm": "@ai-sdk/openai-compatible",\n\
      "options": {\n\
        "baseURL": "http://ollama:11434"\n\
      },\n\
      "models": {\n\
        "llama3.1:8b": {\n\
          "name": "Llama 3.1 8B"\n\
        },\n\
        "llama3.1:70b": {\n\
          "name": "Llama 3.1 70B"\n\
        },\n\
        "codellama:latest": {\n\
          "name": "Code Llama"\n\
        },\n\
        "deepseek-coder:latest": {\n\
          "name": "DeepSeek Coder"\n\
        },\n\
        "qwen2.5-coder:latest": {\n\
          "name": "Qwen 2.5 Coder"\n\
        }\n\
      }\n\
    }\n\
  },\n\
  "model": "ollama/llama3.1:8b",\n\
  "mcp": {\n\
    "adios": {\n\
      "type": "local",\n\
      "command": ["uv", "run", "adios-mcp"],\n\
      "cwd": "/root/scientific-mcps"\n\
    }\n\
  },\n\
  "autoshare": false,\n\
  "autoupdate": true\n\
}' > /root/.config/opencode/opencode.json

# Set up environment
ENV OLLAMA_API_BASE=http://ollama:11434

# Default working directory
WORKDIR /workspace

# Default command
CMD ["opencode"]