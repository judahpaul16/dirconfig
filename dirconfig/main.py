from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from pathlib import Path
import argparse
import logging
import signal
import shutil
import yaml
import sys
import os

observer = None
PID_FILE = 'dirconfig.pid'

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, tasks):
        self.tasks = tasks

    def on_any_event(self, event):
        for task in self.tasks:
            if task['type'] == 'file-organization':
                organize_files(task)

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def organize_files(task):
    source = task['source']
    # Use the current working directory as the base for relative paths.
    cwd = os.getcwd()
    
    # If the source is a relative path, resolve it based on the current working directory.
    source_path = os.path.abspath(os.path.join(cwd, source)) if source.startswith(".") else os.path.abspath(source)
    
    rules = task['rules']
    
    for file in os.listdir(source_path):
        file_extension = os.path.splitext(file)[1]
        
        for rule in rules:
            extensions = [ext.strip() for ext in rule['extension'].split(',')]
            
            if file_extension in extensions:
                # For destination paths starting with "/", treat them as absolute paths.
                # Otherwise, treat as relative to the source directory.
                if rule['destination'].startswith("/"):
                    dest_path = os.path.abspath(rule['destination'][1:])
                else:
                    dest_path = os.path.abspath(os.path.join(source_path, rule['destination']))
                
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                
                source_file_path = os.path.join(source_path, file)
                dest_file_path = os.path.join(dest_path, file)
                shutil.move(source_file_path, dest_file_path)
                print(f"Moved: {file} -> {dest_file_path}")
                logging.info(f"Moved: {file} -> {dest_file_path}")

def signal_handler(signum, frame):
    print("\nReceived interrupt signal. Stopping dirconfig...")
    logging.info("Received interrupt signal. Stopping dirconfig...")
    if observer is not None:
        observer.stop()
        observer.join()  # Ensure all threads are joined
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        sys.exit(0)

def start_daemon(config_path):
    global observer
    config = load_config(config_path)
    tasks = config['tasks']
    observer = Observer()
    for task in tasks:
        if task['type'] == 'file-organization':
            observer.schedule(ChangeHandler(tasks), os.path.abspath(task['source']), recursive=True)

    # Register the signal handler for SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    observer.start()
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    # This loop keeps the script running until the observer is stopped
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        if observer.is_alive():
            observer.stop()
            observer.join()

def stop_daemon():
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read())
        os.kill(pid, signal.SIGTERM)
    except FileNotFoundError:
        print("Error: PID file not found. Is the daemon running?")
        logging.error("Error: PID file not found. Is the daemon running?")
        sys.exit(1)
    except ProcessLookupError:
        print("Error: Process not found. It may have been stopped already.")
        logging.error("Error: Process not found. It may have been stopped already.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='dirconfig Daemon')
    parser.add_argument('action', choices=['start', 'stop'], help='Start or stop the daemon')
    # Default to 'config.yaml' in the current working directory if not specified
    parser.add_argument('--config', help='Path to the configuration file', default='config.yaml')
    parser.add_argument('--log', help='Path to the log file', default='dirconfig.log')
    args = parser.parse_args()

    # Resolve the absolute path of the configuration file
    config_path = os.path.abspath(args.config)

    # Initialize logging to log to a file specified by the --log argument.
    logging.basicConfig(level=logging.INFO, filename=args.log, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

    if args.action == 'start':
        if not os.path.exists(config_path):
            print(f"Configuration file not found: {config_path}")
            logging.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        start_daemon(config_path)
    elif args.action == 'stop':
        stop_daemon()

if __name__ == "__main__":
    main()
