from urbackup import urbackup_server, installer_os
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from threading import Thread, Event
import subprocess
import argparse
import logging
import signal
import shutil
import time
import yaml
import sys
import os

# Global variables
observer = None
backup_thread = None # Thread for backup scheduling
shutdown_event = Event()  # Event to signal shutdown to backup thread
PID_FILE = 'dirconfig.pid' # Default PID file path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__)) # Directory of the module

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
        
def get_urbackup_command(os_name=None):
    if os.name == 'nt' and os_name != 'Linux':  # Windows
        return 'urbackupclient_cmd'
    else:  # Linux or macOS
        return 'urbackupclientctl'
    
def add_to_path(new_path_entry):
    # Define the PowerShell command to modify the PATH
    powershell_command = f"""
    $newPathEntry = '{new_path_entry}';
    $envPath = [Environment]::GetEnvironmentVariable("PATH", "User");
    if ($envPath -split ';' -contains $newPathEntry) {{
        Write-Output 'Already in PATH'
    }} else {{
        $newPath = $envPath + ';' + $newPathEntry;
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User");
        Write-Output 'Added to PATH'
    }}
    """.replace('\n', ' ').replace('    ', '')
    try:
        # Execute the PowerShell command
        result = subprocess.run(["powershell", "-Command", powershell_command], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
            logging.info(result.stdout.strip())
        else:
            print("Failed to modify the system PATH:", result.stderr)
            logging.error("Failed to modify the system PATH: " + result.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {str(e)}")

def get_installer_filename(os_type):
    return "urbackup_client_installer" + (".exe" if os_type.lower() is installer_os.Windows else ".sh")

def check_and_install_urbackup_client(backup_config):
    result = subprocess.run([get_urbackup_command(), "status"], capture_output=True, text=True)
    if result.returncode != 0:
        print("UrBackup client not running. Attempting installation...")
        logging.info("UrBackup client not running. Attempting installation...")
        # Determine OS type for choosing the correct installer
        os_type = "Linux" if os.name != 'nt' else "Windows"
        installer_filename = get_installer_filename(os_type)
        backup_server = urbackup_server(
            url=backup_config['connection']['server'],
            username=backup_config['connection']['username'],
            password=backup_config['connection']['password']
        )
        if backup_server.login():
            client_name = f"{backup_config['name']}-dirconfig"
            if backup_server.download_installer(installer_filename, client_name, os_type):
                if os_type != "Windows":
                    subprocess.run(["chmod", "+x", installer_filename])  # Make executable on Unix/Linux
                subprocess.run([os.path.join(MODULE_DIR, installer_filename)])  # Execute installer
                # Add urbackupclientctl to PATH if Windows
                if os_type == 'Windows':
                    add_to_path('C:\\Program Files\\UrBackup\\')
                print("Installation successful.")
                logging.info("Installation successful.")
            else:
                print("Failed to download installer.")
                logging.error("Failed to download installer.")
        else:
            print("Failed to log in to the backup server.")
            logging.error("Failed to log in to the backup server.")
    else:
        print("UrBackup client is running.")
        logging.info("UrBackup client is running.")

def setup_backup_dirs(backup_config):
    """Add directories specified in config to UrBackup."""
    for directory in backup_config['directories']:
        cmd = [get_urbackup_command(), "add-backupdir", "--path", directory]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully added backup directory: {directory}")
            logging.info(f"Successfully added backup directory: {directory}")
        else:
            print(f"Failed to add backup directory: {directory}. Error: {result.stderr}")
            logging.error(f"Failed to add backup directory: {directory}. Error: {result.stderr}")

def initiate_backup(backup_type, client_name):
    """Initiate the backup process using the urbackupclientctl command with detailed options."""
    if 'incremental' in backup_type:
        backup_option = '-i'
    else:
        backup_option = '-f'

    cmd = [
        get_urbackup_command(), "start", backup_option,
        "--non-blocking", "--client", client_name
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully started {backup_type} backup for {client_name}.")
        logging.info(f"Successfully started {backup_type} backup for {client_name}.")
    else:
        print(f"Failed to start {backup_type} backup for {client_name}. Error: {result.stderr}")
        logging.error(f"Failed to start {backup_type} backup for {client_name}. Error: {result.stderr}")

def backup_task(backup_config):
    """Performs the entire backup task from checking/installing client to starting backups."""
    check_and_install_urbackup_client(backup_config)
    setup_backup_dirs(backup_config)
    initiate_backup(backup_config['type'], backup_config['name'])
    
def start_daemon(config_path):
    global observer
    config = load_config(config_path)
    tasks = config['tasks']
    observer = Observer()
    
    for task in tasks:
        if task['type'] == 'file-organization':
            observer.schedule(ChangeHandler(tasks), os.path.abspath(task['source']), recursive=True)
    
    # Start backup scheduling in a separate thread if 'backup' is defined in the config
    if 'backup' in config:
        backup_thread = Thread(target=backup_task, args=(config,))
        backup_thread.start()

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
    parser.add_argument('action', choices=['start', 'stop', 'generate'], help='Dirconfig actions to perform')
    # Default to 'config.yaml' in the current working directory if not specified
    parser.add_argument('--config', help='Path to the configuration file', default='config.yaml')
    parser.add_argument('--log', help='Path to the log file', default='dirconfig.log')
    parser.add_argument('--pid', help='Path to the PID file', default='dirconfig.pid')
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
    elif args.action == 'generate':
        with open('config.yaml', 'w') as f:
            f.write("tasks:\n  - type: file-organization\n    source: './source'\n    rules:\n      - extension: .pdf, .doc, .docx\n        destination: 'documents'\n      - extension: .jpg, .jpeg\n        destination: 'images'\n")
        print("Sample configuration file generated: config.yaml")
        logging.info("Sample configuration file generated: config.yaml")

if __name__ == "__main__":
    main()
