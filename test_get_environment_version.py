"""
Test class for get_environment_version function"""

import unittest
from unittest.mock import patch
from action import get_environment_version, EnvironmentStatus, READY_STATUS


class TestGetEnvironmentVersion(unittest.TestCase):
    """
    Test class for get_environment_version function"""
    @patch('boto3.session.Session')
    def test_get_environment_version_expected(self, mock_client):
        """
        Test get_environment_version function with expected response"""
        mock_eb = mock_client.return_value
        mock_eb.describe_environments.return_value = {
            'Environments': [
                {
                    'VersionLabel': 'v1.0.0',
                    'Status': 'Ready',
                }
            ]
        }
        env_name = 'my-environment'
        expected_version = 'v1.0.0'
        env_status: EnvironmentStatus = get_environment_version(env_name, client=mock_eb)
        self.assertEqual(env_status.version_label, expected_version)
        self.assertEqual(env_status.status, READY_STATUS)
        mock_eb.describe_environments.assert_called_once_with(
            EnvironmentNames=[env_name]
        )

    @patch('boto3.session.Session')
    def test_get_environment_version_not_found(self, mock_client):
        """
        Test get_environment_version function with environment not found
        """
        mock_eb = mock_client.return_value
        mock_eb.describe_environments.return_value = {
            'Environments': []
        }
        env_name = 'my-environment'
        with self.assertRaises(SystemExit) as assert_exit:
            get_environment_version(env_name, client=mock_eb)
        self.assertEqual(assert_exit.exception.code, 1)
        mock_eb.describe_environments.assert_called_once_with(
            EnvironmentNames=[env_name]
        )
