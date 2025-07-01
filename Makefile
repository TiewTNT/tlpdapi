build:
	cd frontend && npm run build && cd ..

run:
	cd backend && python3 run.py && cd ..

dev:
	cd frontend && npm run build && cd ../backend/app && python3 -m uvicorn app:app