# Use the existing Dockerfile in the subdirectory but set the context correctly
# This allows 'docker build .' from the workspace root to work.

FROM ghcr.io/meta-pytorch/openenv-base:latest

WORKDIR /app

# Copy the environment project
COPY . /app/env/

# Set workdir to the project root
WORKDIR /app/env

# Install dependencies
RUN if ! command -v uv >/dev/null 2>&1; then \
        curl -LsSf https://astral.sh/uv/install.sh | sh && \
        mv /root/.local/bin/uv /usr/local/bin/uv && \
        mv /root/.local/bin/uvx /usr/local/bin/uvx; \
    fi

RUN uv sync --frozen --no-editable

# Set environment
ENV PATH="/app/env/.venv/bin:$PATH"
ENV PYTHONPATH="/app/env:$PYTHONPATH"

# Expose port
EXPOSE 7860

# Start command
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
