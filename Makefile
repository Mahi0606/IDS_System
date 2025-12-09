.PHONY: help install-backend install-frontend dev-backend dev-frontend dev setup

help:
	@echo "IDS System - Makefile Commands"
	@echo ""
	@echo "  make setup              - Set up both backend and frontend"
	@echo "  make install-backend    - Install backend dependencies"
	@echo "  make install-frontend  - Install frontend dependencies"
	@echo "  make dev-backend        - Start backend server"
	@echo "  make dev-frontend       - Start frontend dev server"
	@echo "  make dev                - Start both backend and frontend"

setup:
	@echo "Setting up IDS System..."
	@cd backend && python3 -m venv venv || true
	@cd backend && source venv/bin/activate && pip install -r requirements.txt
	@cd frontend && npm install
	@echo "Setup complete!"

install-backend:
	@cd backend && python3 -m venv venv || true
	@cd backend && source venv/bin/activate && pip install -r requirements.txt

install-frontend:
	@cd frontend && npm install

dev-backend:
	@cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@cd frontend && npm run dev

dev:
	@echo "Starting both backend and frontend..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@make -j2 dev-backend dev-frontend

