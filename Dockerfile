# Build stage for CSS
FROM node:18-alpine AS css-builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tailwind.config.js ./

# Install dependencies
RUN npm ci --only=production && npm ci --only=dev

# Copy CSS source files
COPY app/static/css/input.css ./app/static/css/
COPY app/templates ./app/templates

# Build CSS
RUN npm run build-css-prod

# Production stage
FROM python:3.11-slim AS production

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built CSS from build stage
COPY --from=css-builder /app/app/static/css/app.css ./app/static/css/

# Create necessary directories
RUN mkdir -p instance static/uploads

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]