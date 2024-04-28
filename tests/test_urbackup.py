import unittest
from unittest.mock import patch, MagicMock
from dirconfig import backup_task, initiate_backup, check_and_install_urbackup_client, setup_backup_dirs, get_urbackup_command

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

    @patch('dirconfig.subprocess.run')
    def test_check_and_install_urbackup_client(self, mock_run):
        mock_run.return_value = {'stdout': "Client installed.", 'stderr': "", 'returncode': 0}
        check_and_install_urbackup_client(self.backup_config)
        mock_run.assert_called_with([get_urbackup_command(), "status"], capture_output=True, text=True)

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
