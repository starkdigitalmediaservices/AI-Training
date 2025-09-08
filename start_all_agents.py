#!/usr/bin/env python3
"""
Start All Agents Script - Single Server Setup
Starts all three agents (Calculator, Unit Converter, Statistics) on localhost
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class AgentManager:
    def __init__(self):
        self.processes = {}
        self.base_dir = Path(__file__).parent.absolute()
        
        # Agent configurations
        self.agents = {
            'calculator': {
                'script': 'calculator_agent_network.py',
                'port': 5001,
                'cwd': self.base_dir,
                'venv': self.base_dir / 'venv'
            },
            'unit_converter': {
                'script': 'Y_Agent/unit_converter_network.py',
                'port': 5002,
                'cwd': self.base_dir,
                'venv': self.base_dir / 'venv'
            },
            'statistics': {
                'script': 'P_Agent/web_server.py',
                'port': 5003,
                'cwd': self.base_dir,
                'venv': self.base_dir / 'P_Agent' / 'venv'
            }
        }
    
    def start_agent(self, agent_name):
        """Start a single agent"""
        config = self.agents[agent_name]
        script_path = self.base_dir / config['script']
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False
        
        # Check if virtual environment exists
        venv_python = config['venv'] / 'bin' / 'python'
        if not venv_python.exists():
            print(f"❌ Virtual environment not found: {config['venv']}")
            return False
        
        print(f"🚀 Starting {agent_name} agent on port {config['port']}...")
        
        try:
            # Start the agent process
            process = subprocess.Popen(
                [str(venv_python), str(script_path)],
                cwd=str(config['cwd']),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes[agent_name] = process
            
            # Start a thread to monitor the output
            def monitor_output():
                for line in iter(process.stdout.readline, ''):
                    print(f"[{agent_name.upper()}] {line.rstrip()}")
            
            monitor_thread = threading.Thread(target=monitor_output, daemon=True)
            monitor_thread.start()
            
            # Give the agent time to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {agent_name} agent started successfully on port {config['port']}")
                return True
            else:
                print(f"❌ {agent_name} agent failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {agent_name} agent: {e}")
            return False
    
    def stop_agent(self, agent_name):
        """Stop a single agent"""
        if agent_name in self.processes:
            process = self.processes[agent_name]
            if process.poll() is None:  # Process is still running
                print(f"🛑 Stopping {agent_name} agent...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                print(f"✅ {agent_name} agent stopped")
            del self.processes[agent_name]
    
    def stop_all_agents(self):
        """Stop all running agents"""
        print("\n🛑 Stopping all agents...")
        for agent_name in list(self.processes.keys()):
            self.stop_agent(agent_name)
    
    def check_agent_health(self, agent_name):
        """Check if an agent is responding"""
        config = self.agents[agent_name]
        try:
            import requests
            response = requests.get(f"http://localhost:{config['port']}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {agent_name} agent is healthy")
                return True
            else:
                print(f"❌ {agent_name} agent health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {agent_name} agent health check failed: {e}")
            return False
    
    def start_all_agents(self):
        """Start all agents in sequence"""
        print("🚀 Starting Multi-Agent System on Single Server")
        print("=" * 50)
        
        # Start agents in order
        start_order = ['calculator', 'unit_converter', 'statistics']
        started_agents = []
        
        for agent_name in start_order:
            if self.start_agent(agent_name):
                started_agents.append(agent_name)
                time.sleep(3)  # Give time for agent to fully initialize
            else:
                print(f"❌ Failed to start {agent_name}, stopping all agents...")
                self.stop_all_agents()
                return False
        
        print("\n🔍 Checking agent health...")
        all_healthy = True
        for agent_name in started_agents:
            if not self.check_agent_health(agent_name):
                all_healthy = False
        
        if all_healthy:
            print("\n🎉 All agents started successfully!")
            print("\n📋 Agent URLs:")
            print(f"  🧮 Calculator: http://localhost:5001")
            print(f"  🔄 Unit Converter: http://localhost:5002")
            print(f"  📊 Statistics: http://localhost:5003")
            print("\n🌐 Web Interfaces:")
            print(f"  🧮 Calculator UI: http://localhost:5001/")
            print(f"  🔄 Unit Converter UI: http://localhost:5002/")
            print(f"  📊 Statistics UI: http://localhost:5003/")
            print("\n🔧 Test the system:")
            print(f"  python pipeline_orchestrator.py --numbers 10,20,30 --from-unit meter --to-unit feet --stats-op mean")
            return True
        else:
            print("\n❌ Some agents are not healthy, stopping all...")
            self.stop_all_agents()
            return False
    
    def run_interactive(self):
        """Run in interactive mode"""
        def signal_handler(signum, frame):
            print("\n🛑 Received interrupt signal, stopping all agents...")
            self.stop_all_agents()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if self.start_all_agents():
            print("\n⏳ Agents are running. Press Ctrl+C to stop all agents.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                self.stop_all_agents()

def main():
    manager = AgentManager()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--stop':
        # Stop all agents
        manager.stop_all_agents()
    elif len(sys.argv) > 1 and sys.argv[1] == '--health':
        # Check health of all agents
        for agent_name in manager.agents.keys():
            manager.check_agent_health(agent_name)
    else:
        # Start all agents
        manager.run_interactive()

if __name__ == '__main__':
    main()
