# elastic-beanstalk-check
This GitHub Action checks the status of an Elastic Beanstalk environment and fails if the environment is not ready or if the version label does not match the expected label.

# Usage
To use this action, you can add the following step to your workflow:

```yml
- name: Check Elastic Beanstalk environment
  uses: reubinoff/elastic-beanstalk-check@v1
  with:
    region: us-west-2
    env-name: my-environment
    app-version-label: v1.0.0
    timeout: 300
```

In this example, the **reubinoff/elastic-beanstalk-check** action is used to check the status of an Elastic Beanstalk environment with the name __my-environment__ in the __us-west-2__ region. The action expects the environment to have the version label __v1.0.0__ and will wait up to 300 seconds for the environment to become ready.


# Inputs
This action accepts the following inputs:

* region: The AWS region where the Elastic Beanstalk environment is located.
* env-name: The name of the Elastic Beanstalk environment to check.
* app-version-label: The expected version label of the Elastic Beanstalk environment.
* timeout: The maximum amount of time to wait for the Elastic Beanstalk environment to become ready.

# Outputs
This action does not produce any outputs.

# License
This action is licensed under the MIT License.