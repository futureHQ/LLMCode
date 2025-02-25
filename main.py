#!/usr/bin/env python3
"""
LLM Code – Python version
-----------------------------

LLM Code is an agentic coding tool that lives in your terminal, understands
your codebase, and helps you code faster through natural language commands.
This early research preview integrates directly with your development environment,
allowing you to edit files, navigate directories, and interact with an AI assistant.

Key capabilities include:
  • Editing and appending files
  • Answering questions about your code’s architecture and logic
  • Running file and git commands (to be extended as needed)
  • Interacting with an AI API (stub provided)

Usage:
  • Run the script and follow on-screen prompts.
  • Use commands like /help, /exit, /pwd, /ls, /cd, /mkdir, /cat, /write, /append, /config, /context or /#.
  • When not using a built‐in command, your input is sent to the assistant.
  
Before you begin:
  • Ensure Python 3 is installed.
  • (Optionally) set your API key and baseUrl using: /config set apiKey YOUR_API_KEY and /config set baseUrl YOUR_BASE_URL
"""

import os
import sys
import json
import time
import openai
import traceback
import fnmatch

# ANSI color codes for colored terminal output
class Color:
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    @staticmethod
    def blue(text):
        return f"{Color.BLUE}{text}{Color.RESET}"

    @staticmethod
    def green(text):
        return f"{Color.GREEN}{text}{Color.RESET}"

    @staticmethod
    def red(text):
        return f"{Color.RED}{text}{Color.RESET}"

    @staticmethod
    def yellow(text):
        return f"{Color.YELLOW}{text}{Color.RESET}"

    @staticmethod
    def dim(text):
        return f"{Color.DIM}{text}{Color.RESET}"


# ----------------------------
# Configuration Management
# ----------------------------

CONFIG_PATH = os.path.expanduser("~/.llm_code_config.json")
DEFAULT_CONFIG = {
    "configs": {
        "default": {
            "apiKey": "",
            "baseUrl": "https://api.openai.com/v1",
            "model": "gpt-4o",
            "debug": False
        }
    },
    "active": "default"
}

def load_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        else:
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(Color.red("Error loading config:"), e)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(Color.red("Error saving config:"), e)

# Load configuration on startup.
config = load_config()

# Added missing functions for configuration handling.
def get_active_config():
    active = config.get("active", "default")
    return config.get("configs", {}).get(active, {})

def set_active_config(key, value):
    active = config.get("active", "default")
    if active in config.get("configs", {}):
        config["configs"][active][key] = value
        save_config(config)
        return True
    return False


# ----------------------------
# File System Operations
# ----------------------------

def get_current_dir():
    return os.getcwd()

def print_tree(path, prefix="", is_last=True):
    """Print directory structure in tree format."""
    try:
        full_path = os.path.abspath(os.path.join(os.getcwd(), path))
        base_name = os.path.basename(full_path)
        
        # Print current node
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{Color.blue(base_name) if os.path.isdir(full_path) else base_name}")
        
        # If it's a directory, process its contents
        if os.path.isdir(full_path):
            entries = os.listdir(full_path)
            entries.sort(key=lambda x: (not os.path.isdir(os.path.join(full_path, x)), x.lower()))
            
            for i, entry in enumerate(entries):
                entry_path = os.path.join(full_path, entry)
                # Skip hidden files and common ignore patterns
                if entry.startswith('.') or entry in ['__pycache__', 'node_modules']:
                    continue
                    
                is_last_entry = i == len(entries) - 1
                new_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(os.path.join(path, entry), new_prefix, is_last_entry)
                
    except Exception as e:
        print(Color.red(f"Error accessing {path}: {str(e)}"))
        
def list_directory(dir_path="."):
    try:
        full_path = os.path.abspath(os.path.join(os.getcwd(), dir_path))
        entries = os.listdir(full_path)
        files = []
        for entry in entries:
            entry_path = os.path.join(full_path, entry)
            try:
                stat = os.stat(entry_path)
                files.append({
                    "name": entry,
                    "isDirectory": os.path.isdir(entry_path),
                    "size": stat.st_size,
                    "modified": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(stat.st_mtime))
                })
            except Exception as e:
                files.append({"name": entry, "error": str(e)})
        return {"success": True, "path": full_path, "files": files}
    except Exception as e:
        return {"success": False, "error": str(e)}

