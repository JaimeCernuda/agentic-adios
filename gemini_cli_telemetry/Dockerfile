FROM node:20-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    build-essential \
    ca-certificates \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager) as root
RUN pip3 install uv

# Install Gemini CLI globally
RUN npm install -g @google/gemini-cli

# Create non-root user with sudo privileges
RUN useradd -m -s /bin/bash gemini && \
    echo "gemini ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    usermod -aG sudo gemini

# Switch to non-root user
USER gemini
WORKDIR /home/gemini

# Install uv for gemini user
RUN pip3 install --user uv
ENV PATH="/home/gemini/.local/bin:$PATH"

# Clone and install ADIOS MCP
RUN git clone https://github.com/iowarp/scientific-mcps.git && \
    cd scientific-mcps/Adios && \
    uv sync

# Create workspace and .gemini directories
RUN mkdir -p /home/gemini/workspace /home/gemini/.gemini

# Copy and set up Gemini CLI configuration
COPY --chown=gemini:gemini settings.json.template /home/gemini/.gemini/settings.json

# Set workspace as working directory
WORKDIR /home/gemini/workspace

# Environment variables for telemetry
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
ENV OTEL_EXPORTER_OTLP_PROTOCOL=grpc
ENV OTEL_LOG_LEVEL=info
ENV NODE_ENV=development

# Default command with telemetry enabled
CMD ["node", "/usr/local/lib/node_modules/@google/gemini-cli/dist/index.js", "--telemetry", "--telemetry-target", "local"]