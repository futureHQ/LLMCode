# LLM Code

> ⚠️ This project is currently under active development and in its early stages.

LLM Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster through natural language commands. This tool integrates directly with your development environment, allowing you to edit files, navigate directories, and interact with an AI assistant.

Inspired by Anthropic's Claude Code, this project aims to provide a similar interactive coding experience while being open-source and customizable.

## Features

- 🤖 Interactive AI coding assistant
- 📁 File and directory operations
- ✏️ File editing and appending
- 🔍 Codebase context understanding
- ⚙️ Configurable settings
- 🌈 Colored terminal output

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llmcode.git
cd llmcode
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API key:
```bash
python main.py
/config set apiKey YOUR_API_KEY
```

## Usage

Start the application:
```bash
python main.py
```

### Available Commands

- Basic Commands:
  - `/help` - Show help message
  - `/exit`, `/quit` - Exit the program
  - `/pwd`, `/cwd` - Print working directory

- File Operations:
  - `/ls [path]` - List directory contents
  - `/tree [path]` - Show directory structure
  - `/cat <file>` - Display file contents
  - `/write <file>` - Create/overwrite a file
  - `/append <file>` - Append to existing file

- Directory Operations:
  - `/cd <path>` - Change directory
  - `/mkdir <path>` - Create directory

- Configuration:
  - `/config set <key> <value>` - Set configuration value
  - `/config list` - List all configurations
  - `/config show` - Show active configuration

- Context:
  - `/context [path]`, `/#` - Get workspace context

## Configuration

The configuration file is stored at `~/.llm_code_config.json`. You can configure:

- `apiKey` - Your API key
- `baseUrl` - API base URL (default: https://api.openai.com/v1)
- `model` - AI model to use
- `debug` - Enable/disable debug mode

## Usage

Start the application:
```bash
python main.py
```

### Basic Usage Examples

1. First, get the context of your codebase:
```bash
[myproject]> /# 
Getting context from: /path/to/myproject
Found 3 file(s) in workspace...

[myproject]> Now I understand your codebase. How can I help?
```

2. Or use tree to understand the project structure:
```bash
[myproject]> /tree
Directory tree for: /path/to/myproject
└── src
    ├── main.py
    ├── utils
    │   └── helpers.py
    └── tests
        └── test_main.py

[myproject]> Can you explain the project structure?
```

3. Get context for specific files:
```bash
[myproject]> /context src/main.py
Getting context from: /path/to/myproject/src/main.py
Found 1 file(s) in workspace...

[myproject]> Can you help me modify the main function?
```

4. Example coding assistance:
```bash
[myproject]> /# 
Getting context from current directory...

[myproject]> Can you add error handling to the process_data function?
Assistant: I see the process_data function in main.py. Here's how we can add error handling...
```

### Best Practices
- Always provide context using `/context`, `/#`, or `/tree` before asking for code modifications
- Use `/context <file>` when working on specific files
- Use `/tree` to get an overview of project structure
- Use `/#` to get context of the current directory