def change_directory(dir_path):
    try:
        full_path = os.path.abspath(os.path.join(os.getcwd(), dir_path))
        if not os.path.isdir(full_path):
            return {"success": False, "error": f"{full_path} is not a directory"}
        os.chdir(full_path)
        return {"success": True, "path": os.getcwd()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def make_directory(dir_path):
    try:
        full_path = os.path.abspath(os.path.join(os.getcwd(), dir_path))
        os.makedirs(full_path, exist_ok=True)
        return {"success": True, "path": full_path}
    except Exception as e:
        return {"success": False, "error": str(e)}

def read_file(file_path):
    try:
        full_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"success": True, "path": full_path, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}

def write_file(file_path, content):
    try:
        full_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
        dir_name = os.path.dirname(full_path)
        os.makedirs(dir_name, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": full_path}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Add after the file system operations section
def get_workspace_context(path="."):
    """Get context from files in the workspace."""
    try:
        ignore_patterns = []
        gitignore_path = os.path.join(os.getcwd(), '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                ignore_patterns = [
                    line.strip().replace('/', os.sep) for line in f 
                    if line.strip() and not line.startswith('#')
                ]

        context = []
        full_path = os.path.abspath(os.path.join(os.getcwd(), path))

        if os.path.isfile(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                context.append({
                    "path": os.path.basename(full_path),
                    "content": content
                })
                return {"success": True, "context": context}
            except (UnicodeDecodeError, IOError):
                return {"success": False, "error": "Cannot read file: binary or unreadable"}

        for root, dirs, files in os.walk(full_path):
            rel_root = os.path.relpath(root, full_path)
            dirs[:] = [d for d in dirs if not any(
                fnmatch.fnmatch(os.path.join(rel_root, d), p) or
                fnmatch.fnmatch(d, p.rstrip(os.sep))
                for p in ignore_patterns
            )]
            
            for file in files:
                rel_path = os.path.join(rel_root, file)
                if any(fnmatch.fnmatch(rel_path, p) for p in ignore_patterns) or \
                   any(fnmatch.fnmatch(file, p.rstrip(os.sep)) for p in ignore_patterns) or \
                   any(pattern in file.lower() for pattern in ['.git', '.pyc', '.env', '__pycache__']):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, path)
                
                if any(any(fnmatch.fnmatch(part, p) for p in ignore_patterns) 
                       for part in rel_path.split(os.sep)):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    context.append({"path": rel_path, "content": content})
                except (UnicodeDecodeError, IOError):
                    continue
                    
        return {"success": True, "context": context}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ----------------------------
# File Edit Mode State
# ----------------------------

class FileEditMode:
    def __init__(self):
        self.active = False
        self.file_path = None
        self.content = []
        self.mode = None  # 'create' or 'append'

    def reset(self):
        self.active = False
        self.file_path = None
        self.content = []
        self.mode = None

file_edit_mode = FileEditMode()


# ----------------------------
# API Call (Stub)
# ----------------------------

def call_api(messages):
    """Send messages to OpenAI API and get response."""
    try:
        active_config = get_active_config()
        
        # Check debug mode
        if active_config.get("debug", False):
            time.sleep(1)  # Simulate API delay
            return {
                "success": True,
                "message": "DEBUG MODE: This is a mock response. Set debug=false to use actual API."
            }
        
        api_key = active_config.get("apiKey")
        model = active_config.get("model", "gpt-4o")
        
        if not api_key:
            return {"success": False, "error": "API key not configured"}
        
        client = openai.OpenAI(api_key=api_key)
        
        # Convert messages to OpenAI format
        formatted_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        # Stream the response
        response = client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=0.7,
            stream=True  # Enable streaming
        )
        
        # Initialize variables for streaming
        full_response = ""
        print(Color.blue("Assistant: "), end="", flush=True)
        
        # Process the stream
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        
        print()  # New line after streaming completes
        return {"success": True, "message": full_response}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ----------------------------
