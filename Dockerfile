# Use the official lightweight Python 3.13 image
FROM python:3.13-slim

# Install uv directly from the official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency management files first
# (This allows Docker to cache the installation step if dependencies haven't changed)
COPY pyproject.toml .

# Install the dependencies using uv
# Note: if you have a uv.lock file, add it to the COPY command above
RUN uv sync

# Copy the rest of the application code and the SQLite database
COPY src/ ./src/
COPY data/ ./data/
COPY app.py .

# Expose Streamlit's default port
EXPOSE 8501

# Configure Streamlit to run headlessly and listen on all network interfaces
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Command to start the Streamlit application
CMD ["uv", "run", "streamlit", "run", "app.py"]