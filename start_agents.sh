#!/bin/bash

# Multi-Agent System Startup Script
# Starts all three agents on a single server

echo "🚀 Starting Multi-Agent System on Single Server"
echo "=============================================="

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Function to start an agent
start_agent() {
    local agent_name=$1
    local script_path=$2
    local port=$3
    local venv_path=$4
    
    echo "🚀 Starting $agent_name agent on port $port..."
    
    if [ ! -f "$script_path" ]; then
        echo "❌ Script not found: $script_path"
        return 1
    fi
    
    if [ ! -f "$venv_path/bin/python" ]; then
        echo "❌ Virtual environment not found: $venv_path"
        return 1
    fi
    
    # Start the agent in background
    nohup "$venv_path/bin/python" "$script_path" > "logs/${agent_name}_agent.log" 2>&1 &
    local pid=$!
    echo $pid > "logs/${agent_name}_agent.pid"
    
    # Wait a moment for startup
    sleep 3
    
    # Check if process is still running
    if kill -0 $pid 2>/dev/null; then
        echo "✅ $agent_name agent started successfully (PID: $pid)"
        return 0
    else
        echo "❌ $agent_name agent failed to start"
        return 1
    fi
}

# Function to stop all agents
stop_agents() {
    echo "🛑 Stopping all agents..."
    
    for agent in calculator unit_converter statistics; do
        if [ -f "logs/${agent}_agent.pid" ]; then
            local pid=$(cat "logs/${agent}_agent.pid")
            if kill -0 $pid 2>/dev/null; then
                echo "🛑 Stopping $agent agent (PID: $pid)..."
                kill $pid
                sleep 2
                if kill -0 $pid 2>/dev/null; then
                    echo "🔨 Force killing $agent agent..."
                    kill -9 $pid
                fi
                echo "✅ $agent agent stopped"
            fi
            rm -f "logs/${agent}_agent.pid"
        fi
    done
}

# Function to check agent health
check_health() {
    local agent_name=$1
    local port=$2
    
    echo "🔍 Checking $agent_name agent health..."
    if curl -s "http://localhost:$port/health" > /dev/null; then
        echo "✅ $agent_name agent is healthy"
        return 0
    else
        echo "❌ $agent_name agent health check failed"
        return 1
    fi
}

# Create logs directory
mkdir -p logs

# Handle command line arguments
case "${1:-start}" in
    "start")
        # Check if ports are available
        echo "🔍 Checking port availability..."
        check_port 5001 || exit 1
        check_port 5002 || exit 1
        check_port 5003 || exit 1
        
        # Start agents in order
        echo ""
        echo "🚀 Starting agents..."
        
        start_agent "calculator" "calculator_agent_network.py" 5001 "venv" || exit 1
        sleep 2
        
        start_agent "unit_converter" "Y_Agent/unit_converter_network.py" 5002 "venv" || exit 1
        sleep 2
        
        start_agent "statistics" "P_Agent/web_server.py" 5003 "P_Agent/venv" || exit 1
        sleep 3
        
        # Check health
        echo ""
        echo "🔍 Checking agent health..."
        check_health "calculator" 5001 || exit 1
        check_health "unit_converter" 5002 || exit 1
        check_health "statistics" 5003 || exit 1
        
        echo ""
        echo "🎉 All agents started successfully!"
        echo ""
        echo "📋 Agent URLs:"
        echo "  🧮 Calculator: http://localhost:5001"
        echo "  🔄 Unit Converter: http://localhost:5002"
        echo "  📊 Statistics: http://localhost:5003"
        echo ""
        echo "🌐 Web Interfaces:"
        echo "  🧮 Calculator UI: http://localhost:5001/"
        echo "  🔄 Unit Converter UI: http://localhost:5002/"
        echo "  📊 Statistics UI: http://localhost:5003/"
        echo ""
        echo "🔧 Test the system:"
        echo "  python pipeline_orchestrator.py --numbers 10,20,30 --from-unit meter --to-unit feet --stats-op mean"
        echo ""
        echo "📝 Logs are in the 'logs/' directory"
        echo "🛑 To stop all agents: ./start_agents.sh stop"
        ;;
    
    "stop")
        stop_agents
        ;;
    
    "restart")
        stop_agents
        sleep 2
        $0 start
        ;;
    
    "status")
        echo "🔍 Checking agent status..."
        for agent in calculator unit_converter statistics; do
            if [ -f "logs/${agent}_agent.pid" ]; then
                local pid=$(cat "logs/${agent}_agent.pid")
                if kill -0 $pid 2>/dev/null; then
                    echo "✅ $agent agent is running (PID: $pid)"
                else
                    echo "❌ $agent agent is not running"
                fi
            else
                echo "❌ $agent agent is not running"
            fi
        done
        ;;
    
    "health")
        echo "🔍 Checking agent health..."
        check_health "calculator" 5001
        check_health "unit_converter" 5002
        check_health "statistics" 5003
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|health}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all agents (default)"
        echo "  stop    - Stop all agents"
        echo "  restart - Restart all agents"
        echo "  status  - Check if agents are running"
        echo "  health  - Check agent health endpoints"
        exit 1
        ;;
esac
