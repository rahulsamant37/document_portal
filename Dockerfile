# Use Official Python Image
FROM python:3.10-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Setting up the Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the application into the container.
COPY . /app

# Setting workdir
WORKDIR /app

# Install the application dependencies.
RUN uv sync --frozen --no-cache

# Expose port 8000 (since you're mapping to 8000)
EXPOSE 8000

# Run the application.
CMD ["uv", "run", "fastapi", "run", "app.py", "--port", "8000", "--host", "0.0.0.0"]