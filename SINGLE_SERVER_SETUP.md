# 🚀 Multi-Agent System - Single Server Setup

This guide will help you run all three agents (Calculator, Unit Converter, Statistics) on a single server with full A2A (Agent-to-Agent) communication.

## 📋 System Overview

The system consists of three Flask-based agents that communicate using a standardized A2A protocol:

- **🧮 Calculator Agent** (Port 5001): Handles mathematical operations
- **🔄 Unit Converter Agent** (Port 5002): Converts between different units
- **📊 Statistics Agent** (Port 5003): Performs statistical calculations

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Calculator    │    │ Unit Converter  │    │   Statistics    │
│   Agent         │◄──►│ Agent           │◄──►│ Agent           │
│   Port: 5001    │    │ Port: 5002      │    │ Port: 5003      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │   (Pipeline)    │
                    └─────────────────┘
```

## 🚀 Quick Start

### Method 1: Using the Shell Script (Recommended)

```bash
# Start all agents
./start_agents.sh start

# Check status
./start_agents.sh status

# Check health
./start_agents.sh health

# Stop all agents
./start_agents.sh stop

# Restart all agents
./start_agents.sh restart
```

### Method 2: Using Python Script

```bash
# Start all agents (interactive mode)
python3 start_all_agents.py

# Stop all agents
python3 start_all_agents.py --stop

# Check health
python3 start_all_agents.py --health
```

### Method 3: Manual Startup

```bash
# Terminal 1 - Calculator Agent
cd /home/stark/AI-Training
source venv/bin/activate
python3 calculator_agent_network.py

# Terminal 2 - Unit Converter Agent
cd /home/stark/AI-Training
source venv/bin/activate
python3 Y_Agent/unit_converter_network.py

# Terminal 3 - Statistics Agent
cd /home/stark/AI-Training/P_Agent
source venv/bin/activate
python3 web_server.py
```

## 🔧 Configuration

The system uses environment variables for configuration. A `.env` file has been created with localhost settings:

```bash
# Network Configuration for Math Agents - Single Server Setup
CALCULATOR_HOST=localhost
CALCULATOR_PORT=5001
UNIT_CONVERTER_HOST=localhost
UNIT_CONVERTER_PORT=5002
STATISTICS_HOST=localhost
STATISTICS_PORT=5003
```

## 🧪 Testing the System

### 1. Health Checks

```bash
# Check all agents are running
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
```

### 2. Individual Agent Testing

```bash
# Test Calculator Agent
curl -X POST http://localhost:5001/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "add", "data": {"numbers": [10, 20, 30]}}'

# Test Unit Converter Agent
curl -X POST http://localhost:5002/convert \
  -H "Content-Type: application/json" \
  -d '{"value": 10, "from_unit": "meter", "to_unit": "feet"}'

# Test Statistics Agent
curl -X POST http://localhost:5003/message \
  -H "Content-Type: application/json" \
  -d '{"sender": "test", "message": {"operation": "mean", "data": {"numbers": [10, 20, 30]}}}'
```

### 3. Pipeline Orchestrator Testing

```bash
# Basic pipeline test
python3 pipeline_orchestrator.py --numbers 10,20,30 --from-unit meter --to-unit feet --stats-op mean

# Different operations
python3 pipeline_orchestrator.py --numbers 5,4 --from-unit kilogram --to-unit pound --stats-op median

