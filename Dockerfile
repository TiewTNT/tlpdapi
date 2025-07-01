# --------- FRONTEND BUILD STAGE ---------
FROM node:20 AS frontend

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# --------- BACKEND STAGE ---------
FROM texlive/texlive:latest AS backend

# System dependencies for Python & unzip
RUN apt-get update && \
    apt-get install -y python3 python3-pip poppler && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python requirements
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend ./backend

# Copy compiled frontend build
COPY --from=frontend /app/frontend/build ./frontend/build

EXPOSE 8000

CMD ["python3", "backend/run.py"]
