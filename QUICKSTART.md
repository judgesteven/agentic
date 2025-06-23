# Quick Start Guide

Get your agentic AI up and running in minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd agentic
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment**
   ```bash
   # Copy the example environment file
   cp env_example.txt .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_actual_api_key_here
   ```

## Quick Test

Run the demo to see the agent in action:

```bash
python main.py --demo
```

## Interactive Mode

Start an interactive chat session:

```bash
python main.py
```

### Available Commands

- `status` - Show agent status and capabilities
- `task <goal>` - Plan and execute a task
- `quit` / `exit` / `bye` - End the conversation

### Example Interaction

```
👤 You: Hello! Can you help me search for information about Python?
🤖 Agent: I'd be happy to help you search for information about Python! Let me look that up for you.

I found some information for you:

1. Python (programming language)
   Python is a high-level, interpreted programming language known for its simplicity and readability...

2. Python Software Foundation
   The Python Software Foundation (PSF) is a 501(c)(3) non-profit corporation that holds the intellectual property rights behind the Python programming language...

👤 You: task Create a simple text file with a greeting
🎯 Planning task: Create a simple text file with a greeting
📋 Task created: Create a simple text file with a greeting
⚡ Executing task...
✅ Task completed successfully!
⏱️  Execution time: 3.50 seconds
```

## Examples

Check out the examples directory for more detailed usage:

```bash
# Basic usage example
python examples/basic_usage.py

# Task planning example
python examples/task_planning.py
```

## Configuration

The agent is highly configurable. Key settings in your `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4

# Agent Configuration
AGENT_NAME=AgenticAI
AGENT_PERSONALITY=helpful, intelligent, and proactive

# Tool Configuration
ENABLE_WEB_SEARCH=true
ENABLE_FILE_OPERATIONS=true
ENABLE_CODE_EXECUTION=true

# Memory Configuration
MAX_MEMORY_SIZE=1000
MEMORY_TYPE=persistent
```

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY is required"**
   - Make sure you've set your OpenAI API key in the `.env` file
   - Verify the key is valid and has sufficient credits

2. **Import errors**
   - Ensure you've installed all dependencies: `pip install -r requirements.txt`
   - Check that you're running Python 3.8+

3. **Tool execution errors**
   - Some tools require internet connectivity
   - File operations are restricted to the current working directory for security

### Getting Help

- Check the full [README.md](README.md) for detailed documentation
- Run `python main.py --help` for command-line options
- Review the examples in the `examples/` directory

## Next Steps

- Explore the code structure in `core/`, `tools/`, `memory/`, and `planning/`
- Create your own custom tools
- Extend the agent with new capabilities
- Integrate with your own applications

Happy agent building! 🤖 