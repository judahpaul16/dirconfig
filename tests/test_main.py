import os
import pytest
import tempfile
import shutil
from unittest.mock import patch
from dirconfig.main import load_config, organize_files, start_daemon, stop_daemon, ChangeHandler

TEST_CONFIG = """
tasks:
  - type: file-organization
    source: "./test_source"
    rules:
      - extension: .txt
        destination: "text_files"
      - extension: .jpg, .jpeg
        destination: "images"
"""

@pytest.fixture
def setup_test_env():
    """
    Sets up a temporary testing environment, including a test config file
    and a test source directory with some files.
    """
    original_dir = os.getcwd()
    test_dir = tempfile.mkdtemp()
    os.chdir(test_dir)

    # Create test config file
    with open('config.yaml', 'w') as f:
        f.write(TEST_CONFIG)

    # Create source directory and test files
    os.mkdir('test_source')
    with open('test_source/test.txt', 'w') as f:
        f.write("This is a test text file.")
    with open('test_source/image.jpg', 'w') as f:
        f.write("This is a test image file.")

    yield test_dir  # Provide the temporary directory to the test

    # Cleanup
    os.chdir(original_dir)
    shutil.rmtree(test_dir)

def test_load_config():
    """
    Tests the load_config function to ensure it correctly loads and parses
    the configuration from a YAML file.
    """
    with tempfile.NamedTemporaryFile('w', delete=False) as tmpfile:
        tmpfile.write(TEST_CONFIG)
        tmpfile.close()  # Close the file to ensure it's written and flushed

        config = load_config(tmpfile.name)
        assert 'tasks' in config, "The configuration should have a 'tasks' key"
        assert len(config['tasks']) > 0, "There should be at least one task in the configuration"

        os.unlink(tmpfile.name)  # Clean up the temporary file

def test_organize_files(setup_test_env):
    """
    Tests the organize_files function to verify it correctly organizes files
    according to the specified rules in the configuration.
    """
    config_path = os.path.join(setup_test_env, 'config.yaml')
    config = load_config(config_path)
    for task in config['tasks']:
        if task['type'] == 'file-organization':
            organize_files(task)

    # Use the setup_test_env path to build the correct assertion paths
    text_file_path = os.path.join(setup_test_env, 'test_source', 'text_files', 'test.txt')
    image_file_path = os.path.join(setup_test_env, 'test_source', 'images', 'image.jpg')

    # Check if the files have been moved to the correct destinations
    assert os.path.exists(text_file_path), "Text file should be moved to 'text_files'"
    assert os.path.exists(image_file_path), "Image file should be moved to 'images'"
