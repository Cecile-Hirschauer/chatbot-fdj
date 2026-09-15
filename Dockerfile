# Use the official lightweight Python 3.13 image
FROM python:3.13-slim

# Install uv directly from the official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory inside the container
WORKDIR /app

# Copy dependency manifests first so Docker can cache the install layer
COPY pyproject.toml uv.lock ./
COPY README.md .

# Install only external dependencies (skip building the local package).
# This layer is cached as long as pyproject.toml / uv.lock don't change.
RUN uv sync --frozen --no-install-project

# Copy the application source, data, and entry point
COPY src/ ./src/
COPY data/ ./data/
COPY app.py .

# Install the local package now that src/ is present
RUN uv sync --frozen

# Expose Streamlit's default port
EXPOSE 8501

# Configure Streamlit to run headlessly and listen on all network interfaces
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Command to start the Streamlit application
CMD ["uv", "run", "streamlit", "run", "app.py"]