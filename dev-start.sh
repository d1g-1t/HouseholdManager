#!/bin/bash
# Development startup script

set -e

echo "🚀 Starting HouseholdManager development environment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run commands in new terminal tabs (works on most Unix systems)
run_in_new_tab() {
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --tab -- bash -c "$1; exec bash"
    elif command -v konsole &> /dev/null; then
        konsole --new-tab -e bash -c "$1; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -e "$1; exec bash" &
    else
        echo "Please run this command manually in a new terminal:"
        echo "$1"
    fi
}

# Start Django development server
echo -e "${BLUE}Starting Django development server...${NC}"
poetry run python manage.py runserver &
DJANGO_PID=$!

# Give Django time to start
sleep 2

# Start Celery worker
echo -e "${BLUE}Starting Celery worker...${NC}"
run_in_new_tab "poetry run celery -A household_manager worker -l info -Q default,ocr,ml,notifications -c 4"

# Start Celery beat
echo -e "${BLUE}Starting Celery beat...${NC}"
run_in_new_tab "poetry run celery -A household_manager beat -l info"

# Start Celery flower (monitoring)
echo -e "${BLUE}Starting Celery Flower...${NC}"
run_in_new_tab "poetry run celery -A household_manager flower --port=5555"

echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "📱 Services available at:"
echo "   - Django API: http://localhost:8000/api/docs"
echo "   - Admin Panel: http://localhost:8000/admin"
echo "   - Celery Flower: http://localhost:5555"
echo ""
echo "Press Ctrl+C to stop Django server..."
echo ""

# Wait for Django to finish
wait $DJANGO_PID
