# dirconfig 📂
 Configure what files should be in what folders using an easy-to-read YAML config file.

![PyPI](https://img.shields.io/pypi/v/dirconfig)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dirconfig)
![PyPI - License](https://img.shields.io/pypi/l/dirconfig)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/judahpaul16/dirconfig/workflow.yaml)

## Features

- **File Organization**: Automatically move files based on their extension from one directory to another.
- **Notification System** (Future Feature): Get notified regarding specific events specified in the configuration file.
- **Automated Backups** (Future Feature): Set up scheduled backups for important directories.

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

This command starts **dirconfig**, which then operates in the background. It will watch the source directories specified in your `config.yml` for any changes, organizing files according to your predefined rules.

To run **dirconfig** as a separate process, use the following command:

```sh
dirconfig start &
```

### Stopping dirconfig

To stop the **dirconfig** daemon, execute:

```sh
dirconfig stop
```

This command stops the background process of **dirconfig**, halting the monitoring and file organization tasks.

### Advanced Management

For long-term operation or deployment, integrating **dirconfig** with system services or process managers can offer more graceful management, including automatic restarts, logging, and simplified start/stop operations.

## Extending dirconfig

**dirconfig** welcomes enhancements and customization. If you're interested in adding new features or improving the tool, consider contributing to the source code. Your input and contributions are highly appreciated.

## License

**dirconfig** is licensed under the MIT License. See the `LICENSE` file for more details.
