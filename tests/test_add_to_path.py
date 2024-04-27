from dirconfig import add_to_path
from unittest.mock import patch, MagicMock, ANY
import subprocess

def test_add_to_path_already_in_path(capsys):
    # Mock subprocess.run to simulate the PATH already containing the entry
    mock_run = MagicMock(return_value=subprocess.CompletedProcess(args=['powershell'], returncode=0, stdout='Already in PATH'))
    with patch('subprocess.run', mock_run):
        add_to_path('C:\\Program Files\\UrBackup\\')
        # Check that subprocess.run was called correctly
        mock_run.assert_called_with(
            ["powershell", "-Command", ANY],
            capture_output=True, text=True
        )
        # Check the output handling
        out, _ = capsys.readouterr()
        assert 'Already in PATH' in out

def test_add_to_path_add_success(capsys):
    # Mock subprocess.run to simulate successfully adding to the PATH
    mock_run = MagicMock(return_value=subprocess.CompletedProcess(args=['powershell'], returncode=0, stdout='Added to PATH'))
    with patch('subprocess.run', mock_run):
        add_to_path('C:\\Program Files\\UrBackup\\')
        # Ensure it reports successful addition
        out, _ = capsys.readouterr()
        assert 'Added to PATH' in out

def test_add_to_path_error(capsys):
    # Mock subprocess.run to simulate an error
    mock_run = MagicMock(return_value=subprocess.CompletedProcess(args=['powershell'], returncode=1, stderr='Error occurred'))
    with patch('subprocess.run', mock_run):
        add_to_path('C:\\Program Files\\UrBackup\\')
        # Check error handling
        out, _ = capsys.readouterr()
        assert 'Failed to modify the system PATH:' in out

if __name__ == '__main__':
    add_to_path('C:\\Program Files\\UrBackup\\')