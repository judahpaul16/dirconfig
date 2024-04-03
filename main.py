import os
import sys
import signal
import shutil
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml

observer = None
PID_FILE = 'dirconfig.pid'
ROOT_DIR = str(Path(__file__).resolve().parent)

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
    if source.startswith("."):
        source_path = ROOT_DIR
    else:
        source_path = os.path.abspath(source)
    
    rules = task['rules']
    
    for file in os.listdir(source_path):
        for rule in rules:
            if file.endswith(rule['extension']):
                # Correctly resolve destination path
                if rule['destination'].startswith("/"):
                    # Treat as an absolute path
                    dest_path = os.path.abspath(rule['destination'][1:])
                else:
                    # Treat as a relative path from source
                    dest_path = os.path.abspath(os.path.join(source_path, rule['destination']))
                
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                
                source_file_path = os.path.join(source_path, file)
                dest_file_path = os.path.join(dest_path, file)
                shutil.move(source_file_path, dest_file_path)
                print(f"Moved: {file} -> {dest_file_path}")

def signal_handler(signum, frame):
    print("\nReceived interrupt signal. Stopping dirconfig...")
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
        sys.exit(1)
    except ProcessLookupError:
        print("Error: Process not found. It may have been stopped already.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='dirconfig Daemon')
    parser.add_argument('action', choices=['start', 'stop'], help='Start or stop the daemon')
    args = parser.parse_args()

    if args.action == 'start':
        config_path = os.path.join(ROOT_DIR, 'config.yaml')
        start_daemon(config_path)
    elif args.action == 'stop':
        stop_daemon()

if __name__ == "__main__":
    main()