# Main Interactive Loop
# ----------------------------

# Add import at the top with other imports
from intro import print_banner

# In the main() function, replace the initial print statements with:
def main():
    print_banner()  # Add banner at the very start
    
    active_config = get_active_config()
    if not active_config.get("apiKey", "").strip():
        print(Color.dim("Please configure your API key first."))
        while True:
            line = input(Color.green("> ")).strip()
            if line.startswith("/config set apiKey "):
                api_key = line[len("/config set apiKey "):].strip()
                if api_key:
                    set_active_config("apiKey", api_key)
                    print(Color.green("API key configured. Please restart LLM Code."))
                    sys.exit(0)
                else:
                    print(Color.red("API key cannot be empty."))
            elif line in ("/exit", "/quit"):
                sys.exit(0)
            else:
                print(Color.red('Please configure your API key with "/config set apiKey YOUR_API_KEY"'))
    
    print(Color.blue("LLM Code") + " - Your AI coding assistant")
    print("Type \"/exit\" to quit or \"/help\" for commands")
    print(Color.dim(f"Working directory: {os.getcwd()}"))
    
    messages = [{
        "role": "system",
        "content": f"You are a helpful coding assistant. You have access to the user's filesystem.\nCurrent directory: {os.getcwd()}"
    }]
    
    while True:
        try:
            # Update prompt to show more context
            dir_name = os.path.basename(os.getcwd())
            prompt = (Color.yellow(f"[{dir_name}] edit> ") if file_edit_mode.active and file_edit_mode.mode == "create" else
                     Color.yellow(f"[{dir_name}] append> ") if file_edit_mode.active and file_edit_mode.mode == "append" else
                     Color.green(f"[{dir_name}]> "))
            line = input(prompt)

        except (EOFError, KeyboardInterrupt):
            print("\n" + Color.blue("Goodbye! Thanks for using LLM Code."))
            break

        # File edit mode handling
        if file_edit_mode.active:
            if line.strip() == "/save":
                content = "\n".join(file_edit_mode.content)
                result = write_file(file_edit_mode.file_path, content)
                if result.get("success"):
                    print(Color.green(f"File saved: {result['path']}"))
                else:
                    print(Color.red(f"Error saving file: {result.get('error')}"))
                file_edit_mode.reset()
                continue
            elif line.strip() == "/cancel":
                print(Color.yellow("File edit cancelled."))
                file_edit_mode.reset()
                continue
            else:
                file_edit_mode.content.append(line)
                continue

        cmd = line.strip()
        
        # Basic commands
        if cmd in ("/exit", "/quit"):
            print(Color.blue("Goodbye!"))
            break

        # Add the print_help function before the main loop
        # Move print_help function outside of main loop
        def print_help():
            """Print help information about available commands."""
            commands = {
                "Basic Commands": {
                    "/help": "Show this help message",
                    "/exit, /quit": "Exit the program",
                    "/pwd, /cwd": "Print working directory"
                },
                "File Operations": {
                    "/ls [path]": "List directory contents",
                    "/tree [path]": "Show directory structure in tree format",
                    "/cat <file>": "Display file contents",
                    "/write <file>": "Create/overwrite a file",
                    "/append <file>": "Append to existing file"
                },
                "Directory Operations": {
                    "/cd <path>": "Change directory",
                    "/mkdir <path>": "Create directory"
                },
                "Configuration": {
                    "/config set <key> <value>": "Set configuration value",
                    "/config list": "List all configurations",
                    "/config show": "Show active configuration"
                },
                "Context": {
                    "/context [path], /#": "Get workspace context from path (default: current directory)"
                }
            }
        
            print(Color.blue("\nAvailable Commands:"))
            for section, cmds in commands.items():
                print(Color.yellow(f"\n{section}:"))
                for cmd, desc in cmds.items():
                    print(f"  {Color.green(cmd):<30} {desc}")
            print()
        
        # Add config command handling in main loop after the basic commands section
        # Configuration commands
        if cmd.startswith("/config"):
            parts = cmd.split()
            if len(parts) == 1:
                print(Color.red("Missing config command. Use: /config set|list|show"))
                continue
                
            if parts[1] == "list":
                print(Color.green("Available configurations:"))
                for name in config.get("configs", {}):
                    if name == config.get("active"):
                        print(f"* {name} (active)")
                    else:
                        print(f"  {name}")
                continue
                
            if parts[1] == "show":
                active = get_active_config()
                print(Color.green("Active configuration:"))
                for key, value in active.items():
                    if key == "apiKey":
                        print(f"  {key}: {'*' * 8}")
                    else:
                        print(f"  {key}: {value}")
                continue
                
            if parts[1] == "set" and len(parts) >= 4:
                key = parts[2]
                value = " ".join(parts[3:])
                if set_active_config(key, value):
                    print(Color.green(f"Configuration updated: {key}"))
                else:
                    print(Color.red("Failed to update configuration"))
                continue
                
            print(Color.red("Invalid config command. Use: /config set|list|show"))
            continue

        if cmd == "/help":
            print_help()
            continue

        if cmd in ("/pwd", "/cwd"):
            print(Color.green("Current directory:"), get_current_dir())
            continue

        # Directory operations
        if cmd.startswith("/cd "):
            path_arg = cmd[4:].strip()
            result = change_directory(path_arg)
            if result.get("success"):
                print(Color.green(f"Changed directory to: {result['path']}"))
                messages[0]["content"] = f"You are a helpful coding assistant. You have access to the user's filesystem.\nCurrent directory: {os.getcwd()}"
            else:
                print(Color.red(f"Error: {result.get('error')}"))
            continue

        if cmd.startswith("/mkdir "):
            path_arg = cmd[7:].strip()
            result = make_directory(path_arg)
            if result.get("success"):
                print(Color.green(f"Created directory: {result['path']}"))
            else:
                print(Color.red(f"Error: {result.get('error')}"))
            continue

        # File operations
        if cmd.startswith("/cat "):
            file_arg = cmd[5:].strip()
            result = read_file(file_arg)
            if result.get("success"):
                print(Color.green(f"Contents of: {result['path']}"))
                print("─" * 40)
                print(result.get("content"))
                print("─" * 40)
            else:
                print(Color.red(f"Error: {result.get('error')}"))
            continue

        if cmd.startswith("/write "):
            file_arg = cmd[7:].strip()
            file_edit_mode.active = True
            file_edit_mode.file_path = file_arg
            file_edit_mode.content = []
            file_edit_mode.mode = "create"
            print(Color.green(f"Creating file: {file_arg}"))
            print(Color.dim("Enter file content (type /save to save and exit, or /cancel to cancel):"))
            continue

        if cmd.startswith("/append "):
            file_arg = cmd[8:].strip()
            result = read_file(file_arg)
            if result.get("success"):
                file_edit_mode.active = True
                file_edit_mode.file_path = file_arg
                file_edit_mode.content = result.get("content", "").splitlines()
                file_edit_mode.mode = "append"
                print(Color.green(f"Appending to file: {file_arg}"))
                print(Color.dim("Enter content to append (type /save to save and exit, or /cancel to cancel):"))
            else:
                print(Color.red(f"Error: {result.get('error')}"))
            continue

        # Context commands
        if cmd.startswith("/context") or cmd.startswith("/#"):
            parts = cmd.split(maxsplit=1)
            path = parts[1] if len(parts) > 1 else "."
            print(Color.green(f"Getting context from: {os.path.abspath(path)}"))
            result = get_workspace_context(path)
            if result.get("success"):
                files = result["context"]
                print(Color.green(f"\nFound {len(files)} file(s) in workspace:"))
                
                # Build context message for chat history
                context_message = f"Here are the files in the workspace ({path}):\n\n"
                for file in files:
                    print(Color.blue(f"\n[{file['path']}]"))
                    print("─" * 80)
                    content_lines = file['content'].splitlines()
                    for i, line in enumerate(content_lines, 1):
                        print(f"{Color.dim(f'{i:4d} │')} {line}")
                    print("─" * 80)
                    
                    # Add file content to context message
                    context_message += f"File: {file['path']}\n```\n{file['content']}\n```\n\n"
                
                # Add context to chat history
                messages.append({
                    "role": "user",
                    "content": f"Here's the current workspace context:\n{context_message}"
                })
                messages.append({
                    "role": "assistant",
                    "content": "I've received and understood the workspace context. I'll use this information to provide better assistance."
                })
                print(Color.green("\nContext added to chat history."))
            else:
                print(Color.red(f"Error: {result.get('error')}"))
            continue

        if cmd.startswith("/ls"):
            parts = cmd.split(maxsplit=1)
            dir_path = parts[1] if len(parts) > 1 else "."
            result = list_directory(dir_path)
            if result.get("success"):
                output = [Color.green(f"Contents of: {result['path']}")]
                files = result["files"]
                files.sort(key=lambda x: (not x.get("isDirectory", False), x["name"].lower()))
                for f in files:
                    if f.get("isDirectory"):
                        output.append(f"{f['name']}/")
                    elif f.get("error"):
                        output.append(f"{f['name']} (error: {f['error']})")
                    else:
                        output.append(f"{f['name']}")
                
                # Print to terminal
                print("\n".join(output))
                
                # Add to AI context
                messages.append({
                    "role": "user",
                    "content": f"Directory listing for {result['path']}:\n" + "\n".join(output)
                })
            else:
                print(Color.red(f"Error: {result.get('error')}"))
            continue

        if cmd.startswith("/tree"):
            parts = cmd.split(maxsplit=1)
            path = parts[1] if len(parts) > 1 else "."
            print(Color.green(f"Directory tree for: {os.path.abspath(path)}"))
            
            # Capture tree output
            import io
            from contextlib import redirect_stdout
            
            tree_output = io.StringIO()
            with redirect_stdout(tree_output):
                print_tree(path)
            
            # Print to terminal
            print(tree_output.getvalue())
            
            # Add to AI context
            messages.append({
                "role": "user",
                "content": f"Directory tree for {os.path.abspath(path)}:\n{tree_output.getvalue()}"
            })
            continue

        # Context commands (already handling context properly)
        if cmd.startswith("/context") or cmd.startswith("/#"):
            parts = cmd.split(maxsplit=1)
            path = parts[1] if len(parts) > 1 else "."
            print(Color.green(f"Getting context from: {os.path.abspath(path)}"))
            result = get_workspace_context(path)
            if result.get("success"):
                files = result["context"]
                print(Color.green(f"\nFound {len(files)} file(s) in workspace:"))
                
                # Build context message for chat history
                context_message = f"Here are the files in the workspace ({path}):\n\n"
                for file in files:
                    print(Color.blue(f"\n[{file['path']}]"))
                    print("─" * 80)
                    content_lines = file['content'].splitlines()
                    for i, line in enumerate(content_lines, 1):
                        print(f"{Color.dim(f'{i:4d} │')} {line}")
                    print("─" * 80)
                    
                    # Add file content to context message
                    context_message += f"File: {file['path']}\n```\n{file['content']}\n```\n\n"
                
                # Add context to chat history
                messages.append({
                    "role": "user",
                    "content": f"Here's the current workspace context:\n{context_message}"
                })
                messages.append({
                    "role": "assistant",
                    "content": "I've received and understood the workspace context. I'll use this information to provide better assistance."
                })
                print(Color.green("\nContext added to chat history."))
            else:
                print(Color.red(f"Error: {result.get('error')}"))
            continue

        if cmd.startswith("/ls"):
            parts = cmd.split(maxsplit=1)
            dir_path = parts[1] if len(parts) > 1 else "."
            result = list_directory(dir_path)
            if result.get("success"):
                output = [Color.green(f"Contents of: {result['path']}")]
                files = result["files"]
                files.sort(key=lambda x: (not x.get("isDirectory", False), x["name"].lower()))
                for f in files:
                    if f.get("isDirectory"):
                        output.append(f"{f['name']}/")
                    elif f.get("error"):
                        output.append(f"{f['name']} (error: {f['error']})")
                    else:
                        output.append(f"{f['name']}")
                
                # Print to terminal
                print("\n".join(output))
                
                # Add to AI context
                messages.append({
                    "role": "user",
                    "content": f"Directory listing for {result['path']}:\n" + "\n".join(output)
                })
            else:
                print(Color.red(f"Error: {result.get('error')}"))
            continue

        if cmd.startswith("/tree"):
            parts = cmd.split(maxsplit=1)
            path = parts[1] if len(parts) > 1 else "."
            print(Color.green(f"Directory tree for: {os.path.abspath(path)}"))
            
            # Capture tree output
            import io
            from contextlib import redirect_stdout
            
            tree_output = io.StringIO()
            with redirect_stdout(tree_output):
                print_tree(path)
            
            # Print to terminal
            print(tree_output.getvalue())
            
            # Add to AI context
            messages.append({
                "role": "user",
                "content": f"Directory tree for {os.path.abspath(path)}:\n{tree_output.getvalue()}"
            })
            continue

        # Context commands (already handling context properly)
        if cmd.startswith("/context") or cmd.startswith("/#"):
            parts = cmd.split(maxsplit=1)
            path = parts[1] if len(parts) > 1 else "."
            print(Color.green(f"Getting context from: {os.path.abspath(path)}"))
            result = get_workspace_context(path)
            if result.get("success"):
                files = result["context"]
                print(Color.green(f"\nFound {len(files)} file(s) in workspace:"))
                
                # Build context message for chat history
                context_message = f"Here are the files in the workspace ({path}):\n\n"
                for file in files:
                    print(Color.blue(f"\n[{file['path']}]"))
                    print("─" * 80)
                    content_lines = file['content'].splitlines()
                    for i, line in enumerate(content_lines, 1):
                        print(f"{Color.dim(f'{i:4d} │')} {line}")
                    print("─" * 80)
                    
                    # Add file content to context message
                    context_message += f"File: {file['path']}\n```\n{file['content']}\n```\n\n"
                
                # Add context to chat history
                messages.append({
                    "role": "user",
                    "content": f"Here's the current workspace context:\n{context_message}"
                })
                messages.append({
                    "role": "assistant",
                    "content": "I've received and understood the workspace context. I'll use this information to provide better assistance."
                })
                print(Color.green("\nContext added to chat history."))
            else:
                print(Color.red(f"Error: {result.get('error')}"))
            continue

        if cmd.startswith("/ls"):
            parts = cmd.split(maxsplit=1)
            dir_path = parts[1] if len(parts) > 1 else "."
            result = list_directory(dir_path)
            if result.get("success"):
                print(Color.green(f"Contents of: {result['path']}"))
                files = result["files"]
                files.sort(key=lambda x: (not x.get("isDirectory", False), x["name"].lower()))
                for f in files:
                    if f.get("isDirectory"):
                        print(Color.blue(f"{f['name']}/"))
                    elif f.get("error"):
                        print(Color.red(f"{f['name']} (error: {f['error']})"))
                    else:
                        print(f["name"])
            else:
                print(Color.red(f"Error: {result.get('error')}"))
            continue

        if cmd.startswith("/tree"):
            parts = cmd.split(maxsplit=1)
            path = parts[1] if len(parts) > 1 else "."
            print(Color.green(f"Directory tree for: {os.path.abspath(path)}"))
            print_tree(path)
            continue

        # In the main loop, update the response handling:
        # If not a built-in command, send as a message to the assistant
        messages.append({"role": "user", "content": cmd})
        response = call_api(messages)
        if response.get("success"):
            assistant_msg = response.get("message", "")
            # Don't print the message again since it was streamed
            messages.append({"role": "assistant", "content": assistant_msg})
        else:
            print(Color.red(f"Error: {response.get('error', 'Could not get response from API.')}"))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(Color.red("Fatal error:"))
        traceback.print_exc()
        sys.exit(1)
