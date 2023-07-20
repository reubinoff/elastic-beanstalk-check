"""
Test class for get_environment_version function"""

import unittest
import os
from unittest.mock import patch, MagicMock
from action import (
    get_environment_version,
    EnvironmentStatus,
    READY_STATUS,
    main,
    set_output_env_vars
)

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

class TestMain(unittest.TestCase):
    """
    Test class for main function"""
    @patch('action.Session')
    def test_main(self, mock_session):
        """
        Test main function
        """
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client

        env_name = 'my-environment'
        app_version_label = 'v1.0.0'
        timeout = 60
        region = 'us-west-2'

        # Set up mock environment status
        mock_env_status = EnvironmentStatus(
            version_label=app_version_label,
            status='Ready',
            health_status='Ok'
        )
        mock_get_env_version = MagicMock(return_value=mock_env_status)

        # Set up mock time
        mock_time = MagicMock()
        mock_time.time.side_effect = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

        with patch('action.get_environment_version', mock_get_env_version), \
             patch('action.time', mock_time):
            # Call main function
            os.environ['INPUT_REGION'] = region
            os.environ['INPUT_TIMEOUT'] = str(timeout)
            os.environ['INPUT_ENV-NAME'] = env_name
            os.environ['INPUT_APP-VERSION-LABEL'] = app_version_label
            main()

        # Check output
        self.assertEqual(os.environ['OUTPUT_HEALTH_STATUS'], 'Ok')
        self.assertEqual(os.environ['OUTPUT_VERSION_LABEL'], app_version_label)
        self.assertEqual(os.environ['OUTPUT_STATUS'], 'Ready')

class TestSetOutputEnvVars(unittest.TestCase):
    """
    Test class for set_output_env_vars function"""
    def test_set_output_env_vars(self):
        """
        Test set_output_env_vars function
        """
        env_status = EnvironmentStatus(
            version_label='v1.0.0',
            status='Ready',
            health_status='Ok'
        )

        set_output_env_vars(env_status)

        self.assertEqual(os.environ['OUTPUT_HEALTH_STATUS'], env_status.health_status)
        self.assertEqual(os.environ['OUTPUT_VERSION_LABEL'], env_status.version_label)
        self.assertEqual(os.environ['OUTPUT_STATUS'], env_status.status)
