FROM ubuntu:22.04

# Install dependencies including Python for uv
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    git \
    python3 \
    python3-pip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Gemini CLI
RUN npm install -g @google/gemini-cli

# Clone and set up scientific-mcps (includes ADIOS MCP)
WORKDIR /root
RUN git clone https://github.com/iowarp/scientific-mcps.git

# Set up the MCP with uv
WORKDIR /root/scientific-mcps
RUN uv sync

# Create workspace directory
RUN mkdir -p /workspace

# Create Gemini configuration directory
RUN mkdir -p /root/.config/gemini

# Create a script to configure Gemini with MCP support
RUN echo '#!/bin/bash\n\
if [ -z "$GEMINI_API_KEY" ]; then\n\
    echo "Error: GEMINI_API_KEY environment variable is not set"\n\
    echo "Please set it when running the container: -e GEMINI_API_KEY=your-key"\n\
    exit 1\n\
fi\n\
\n\
# Set the API key as environment variable for Gemini CLI\n\
export GEMINI_API_KEY="$GEMINI_API_KEY"\n\
\n\
# Start Gemini CLI\n\
echo "Starting Gemini CLI..."\n\
gemini' > /usr/local/bin/start-gemini.sh && \
    chmod +x /usr/local/bin/start-gemini.sh

WORKDIR /workspace

# Default command
CMD ["/usr/local/bin/start-gemini.sh"]