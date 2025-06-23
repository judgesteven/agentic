#!/usr/bin/env python3
"""
Mobile-friendly web interface for the agentic AI system.
Vercel-compatible version with minimal dependencies.
"""

import json
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'agentic-ai-secret-key-2024'

# Global agent instance
agent = None
agent_lock = threading.Lock()


def initialize_agent():
    """Initialize the agent."""
    global agent
    try:
        agent = MockAgent()
        print("🤖 Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        agent = None


class MockAgent:
    """Mock agent for demo purposes without requiring heavy dependencies."""
    
    def __init__(self):
        self.agent_name = "Agentic AI Assistant"
        self.conversation_id = None
        self.memory = []
        self.tools = ["web_search", "file_operations", "code_execution"]
    
    def start_conversation(self):
        """Start a new conversation."""
        import uuid
        self.conversation_id = str(uuid.uuid4())
        return self.conversation_id
    
    def process_message(self, message: str, use_tools: bool = True):
        """Process a user message and return a response."""
        # Add to memory
        self.memory.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate mock response based on message content
        response = self._generate_mock_response(message)
        
        # Add response to memory
        self.memory.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_mock_response(self, message: str) -> str:
        """Generate a mock response based on the message."""
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! I'm your Agentic AI assistant. I'm here to help you with various tasks like searching for information, managing files, and planning complex tasks. What would you like to do today?"
        
        elif "search" in message_lower or "find" in message_lower or "information" in message_lower:
            return "I can help you search for information! I have access to web search capabilities. What would you like me to search for?"
        
        elif "weather" in message_lower:
            return "I can help you get weather information! I would use my API tools to fetch current weather data for your location. What city would you like weather information for?"
        
        elif "file" in message_lower or "organize" in message_lower:
            return "I can help you with file operations! I can read, write, create, and organize files. What specific file task would you like me to help with?"
        
        elif "task" in message_lower or "plan" in message_lower:
            return "I can help you plan and execute tasks! I can break down complex goals into manageable steps and track their progress. What task would you like me to help you plan?"
        
        elif "thank" in message_lower:
            return "You're welcome! I'm here to help. Is there anything else you'd like assistance with?"
        
        elif "capabilities" in message_lower or "what can you do" in message_lower:
            return """I'm an Agentic AI with several capabilities:

🔍 **Web Search**: I can search the internet for information
📁 **File Operations**: I can read, write, and organize files
💻 **Code Execution**: I can run Python code safely
📋 **Task Planning**: I can break down complex tasks into steps
🧠 **Memory**: I remember our conversations and learn from interactions
🛠️ **Tool Usage**: I can use various tools to accomplish tasks

What would you like me to help you with?"""
        
        else:
            return "I understand you said: '" + message + "'. I'm here to help with various tasks including web searches, file operations, code execution, and task planning. What would you like me to assist you with?"
    
    def plan_task(self, goal: str):
        """Plan a task."""
        import uuid
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "id": task_id,
            "title": goal,
            "description": f"Task to achieve: {goal}",
            "status": "pending",
            "subtasks": [
                {"id": f"{task_id}_1", "title": "Analyze requirements", "status": "pending"},
                {"id": f"{task_id}_2", "title": "Execute main task", "status": "pending"},
                {"id": f"{task_id}_3", "title": "Verify results", "status": "pending"}
            ]
        }
    
    def execute_task(self, task):
        """Execute a task."""
        # Simulate task execution
        import time
        time.sleep(2)
        
        return {
            "success": True,
            "data": {"message": f"Task '{task['title']}' completed successfully"},
            "execution_time": 2.0
        }
    
    def get_status(self):
        """Get agent status."""
        return {
            "agent_name": self.agent_name,
            "conversation_id": self.conversation_id,
            "memory_size": len(self.memory),
            "available_tools": self.tools,
            "current_task": None,
            "task_history_count": 0
        }


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Process message with agent
        with agent_lock:
            if agent is None:
                return jsonify({'error': 'Agent not initialized'}), 500
            
            response = agent.process_message(message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status')
def status():
    """Get agent status."""
    with agent_lock:
        if agent is None:
            return jsonify({'error': 'Agent not initialized'}), 500
        
        return jsonify(agent.get_status())


@app.route('/api/task', methods=['POST'])
def create_task():
    """Create and execute a task."""
    try:
        data = request.get_json()
        goal = data.get('goal', '').strip()
        
        if not goal:
            return jsonify({'error': 'Task goal is required'}), 400
        
        with agent_lock:
            if agent is None:
                return jsonify({'error': 'Agent not initialized'}), 500
            
            task = agent.plan_task(goal)
            result = agent.execute_task(task)
        
        return jsonify({
            'task': task,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory')
def get_memory():
    """Get conversation memory."""
    with agent_lock:
        if agent is None:
            return jsonify({'error': 'Agent not initialized'}), 500
        
        return jsonify({
            'memory': agent.memory,
            'count': len(agent.memory)
        })


# Initialize agent when module is imported
initialize_agent()


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run the web interface
    print("🌐 Starting Agentic AI Web Interface...")
    print("📱 Mobile-friendly interface available at: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True) 