# Custom statistics with extra numbers
python3 pipeline_orchestrator.py --numbers 2,3 --from-unit meter --to-unit feet --stats-op mean --stats-list 10.5,25.0,30.8
```

## 🌐 Web Interfaces

Each agent provides a web interface:

- **🧮 Calculator UI**: http://localhost:5001/
- **🔄 Unit Converter UI**: http://localhost:5002/
- **📊 Statistics UI**: http://localhost:5003/

## 📊 Example Workflows

### Example 1: Math → Length → Statistics
```bash
python3 pipeline_orchestrator.py --numbers 10,20,30 --from-unit meter --to-unit feet --stats-op mean
```
**Result**: `10+20+30=60` → `60 meters = 196.85 feet` → `mean([196.85, 12.5, 8.0]) = 72.45`

### Example 2: Power → Weight → Statistics
```bash
python3 pipeline_orchestrator.py --numbers 3,2 --from-unit kilogram --to-unit pound --stats-op median
```
**Result**: `3+2=5` → `5 kg = 11.02 pounds` → `median([11.02, 12.5, 8.0]) = 11.02`

### Example 3: Custom Statistics
```bash
python3 pipeline_orchestrator.py --numbers 5,4 --from-unit meter --to-unit feet --stats-op mean --stats-list 10.5,25.0,30.8
```
**Result**: `5+4=9` → `9 meters = 29.53 feet` → `mean([29.53, 10.5, 25.0, 30.8]) = 23.96`

## 🔍 A2A Communication Protocol

All agents communicate using a standardized A2A protocol:

### Request Format
```json
{
  "sender": "<agent_or_client_name>",
  "correlation_id": "uuid-1234",
  "trace": ["calculator@192.168.1.10:5001"],
  "message": {
    "operation": "add",
    "data": {"numbers": [10,20,30]}
  }
}
```

### Response Format
```json
{
  "agent": "calculator_agent",
  "server_ip": "192.168.1.10",
  "response": {"result": 60, "success": true},
  "correlation_id": "uuid-1234",
  "trace": ["calculator@192.168.1.10:5001"],
  "timestamp": "2025-09-08T12:34:59.854105"
}
```

## 📁 File Structure

```
/home/stark/AI-Training/
├── .env                          # Environment configuration
├── start_agents.sh              # Shell script to start/stop agents
├── start_all_agents.py          # Python script to manage agents
├── pipeline_orchestrator.py     # Pipeline orchestrator
├── calculator_agent_network.py  # Calculator agent server
├── requirements.txt             # Python dependencies
├── logs/                        # Agent logs
│   ├── calculator_agent.log
│   ├── unit_converter_agent.log
│   └── statistics_agent.log
├── Y_Agent/                     # Unit Converter Agent
│   ├── unit_converter_network.py
│   ├── templates/
│   └── static/
└── P_Agent/                     # Statistics Agent
    ├── web_server.py
    ├── statistics_agent.py
    ├── templates/
    └── static/
```

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :5001

# Kill the process
pkill -f calculator_agent_network.py
```

### Agent Not Responding
```bash
# Check agent status
./start_agents.sh status

# Check logs
tail -f logs/calculator_agent.log
tail -f logs/unit_converter_agent.log
tail -f logs/statistics_agent.log
```

### Connection Issues
```bash
# Test individual endpoints
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health

# Restart all agents
./start_agents.sh restart
```

## 🎯 Key Features

- ✅ **Single Server Setup**: All agents run on localhost
- ✅ **A2A Communication**: Standardized inter-agent protocol
- ✅ **Health Monitoring**: Built-in health check endpoints
- ✅ **Web Interfaces**: User-friendly web UIs for each agent
- ✅ **Pipeline Orchestration**: Sequential workflow execution
- ✅ **Error Handling**: Robust error handling and fallbacks
- ✅ **Logging**: Comprehensive logging for debugging
- ✅ **Easy Management**: Simple start/stop scripts

## 🚀 Next Steps

1. **Test the Web Interfaces**: Open each agent's web UI in your browser
2. **Run Pipeline Tests**: Try different combinations of operations
3. **Monitor Logs**: Check the logs directory for detailed information
4. **Customize Operations**: Modify the agents to add new capabilities
5. **Scale Up**: Deploy agents on different servers for distributed setup

## 📞 Support

If you encounter any issues:

1. Check the logs in the `logs/` directory
2. Verify all agents are running: `./start_agents.sh status`
3. Test individual agents: `./start_agents.sh health`
4. Restart the system: `./start_agents.sh restart`

---

**🎉 Your multi-agent system is now running successfully on a single server!**
