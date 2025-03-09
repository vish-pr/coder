import os
import subprocess
import requests
from bs4 import BeautifulSoup
import argparse
import logging
import sys
from typing import List, Dict, Any, Optional, Tuple
import re
import time

class Agent:
  def __init__(self, log_level: str = "INFO"):
    """
    Initialize the agent with capabilities for web browsing, CLI command execution, and code editing
    
    Args:
      log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    self.setup_logging(log_level)
    self.logger = logging.getLogger("agent")
    self.logger.info("Agent initialized with web browsing, CLI, and code editing capabilities")
    self.session = requests.Session()
    self.session.headers.update({
      "User-Agent": "AgentBot/1.0 (Python Agent for Web, CLI, and Code)"
    })
  
  def setup_logging(self, log_level: str) -> None:
    """Configure logging for the agent"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
      raise ValueError(f"Invalid log level: {log_level}")
    
    logging.basicConfig(
      level=numeric_level,
      format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
      handlers=[logging.StreamHandler(sys.stdout)]
    )
  
  def browse(self, url: str, selector: Optional[str] = None) -> Dict[str, Any]:
    """
    Browse a webpage and optionally extract content using CSS selectors
    
    Args:
      url: The URL to browse
      selector: Optional CSS selector to extract specific content
      
    Returns:
      Dictionary containing the response, parsed HTML, and extracted content if selector is provided
    """
    self.logger.info(f"Browsing URL: {url}")
    try:
      response = self.session.get(url, timeout=10)
      response.raise_for_status()
      
      soup = BeautifulSoup(response.text, "html.parser")
      
      result = {
        "status_code": response.status_code,
        "url": response.url,
        "title": soup.title.string if soup.title else None,
        "html": response.text,
        "soup": soup
      }
      
      if selector:
        self.logger.info(f"Extracting content with selector: {selector}")
        selected_elements = soup.select(selector)
        result["selected_content"] = [elem.get_text(strip=True) for elem in selected_elements]
        result["selected_html"] = [str(elem) for elem in selected_elements]
      
      return result
      
    except requests.exceptions.RequestException as e:
      self.logger.error(f"Error browsing {url}: {str(e)}")
      return {"error": str(e)}
  
  def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Perform a web search (Note: This is a simplified implementation)
    In a production environment, you would use a proper search API
    
    Args:
      query: Search query
      num_results: Number of results to return
      
    Returns:
      List of search results with title and URL
    """
    self.logger.info(f"Searching for: {query}")
    
    # In a real implementation, you would use a search API like Google Custom Search,
    # Bing API, or similar. This is a placeholder implementation.
    try:
      # Using DuckDuckGo HTML (not an official API)
      search_url = f"https://html.duckduckgo.com/html/?q={query}"
      response = self.session.get(search_url)
      response.raise_for_status()
      
      soup = BeautifulSoup(response.text, "html.parser")
      results = []
      
      # This would need to be updated based on the actual HTML structure
      for result in soup.select(".result")[:num_results]:
        title_elem = result.select_one(".result__title")
        url_elem = result.select_one(".result__url")
        
        if title_elem and url_elem:
          results.append({
            "title": title_elem.get_text(strip=True),
            "url": url_elem.get_text(strip=True)
          })
      
      return results
      
    except Exception as e:
      self.logger.error(f"Error during search: {str(e)}")
      return [{"error": str(e)}]
  
  def run_command(self, command: str, timeout: int = 60, shell: bool = False) -> Dict[str, Any]:
    """
    Execute a CLI command
    
    Args:
      command: Command to execute (string or list of arguments)
      timeout: Maximum execution time in seconds
      shell: Whether to execute through shell
      
    Returns:
      Dictionary with stdout, stderr, and return code
    """
    self.logger.info(f"Running command: {command}")
    
    try:
      if isinstance(command, str) and not shell:
        command_args = command.split()
      else:
        command_args = command
      
      process = subprocess.Popen(
        command_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell,
        text=True
      )
      
      stdout, stderr = process.communicate(timeout=timeout)
      
      result = {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": process.returncode,
        "success": process.returncode == 0
      }
      
      if process.returncode != 0:
        self.logger.warning(f"Command returned non-zero exit code: {process.returncode}")
        self.logger.warning(f"stderr: {stderr}")
      
      return result
      
    except subprocess.TimeoutExpired:
      self.logger.error(f"Command timed out after {timeout} seconds")
      return {"error": f"Command timed out after {timeout} seconds"}
    except Exception as e:
      self.logger.error(f"Error executing command: {str(e)}")
      return {"error": str(e)}
  
  def read_file(self, file_path: str) -> Dict[str, Any]:
    """
    Read a file from disk
    
    Args:
      file_path: Path to the file
      
    Returns:
      Dictionary with file content or error message
    """
    self.logger.info(f"Reading file: {file_path}")
    try:
      with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
      return {"content": content, "success": True}
    except Exception as e:
      self.logger.error(f"Error reading file {file_path}: {str(e)}")
      return {"error": str(e), "success": False}
  
  def write_file(self, file_path: str, content: str, backup: bool = True) -> Dict[str, Any]:
    """
    Write content to a file
    
    Args:
      file_path: Path to the file
      content: Content to write
      backup: Whether to create a backup of the existing file
      
    Returns:
      Dictionary with success status and backup path if created
    """
    self.logger.info(f"Writing to file: {file_path}")
    result = {"success": False}
    
    try:
      # Create backup if file exists and backup is requested
      if os.path.exists(file_path) and backup:
        backup_path = f"{file_path}.backup.{int(time.time())}"
        with open(file_path, "r", encoding="utf-8") as src:
          with open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
        result["backup_path"] = backup_path
        self.logger.info(f"Created backup at {backup_path}")
      
      # Write new content
      with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
      
      result["success"] = True
      return result
      
    except Exception as e:
      self.logger.error(f"Error writing to file {file_path}: {str(e)}")
      result["error"] = str(e)
      return result
  
  def edit_code_file(self, file_path: str, edits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Edit a code file by applying a list of edits
    
    Args:
      file_path: Path to the code file
      edits: List of edit operations to apply. Each edit is a dictionary with:
        - type: 'replace', 'insert', or 'delete'
        - line_start: Starting line number (1-based)
        - line_end: Ending line number (for replace and delete)
        - content: New content (for replace and insert)
        
    Returns:
      Dictionary with success status and error message if applicable
    """
    self.logger.info(f"Editing code file: {file_path} with {len(edits)} edits")
    
    # Read the file
    read_result = self.read_file(file_path)
    if not read_result.get("success", False):
      return read_result
    
    content = read_result["content"]
    lines = content.splitlines()
    
    # Apply edits in reverse order to avoid affecting line numbers
    sorted_edits = sorted(edits, key=lambda e: e["line_start"], reverse=True)
    
    for edit in sorted_edits:
      edit_type = edit["type"]
      line_start = max(1, edit["line_start"]) - 1 # Convert to 0-based
      
      if edit_type == "replace":
        line_end = edit["line_end"] - 1 # Convert to 0-based
        new_content = edit["content"].splitlines()
        lines[line_start:line_end+1] = new_content
        
      elif edit_type == "insert":
        new_content = edit["content"].splitlines()
        lines[line_start:line_start] = new_content
        
      elif edit_type == "delete":
        line_end = edit["line_end"] - 1 # Convert to 0-based
        lines[line_start:line_end+1] = []
      
      else:
        self.logger.warning(f"Unknown edit type: {edit_type}")
    
    # Write the modified content back to the file
    new_content = "\n".join(lines)
    return self.write_file(file_path, new_content)
  
  def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyze code to identify structure, functions, classes, etc.
    This is a simple implementation and would need to be expanded for production use.
    
    Args:
      code: Code to analyze
      language: Programming language of the code
      
    Returns:
      Dictionary with analysis results
    """
    self.logger.info(f"Analyzing {language} code")
    result = {"language": language}
    
    if language == "python":
      # Extract function definitions
      function_pattern = r"def\s+(\w+)\s*\(([^)]*)\)\s*(?:->.*?)?:"
      functions = re.findall(function_pattern, code)
      result["functions"] = [{"name": f[0], "params": f[1].strip()} for f in functions]
      
      # Extract class definitions
      class_pattern = r"class\s+(\w+)(?:\(([^)]*)\))?\s*:"
      classes = re.findall(class_pattern, code)
      result["classes"] = [{"name": c[0], "inherits": c[1].strip()} for c in classes]
      
      # Count lines
      result["lines"] = len(code.splitlines())
      
      # Check imports
      import_pattern = r"(?:from\s+(\S+)\s+)?import\s+(.+?)(?:\s+as\s+.+)?$"
      imports = []
      for line in code.splitlines():
        line = line.strip()
        if line.startswith("import ") or line.startswith("from "):
          match = re.search(import_pattern, line)
          if match:
            module_from = match.group(1) or ""
            module_import = match.group(2)
            imports.append({"from": module_from, "import": module_import})
      result["imports"] = imports
      
    # Add additional language analyzers as needed
    
    return result

def main():
  parser = argparse.ArgumentParser(description="Agent with web, CLI, and code editing capabilities")
  subparsers = parser.add_subparsers(dest="command", help="Command to execute")
  
  # Browse command
  browse_parser = subparsers.add_parser("browse", help="Browse a webpage")
  browse_parser.add_argument("url", help="URL to browse")
  browse_parser.add_argument("--selector", help="CSS selector to extract content")
  
  # Search command
  search_parser = subparsers.add_parser("search", help="Search the web")
  search_parser.add_argument("query", help="Search query")
  search_parser.add_argument("--results", type=int, default=5, help="Number of results to return")
  
  # Run command
  run_parser = subparsers.add_parser("run", help="Run a CLI command")
  run_parser.add_argument("cmd", help="Command to run")
  run_parser.add_argument("--timeout", type=int, default=60, help="Command timeout in seconds")
  run_parser.add_argument("--shell", action="store_true", help="Run command in shell")
  
  # File commands
  read_parser = subparsers.add_parser("read", help="Read a file")
  read_parser.add_argument("file", help="File to read")
  
  write_parser = subparsers.add_parser("write", help="Write to a file")
  write_parser.add_argument("file", help="File to write")
  write_parser.add_argument("content", help="Content to write")
  write_parser.add_argument("--no-backup", action="store_true", help="Don't create backup")
  
  # Parse arguments
  args = parser.parse_args()
  
  # Create agent
  agent = Agent()
  
  # Execute requested command
  if args.command == "browse":
    result = agent.browse(args.url, args.selector)
    if args.selector and "selected_content" in result:
      for i, content in enumerate(result["selected_content"]):
        print(f"[{i+1}] {content}")
    elif "title" in result:
      print(f"Title: {result['title']}")
      print(f"URL: {result['url']}")
  
  elif args.command == "search":
    results = agent.search(args.query, args.results)
    for i, result in enumerate(results):
      print(f"[{i+1}] {result.get('title', 'No title')}")
      print(f"  {result.get('url', 'No URL')}")
      print()
  
  elif args.command == "run":
    result = agent.run_command(args.cmd, args.timeout, args.shell)
    if result.get("stdout"):
      print("STDOUT:")
      print(result["stdout"])
    if result.get("stderr"):
      print("STDERR:")
      print(result["stderr"])
    print(f"Return code: {result.get('returncode', 'Unknown')}")
  
  elif args.command == "read":
    result = agent.read_file(args.file)
    if "content" in result:
      print(result["content"])
    else:
      print(f"Error: {result.get('error', 'Unknown error')}")
  
  elif args.command == "write":
    result = agent.write_file(args.file, args.content, not args.no_backup)
    if result.get("success"):
      print(f"Successfully wrote to {args.file}")
      if "backup_path" in result:
        print(f"Backup created at {result['backup_path']}")
    else:
      print(f"Error: {result.get('error', 'Unknown error')}")
  
  else:
    parser.print_help()

if __name__ == "__main__":
  main()
