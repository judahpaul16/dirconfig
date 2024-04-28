# dirconfig 📂

[![PyPI](https://img.shields.io/pypi/v/dirconfig)](https://pypi.org/project/dirconfig/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dirconfig)
[![PyPI - License](https://img.shields.io/pypi/l/dirconfig)](LICENSE)
[![Coverage](https://coveralls.io/repos/github/judahpaul16/dirconfig/badge.svg?branch=main)](https://coveralls.io/github/judahpaul16/dirconfig?branch=main)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/judahpaul16/dirconfig/workflow.yaml)](https://github.com/judahpaul16/dirconfig/actions)

 Configure what files should be in what folders using an easy-to-read YAML config file.

## Features

- [x] **File Organization**: Automatically move files based on their extension from one directory to another.
- [x] **Automated Backups**: Set up scheduled backups for important directories using [urbackup](https://github.com/uroni/urbackup-server-python-web-api-wrapper).
- [ ] **Notification System**: Get notified regarding specific events specified in the configuration file.

## Installation

Install **dirconfig** using pip:

```sh
pip install dirconfig
```

## Configuration

Create a `config.yml` file in your working directory with your automation tasks. Here's an example configuration that organizes `.jpg` and `.pdf` files into separate directories:

```yaml
tasks:
  - name: Organize Downloads
    type: file-organization
    source: /path/to/your/source/directory
    rules:
      - extension: .jpg
        destination: /path/to/your/destination/for/images
      - extension: .pdf
        destination: /path/to/your/destination/for/documents
backup:
  - name: Backup Important Files
    type: incremental-file # incremental-image, full-file, full-image
    schedule: daily # weekly, monthly
    retention: 7 # number of days to keep backups
    connection:
      server: http://your-backup-server:55414
      username: foo
      password: bar
    directories:
      - /path/to/your/important/directory
      - /path/to/another/important/directory
```

## Usage

**dirconfig** is designed to run as a daemon, monitoring specified directories and automatically organizing files according to the configurations defined in your `config.yml` file.

You can generate a sample `config.yml` file using the following command:

```sh
dirconfig generate
```

### Starting dirconfig

To initiate **dirconfig** and begin the monitoring process, use the following command:

```sh
dirconfig start
```

This command starts **dirconfig**, which operates in the background. It will watch the source directories specified in your `config.yml` for any changes, organizing files according to your predefined rules.

Alternatively, to run **dirconfig** as a separate process, use the following command:

```sh
dirconfig start &
```

### Stopping dirconfig

To stop the **dirconfig** daemon, execute:

```sh
dirconfig stop
```
This command stops the background process of **dirconfig**, halting the monitoring and file organization tasks.

### Command Line Options
```sh
usage: dirconfig [-h] [--config CONFIG] [--log LOG] [--pid PID] {start,stop,generate}

dirconfig Daemon

positional arguments:
  {start,stop,generate}
                        Dirconfig actions to perform

options:
  -h, --help            show this help message and exit
  --config CONFIG       Path to the configuration file
  --log LOG             Path to the log file
  --pid PID             Path to the PID file
```

### Advanced Management

For long-term operation or deployment, integrating **dirconfig** with system services or process managers can offer more graceful management, including automatic restarts, logging, and simplified start/stop operations.

## Extending dirconfig

**dirconfig** welcomes enhancements and customization. If you're interested in adding new features or improving the tool, consider contributing to the source code. Your input and contributions are highly appreciated.

## Urbackup Documentation
For more information on the Urbackup API, please refer to these resources:
* *[Urbackup Python API Wrapper](https://github.com/uroni/urbackup-server-python-web-api-wrapper)*
* *[Urbackup Backend ClientCTL](https://github.com/uroni/urbackup_backend/tree/dev/clientctl)*

*Important Note: For Windows the command-line tool is `urbackupclient_cmd`. Mac and Linux use `urbackupclientctl`.

Command Line Options for `urbackupclientctl` are as follows:

```sh
USAGE:

        urbackupclientctl [--help] [--version] <command> [<args>]

Get specific command help with urbackupclientctl <command> --help

        urbackupclientctl start
                Start an incremental/full image/file backup

        urbackupclientctl status
                Get current backup status

        urbackupclientctl browse
                Browse backups and files/folders in backups

        urbackupclientctl restore-start
                Restore files/folders from backup

        urbackupclientctl set-settings
                Set backup settings

        urbackupclientctl reset-keep
                Reset keeping files during incremental backups

        urbackupclientctl add-backupdir
                Add new directory to backup set

        urbackupclientctl list-backupdirs
                List directories that are being backed up

        urbackupclientctl remove-backupdir
                Remove directory from backup set
```

## License

**dirconfig** is licensed under the MIT License. See the `LICENSE` file for more details.
