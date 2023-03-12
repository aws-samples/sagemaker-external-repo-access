# Clean up
---

You must clean up provisioned resources to avoid charges in your AWS account.

## Step 1: Revoke GitHub Personal Access Token

GitHub PATs are configured with an expiration value. If you want to ensure that your PAT cannot be used for programmatic access to your internal private GitHub repository before it reaches its expiry, you can revoke the PAT by following [GitHub's instructions](https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/reviewing-and-revoking-personal-access-tokens-in-your-organization).

## Step 2: Clean Up SageMaker Studio MLOps Projects

SageMaker Studio projects and corresponding S3 buckets with project and pipeline artifacts will incur a cost in your AWS account. To delete your SageMaker Studio Domain and corresponding applications, notebooks, and data, please following the instructions in the [SageMaker Developer Guide](https://docs.aws.amazon.com/sagemaker/latest/dg/gs-studio-delete-domain.html).

## Step 3: Delete `external-repo-access.yaml` CloudFormation Stack
The following commands use the default stack name. If you customized the stack name, adjust the commands accordingly.

```sh
aws cloudformation delete-stack --stack-name external-repo-access
aws cloudformation wait stack-delete-complete --stack-name external-repo-access
```

---

[Back to README](../README.md)

---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
