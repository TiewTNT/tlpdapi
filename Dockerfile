# --------- FRONTEND BUILD STAGE ---------
FROM node:20 AS frontend

WORKDIR /frontend/

RUN npm install

RUN npm run build


# --------- BACKEND STAGE ---------
FROM texlive/texlive:latest

WORKDIR /

# System dependencies for Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip poppler

# Python requirements
RUN pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8000

CMD ["python3", "backend/run.py"]
