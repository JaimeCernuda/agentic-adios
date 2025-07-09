FROM ubuntu:22.04

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

# Install Node.js 18+ (required for Claude Code)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Install uv (Python package manager)
RUN pip3 install uv

# Create claude-user with sudo privileges
RUN useradd -m -s /bin/bash claude-user && \
    echo "claude-user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    usermod -aG sudo claude-user

# Switch to claude-user
USER claude-user
WORKDIR /home/claude-user

# Install Claude Code
RUN npm install -g @anthropic-ai/claude-code

# Clone and build ADIOS MCP
RUN git clone https://github.com/iowarp/scientific-mcps.git && \
    cd scientific-mcps && \
    uv sync

# Create workspace directory
RUN mkdir -p /home/claude-user/workspace

# Switch to workspace and add MCP
WORKDIR /home/claude-user/workspace
RUN claude mcp add /home/claude-user/scientific-mcps/adios-server

# Set environment variables for telemetry
ENV CLAUDE_CODE_ENABLE_TELEMETRY=1
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
ENV OTEL_EXPORTER_OTLP_PROTOCOL=grpc

# Keep container running
CMD ["tail", "-f", "/dev/null"]