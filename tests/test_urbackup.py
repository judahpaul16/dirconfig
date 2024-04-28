from unittest.mock import patch, MagicMock, create_autospec, call
import subprocess
import unittest
import os

from dirconfig import \
    backup_task, \
    initiate_backup, \
    check_and_install_urbackup_client, \
    setup_backup_dirs, \
    get_urbackup_command, \
    get_installer_filename, \
    MODULE_DIR


class TestBackupFunctions(unittest.TestCase):
    def setUp(self):
        self.backup_config = {
            'connection': {
                'server': 'http://example.com',
                'username': 'user',
                'password': 'password'
            },
            'name': 'client',
            'directories': ['/path/to/backup'],
            'type': 'incremental-file'
        }

    @patch('os.name', 'nt')
    @patch('subprocess.run')
    @patch('dirconfig.get_installer_filename', return_value='urbackup_client_installer.exe')
    @patch('dirconfig.get_urbackup_command', return_value='urbackupclient_cmd')
    @patch('urbackup.urbackup_server.login', return_value=True)
    @patch('urbackup.urbackup_server.download_installer', return_value=True)
    def test_check_and_install_urbackup_client_windows(self, mock_download_installer, mock_login, mock_get_urbackup_command, mock_get_installer_filename, mock_run):
        mock_completed_process = create_autospec(subprocess.CompletedProcess, instance=True)
        mock_completed_process.stdout = "Client not installed"
        mock_completed_process.stderr = ""
        mock_completed_process.returncode = 1
        mock_run.return_value = mock_completed_process

        check_and_install_urbackup_client(self.backup_config)

        powershell_command = """
            $newPathEntry = 'C:\\Program Files\\UrBackup\\';
            $envPath = [Environment]::GetEnvironmentVariable("PATH", "User");
            if ($envPath -split ';' -contains $newPathEntry) {
                Write-Output 'Already in PATH'
            } else {
                $newPath = $envPath + ';' + $newPathEntry;
                [Environment]::SetEnvironmentVariable("PATH", $newPath, "User");
                Write-Output 'Added to PATH'
            }
            """.replace('\n', ' ').replace('    ', '')

        expected_calls = [
            call([mock_get_urbackup_command(), "status"], capture_output=True, text=True),
            call([os.path.join(MODULE_DIR, mock_get_installer_filename())]),
            call(['powershell', '-Command', powershell_command], capture_output=True, text=True),
        ]
        mock_run.assert_has_calls(expected_calls, any_order=True)

    @patch('os.name', 'posix')
    @patch('subprocess.run')
    @patch('dirconfig.get_installer_filename', return_value='urbackup_client_installer.sh')
    @patch('dirconfig.get_urbackup_command', return_value='urbackupclientctl')
    @patch('urbackup.urbackup_server.login', return_value=True)
    @patch('urbackup.urbackup_server.download_installer', return_value=True)
    def test_check_and_install_urbackup_client_posix(self, mock_download_installer, mock_login, mock_get_urbackup_command, mock_get_installer_filename, mock_run):
        mock_completed_process = create_autospec(subprocess.CompletedProcess, instance=True)
        mock_completed_process.stdout = "Client not installed"
        mock_completed_process.stderr = ""
        mock_completed_process.returncode = 1
        mock_run.return_value = mock_completed_process

        check_and_install_urbackup_client(self.backup_config)

        expected_calls = [
            call([mock_get_urbackup_command(), "status"], capture_output=True, text=True),
            call(['chmod', '+x', mock_get_installer_filename()]),
            call([os.path.join(MODULE_DIR, mock_get_installer_filename())]),
        ]
        mock_run.assert_has_calls(expected_calls, any_order=True)

    @patch('dirconfig.subprocess.run')
    def test_setup_backup_dirs(self, mock_run):
        mock_run.return_value = MagicMock(stdout="Directory added.", stderr="", returncode=0)
        setup_backup_dirs(self.backup_config)
        mock_run.assert_called_with([get_urbackup_command(), "add-backupdir", "--path", "/path/to/backup"], capture_output=True, text=True)

    @patch('dirconfig.subprocess.run')
    def test_initiate_backup(self, mock_run):
        mock_run.return_value = MagicMock(stdout="Backup initiated.", stderr="", returncode=0)
        initiate_backup(self.backup_config['type'], self.backup_config['name'])
        mock_run.assert_called_with([get_urbackup_command(), "start", "-i", "--non-blocking", "--client", "client"], capture_output=True, text=True)

    @patch('dirconfig.initiate_backup')
    @patch('dirconfig.setup_backup_dirs')
    @patch('dirconfig.check_and_install_urbackup_client')
    def test_backup_task(self, mock_check_and_install_urbackup_client, mock_setup_backup_dirs, mock_initiate_backup):
        backup_task(self.backup_config)
        mock_check_and_install_urbackup_client.assert_called_once_with(self.backup_config)
        mock_setup_backup_dirs.assert_called_once_with(self.backup_config)
        mock_initiate_backup.assert_called_once_with(self.backup_config['type'], self.backup_config['name'])

if __name__ == '__main__':
    unittest.main()
