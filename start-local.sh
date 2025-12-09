#!/bin/bash

# Adamani AI RAG - Local Development Startup Script
# This script starts all services needed for local development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Adamani AI RAG - Local Development    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Check if Ollama is running
echo -e "${YELLOW}[1/5] Checking Ollama...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
else
    echo -e "${RED}✗ Ollama is not running${NC}"
    echo -e "${YELLOW}Starting Ollama...${NC}"
    ollama serve > /dev/null 2>&1 &
    sleep 3
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start Ollama. Please install it from https://ollama.com${NC}"
        exit 1
    fi
fi

# Check if llama3 model is available
echo -e "${YELLOW}[2/5] Checking LLM model...${NC}"
if ollama list | grep -q "llama3"; then
    echo -e "${GREEN}✓ llama3 model is available${NC}"
else
    echo -e "${YELLOW}⚠ llama3 model not found. Pulling now (this may take a few minutes)...${NC}"
    ollama pull llama3
    echo -e "${GREEN}✓ llama3 model downloaded${NC}"
fi

# Check if PostgreSQL is running
echo -e "${YELLOW}[3/5] Checking PostgreSQL...${NC}"
if pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not running${NC}"
    echo "Please start PostgreSQL:"
    echo "  macOS: brew services start postgresql"
    echo "  Linux: sudo systemctl start postgresql"
    exit 1
fi

# Check if .env exists
echo -e "${YELLOW}[4/5] Checking configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from template...${NC}"
    cp .env.example .env
    # Generate a random JWT secret
    if command -v openssl &> /dev/null; then
        JWT_SECRET=$(openssl rand -hex 32)
        sed -i.bak "s/your-secret-key-here-generate-with-openssl-rand-hex-32/$JWT_SECRET/" .env
        rm .env.bak 2>/dev/null || true
    fi
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}Please update DATABASE_URL in .env with your PostgreSQL credentials${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Start backend
echo -e "${YELLOW}[5/5] Starting services...${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${BLUE}Backend starting at: http://localhost:8000${NC}"
echo -e "${BLUE}API Docs available at: http://localhost:8000/docs${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Note: Start the frontend in another terminal:${NC}"
echo -e "  cd frontend && npm run dev"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop the backend${NC}"
echo ""

# Activate poetry shell and start backend
poetry run uvicorn src.adamani_ai_rag.api.app:app --reload --host 0.0.0.0 --port 8000
