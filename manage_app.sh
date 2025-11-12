#!/bin/bash

# AEO Monitor Management Script
# Handles starting, stopping, and restarting the Streamlit app with proper cleanup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
APP_FILE="$SCRIPT_DIR/app.py"
PID_FILE="$SCRIPT_DIR/.streamlit.pid"
LOG_FILE="$SCRIPT_DIR/streamlit.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if app is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the app
start_app() {
    if is_running; then
        echo -e "${YELLOW}App is already running (PID: $(cat $PID_FILE))${NC}"
        return 1
    fi

    echo -e "${GREEN}Starting AEO Monitor...${NC}"
    
    # Activate virtual environment and start Streamlit in background
    cd "$SCRIPT_DIR"
    source "$VENV_PATH/bin/activate"
    
    nohup streamlit run "$APP_FILE" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 2
    
    if is_running; then
        echo -e "${GREEN}✓ App started successfully (PID: $(cat $PID_FILE))${NC}"
        echo -e "${GREEN}✓ Log file: $LOG_FILE${NC}"
        echo -e "${GREEN}✓ Check http://localhost:8501${NC}"
    else
        echo -e "${RED}✗ Failed to start app. Check $LOG_FILE for errors${NC}"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the app
stop_app() {
    if ! is_running; then
        echo -e "${YELLOW}App is not running${NC}"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    echo -e "${YELLOW}Stopping AEO Monitor (PID: $PID)...${NC}"
    
    # Send SIGTERM for graceful shutdown
    kill -TERM $PID 2>/dev/null
    
    # Wait up to 10 seconds for graceful shutdown
    for i in {1..10}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓ App stopped gracefully${NC}"
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
    done
    
    # Force kill if still running
    echo -e "${YELLOW}Forcing shutdown...${NC}"
    kill -9 $PID 2>/dev/null
    rm -f "$PID_FILE"
    echo -e "${GREEN}✓ App stopped (forced)${NC}"
}

# Function to restart the app
restart_app() {
    echo -e "${YELLOW}Restarting AEO Monitor...${NC}"
    stop_app
    sleep 2
    start_app
}

# Function to show status
show_status() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}✓ App is running (PID: $PID)${NC}"
        echo -e "${GREEN}  Memory usage: $(ps -o rss= -p $PID | awk '{print int($1/1024)" MB"}')${NC}"
        echo -e "${GREEN}  CPU usage: $(ps -o %cpu= -p $PID)%${NC}"
    else
        echo -e "${RED}✗ App is not running${NC}"
    fi
}

# Function to view logs
view_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}No log file found${NC}"
    fi
}

# Function to cleanup all processes
cleanup_all() {
    echo -e "${YELLOW}Cleaning up all Streamlit processes...${NC}"
    
    # Stop via PID file first
    stop_app
    
    # Kill any remaining streamlit processes
    pkill -9 -f "streamlit run $APP_FILE"
    
    # Kill any Python processes on Streamlit ports
    for port in 8501 8502 8503 8504 8505; do
        PID=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$PID" ]; then
            echo -e "${YELLOW}Killing process on port $port (PID: $PID)${NC}"
            kill -9 $PID 2>/dev/null
        fi
    done
    
    rm -f "$PID_FILE"
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Main script logic
case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        show_status
        ;;
    logs)
        view_logs
        ;;
    cleanup)
        cleanup_all
        ;;
    *)
        echo "AEO Monitor Management Script"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|cleanup}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the Streamlit app"
        echo "  stop     - Stop the Streamlit app (graceful shutdown)"
        echo "  restart  - Restart the Streamlit app"
        echo "  status   - Show app status"
        echo "  logs     - View app logs (tail -f)"
        echo "  cleanup  - Force cleanup all processes and ports"
        echo ""
        exit 1
        ;;
esac

exit 0

