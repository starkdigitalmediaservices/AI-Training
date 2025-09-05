# 🚀 Quick Start Guide - A2A Calculator Agent

## 📋 Prerequisites
- Python 3.8+ installed
- Virtual environment support
- Network access to teammates' agents

## 🏃‍♂️ Quick Start (5 minutes)

### Step 1: Navigate to Project Directory
```bash
cd "/home/stark/Desktop/A2A Calc Agent "
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```
*You should see `(venv)` in your terminal prompt*

### Step 3: Start the Calculator Agent
```bash
nohup python calculator_agent_network.py > server.log 2>&1 &
```
*This starts the server in the background*

### Step 4: Verify Server is Running
```bash
curl http://localhost:5001/health
```
*Should return JSON with status "online"*

### Step 5: Configure Agent URLs
```bash
curl -X PUT http://localhost:5001/config/agents \
  -H "Content-Type: application/json" \
  -d '{
    "unit_url": "http://192.168.0.68:5002",
    "statistics_url": "http://192.168.0.99:5004"
  }'
```

### Step 6: Test Connectivity
```bash
curl -X POST http://localhost:5001/config/test
```
*Should show all agents as "ok": true*

### Step 7: Open Web UI
Open your browser and go to: **http://localhost:5001/**

## 🎯 Using the Web UI

### Agent URLs Section
1. **Calculator URL**: `http://192.168.0.104:5001` (auto-filled)
2. **Unit Converter URL**: `http://192.168.0.68:5002`
3. **Statistics URL**: `http://192.168.0.99:5004`
4. Click **"Save"** then **"Test"** - all should show green checkmarks

### Pipeline Section
1. **Calculator Operation**: Choose from:
   - Addition (+)
   - Subtraction (-)
   - Multiplication (×)
   - Division (÷)
   - Power (^)
   - Square Root (√)

2. **Numbers**: Enter based on operation:
   - Multiple operations: `10,20,30`
   - Power: `2,3` (base,exponent)
   - Square root: `16` (single number)

3. **Unit Conversion**: Select from dropdowns:
   - **Length**: meter, cm, mm, feet, inch, km, yard, mile
   - **Weight**: kg, gram, pound, ounce

4. **Statistics**: 
   - **Operation**: Choose from Mean, Median, Mode, Standard Deviation, Range
   - **Extra Numbers**: Optional CSV input (e.g., `12.5,8.0,15.2`) to include with converted value

5. Click **"Run Pipeline"** to execute the full chain

## 🔧 Troubleshooting

### If Server Won't Start
```bash
# Check if port is already in use
lsof -i :5001

# Kill existing process
pkill -f calculator_agent_network.py

# Try starting again
python calculator_agent_network.py
```

### If Agents Show "FAIL"
```bash
# Test individual agents
curl http://192.168.0.68:5002/health  # Unit Converter
curl http://192.168.0.99:5004/health  # Statistics

# Reconfigure if needed
curl -X PUT http://localhost:5001/config/agents \
  -H "Content-Type: application/json" \
  -d '{"unit_url": "http://192.168.0.68:5002", "statistics_url": "http://192.168.0.99:5004"}'
```

### Check Server Logs
```bash
tail -f server.log
```

## 📊 Example Workflows

### Example 1: Math → Length → Statistics
- **Calculator**: `multiply` with `5,4` → `20`
- **Unit**: `meter` → `feet` → `65.62 feet`
- **Stats**: `mean` → `65.62`

### Example 2: Power → Weight → Statistics
- **Calculator**: `power` with `3,2` → `9`
- **Unit**: `kilogram` → `pound` → `19.84 pounds`
- **Stats**: `median` → `19.84`

### Example 3: Custom Statistics with Extra Numbers
- **Calculator**: `multiply` with `5,4` → `20`
- **Unit**: `meter` → `feet` → `65.62 feet`
- **Stats**: `mean` with extra numbers `10.5,25.0,30.8` → `mean of [65.62, 10.5, 25.0, 30.8] = 32.98`

## 🛑 Stopping the Agent
```bash
# Find and kill the process
pkill -f calculator_agent_network.py

# Or find the process ID and kill it
ps aux | grep calculator_agent_network.py
kill <PID>
```

## 📁 Key Files
- `calculator_agent_network.py` - Main Flask server
- `templates/index.html` - Web UI
- `static/app.js` - Frontend logic
- `requirements.txt` - Python dependencies
- `server.log` - Server logs
- `QUICK_START.md` - This guide

## 🌐 Network Information
- **Your Calculator Agent**: `192.168.0.104:5001`
- **Unit Converter Agent**: `192.168.0.68:5002`
- **Statistics Agent**: `192.168.0.99:5004`

## 💡 Tips
1. Always activate the virtual environment first
2. Check server logs if something isn't working
3. Test connectivity before running pipelines
4. The UI will show per-agent steps and final results
5. All agents communicate via A2A (Agent-to-Agent) protocol

---
**Ready to go!** 🎯 Just follow these steps and you'll be running your A2A calculator agent in minutes!
