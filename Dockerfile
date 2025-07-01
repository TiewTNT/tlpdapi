# --- Frontend Build Stage ---
FROM node:20 AS frontend
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Backend Stage ---
FROM texlive/texlive:latest

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 python3-pip unzip poppler-utils imagemagick pandoc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend and related files
COPY backend/ ./backend/
COPY backend/run.py ./
# Copy your Makefile if still needed
COPY Makefile ./

# Copy built frontend into appropriate directory
COPY --from=frontend /app/frontend/build ./frontend/build

# Install Python deps
RUN python3 -m pip install --break-system-packages --no-cache-dir -r backend/requirements.txt

EXPOSE 8000

CMD make run
