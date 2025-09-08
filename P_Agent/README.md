# 📊 Statistics Calculator Agent

A professional statistics calculator agent with web interface and A2A (Agent-to-Agent) communication capabilities.

## 🚀 Quick Start

### Web Interface
```bash
python3 web_server.py
```
Opens a beautiful web interface at: http://localhost:5004

## 📊 Features

- **Mean** - Calculate arithmetic average
- **Median** - Find middle value  
- **Mode** - Find most frequent value
- **Standard Deviation** - Measure data spread
- **Range** - Difference between max and min
- **Summary Statistics** - All statistics at once

## 🌐 Web Interface

The web interface provides:
- Beautiful, responsive design
- Sample data for quick testing
- Real-time calculations
- Detailed results with explanations
- Mobile-friendly interface

## 🤖 A2A Communication

Your agent is ready for communication with other agents:
- **Health Check**: http://localhost:5004/health
- **API Endpoint**: http://localhost:5004/stats
- **Message Endpoint**: http://localhost:5004/message

## 📁 Project Structure

```
A2A_grptask/
├── statistics_agent.py      # Core statistics calculations
├── web_server.py           # Flask web server
├── templates/
│   └── index.html         # Web interface
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container setup
├── .gitignore           # Git ignore rules
├── .env.example         # Environment variables template
└── README.md            # This file
```

## 🛠️ Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Start the server
python3 web_server.py
```

## 🎯 Usage Examples

### Web Interface
1. Run: `python3 web_server.py`
2. Open: http://localhost:5004
3. Enter numbers: `10, 20, 30, 40, 50`
4. Click "Mean" → Result: `30.0`

### API Usage
```bash
curl -X POST http://localhost:5004/stats \
  -H "Content-Type: application/json" \
  -d '{"operation": "mean", "data": {"numbers": [10, 20, 30]}}'
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker
docker build -t statistics-agent .
docker run -p 5004:5004 statistics-agent
```

## 🔧 Configuration

Edit `.env` file to configure:
- Port settings
- Agent identification
- A2A communication settings
- Other agent endpoints

## 🤝 A2A Setup

1. Share your agent details with friends
2. Update `.env` with other agent URLs
3. Test communication with other agents

## 📋 Requirements

- Python 3.8+
- Flask 2.3.3
- Flask-CORS 4.0.0
- requests 2.31.0
- python-dotenv 1.0.0

## 🎉 Ready to Use!

Your statistics agent is production-ready with:
- ✅ Web interface
- ✅ A2A communication
- ✅ All statistics operations
- ✅ Docker support
- ✅ Professional code structure

Perfect for team collaboration and code reviews! 🚀