FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /composable_app

# Copy project files
COPY pyproject.toml .
COPY requirements.txt .

# Install Python dependencies using uv
RUN uv pip install --system --no-cache -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN useradd -m appuser

# Set permissions and create log files
RUN touch *.log 2>/dev/null || true && \
    chown -R appuser:appuser /composable_app

# Set environment variables
ENV PYTHONPATH=/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Start application
CMD ["python3", "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]