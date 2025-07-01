# --------- FRONTEND BUILD STAGE ---------
FROM node:20 AS frontend

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# --------- BACKEND STAGE ---------
FROM texlive/texlive:latest AS backend

# System dependencies for Python and PDF tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    unzip \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY backend/requirements.txt ./backend/
RUN python3 -m pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend ./backend

# Copy built frontend
COPY --from=frontend /app/frontend/build ./frontend/build

EXPOSE 8000

RUN make build && make run
