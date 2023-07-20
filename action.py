"""
This module contains functions for interacting with Elastic Beanstalk environments.
"""

import os
import sys
import time
from dataclasses import dataclass
from boto3.session import Session
from botocore.exceptions import NoCredentialsError


READY_STATUS = "Ready"
TIME_SLEEP = int(os.environ.get('TIME_SLEEP', '5'))


@dataclass
class EnvironmentStatus:
    """
    Dataclass for storing environment status"""
    version_label: str
    status: str
    health_status: str

    def __str__(self) -> str:
        return f"""EnvironmentStatus(version_label={self.version_label},
                 status={self.status}, health_status={self.health_status})"""


def get_environment_version(env_name, client) -> EnvironmentStatus:
    """
    Get environment version from Elastic Beanstalk"""
    response = client.describe_environments(
        EnvironmentNames=[
            env_name,
        ]
    )
    if len(response.get("Environments")) == 0:
        print(f"Environment {env_name} not found")
        sys.exit(1)
    version_label = response.get("Environments")[0].get("VersionLabel")
    status = response.get("Environments")[0].get("Status")
    health_status = response.get("Environments")[0].get("HealthStatus")
    env_status = EnvironmentStatus(version_label, status, health_status)
    print(str(env_status))
    return env_status


def is_env_ready(env_status: EnvironmentStatus, app_version_label: str) -> bool:
    """
    Check if environment is ready"""
    print(f"Checking if environment {env_status} is ready. Expected version: {app_version_label}")
    version_is_ok = env_status.version_label == app_version_label and (app_version_label is not None or app_version_label != "")
    if app_version_label is None or app_version_label == "":
        version_is_ok = True    # no version check required
    print(f"Version is ok: {version_is_ok}")
    status_is_ok = env_status.status == READY_STATUS
    print(f"Status is ok: {status_is_ok}")
    return version_is_ok and status_is_ok

def set_output(name, value):
    """
    Set output environment variable"""
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output_file:
        print(f'{name}={value}', file=output_file)

def set_output_env_vars(env_status: EnvironmentStatus):
    """
    Set output environment variables"""
    set_output('health-status', env_status.health_status)
    set_output('version-label', env_status.version_label)
    set_output('status', env_status.status)

def main(time_sleep=TIME_SLEEP) -> bool:
    """
    Main function for action
    """
    region = os.environ['INPUT_REGION']
    timeout = int(os.environ.get('INPUT_TIMEOUT', '60'))
    env_name = os.environ['INPUT_ENV-NAME']
    app_version_label = os.environ['INPUT_APP-VERSION-LABEL']
    timeout = int(timeout)
    start = time.time()

    session = Session(region_name=region)
    client = session.client('elasticbeanstalk')

    env_status = get_environment_version(env_name, client)
    while is_env_ready(env_status, app_version_label) is False and (time.time() - start) < timeout:
        time.sleep(time_sleep)
        env_status = get_environment_version(env_name, client)

    set_output_env_vars(env_status)

    if is_env_ready(env_status, app_version_label) is False:
        print(f"""Fail. Expected version {app_version_label}
               but got {env_status.version_label}. Status: {env_status.status}""")
        return False

    return True


if __name__ == "__main__":
    try:
        RESULT = main()
        if RESULT is False:
            sys.exit(1)
    except NoCredentialsError as creds_ex:
        print(f"Failed to get AWS credentials: {creds_ex}")
        print("Did you set the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables?")
        sys.exit(1)
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        sys.exit(1)
    sys.exit(0)
