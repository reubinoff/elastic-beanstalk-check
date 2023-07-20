import unittest
from unittest.mock import patch
from action import get_environment_version

class TestGetEnvironmentVersion(unittest.TestCase):
    @patch('action.boto3.client')
    def test_get_environment_version(self, mock_client):
        mock_eb = mock_client.return_value
        mock_eb.describe_environments.return_value = {
            'Environments': [
                {
                    'VersionLabel': 'v1.0.0'
                }
            ]
        }
        env_name = 'my-environment'
        expected_version = 'v1.0.0'
        actual_version = get_environment_version(env_name)
        self.assertEqual(actual_version, expected_version)
        mock_eb.describe_environments.assert_called_once_with(
            EnvironmentNames=[env_name]
        )