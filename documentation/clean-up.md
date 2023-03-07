# Clean up
---

You must clean up provisioned resources to avoid charges in your AWS account.

## Step 1: Revoke GitHub Personal Access Token

GitHub PATs are configured with an expiration value. If you want to ensure that your PAT cannot be used for programmatic access to your internal private GitHub repository before it reaches its expiry, you can revoke the PAT by following [GitHub's instructions](https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/reviewing-and-revoking-personal-access-tokens-in-your-organization).

## Step 2: Clean Up SageMaker Studio MLOps Projects

SageMaker Studio projects and corresponding S3 buckets with project and pipeline artifacts will incur a cost in your AWS account. To delete your SageMaker Studio Domain and corresponding applications, notebooks, and data, please following the instructions in the (SageMaker Developer Guide) [https://docs.aws.amazon.com/sagemaker/latest/dg/gs-studio-delete-domain.html].

## Step 2: Empty data and model S3 buckets
CloudFormation `delete-stack` doesn't remove any non-empty S3 bucket. You must empty data science environment S3 buckets for data and models before you can delete the data science environment stack.

Set `AWS_ACCOUNT_ID` variable. You must be logged in the terminal under the same account where the data science environment installed:
```sh
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
```

First, remove VPC-only access policy from the data and model bucket to be able to delete objects from a CLI terminal.
```sh
ENV_NAME=<use default name `sm-mlops` or your data science environment name you chosen when you created the stack>
aws s3api delete-bucket-policy --bucket $ENV_NAME-dev-${AWS_DEFAULT_REGION}-${AWS_ACCOUNT_ID}-data
aws s3api delete-bucket-policy --bucket $ENV_NAME-dev-${AWS_DEFAULT_REGION}-${AWS_ACCOUNT_ID}-models
```

❗ **This is a destructive action. The following command will delete all files in the data and models S3 buckets** ❗  

Now you can empty the buckets:
```sh
aws s3 rm s3://$ENV_NAME-dev-$AWS_DEFAULT_REGION-${AWS_ACCOUNT_ID}-data --recursive
aws s3 rm s3://$ENV_NAME-dev-$AWS_DEFAULT_REGION-${AWS_ACCOUNT_ID}-models --recursive
```

## Step 3: Delete data science environment CloudFormation stacks
Depending on the [deployment type](deployment.md#deployment-options), you must delete the corresponding CloudFormation stacks. The following commands use the default stack names. If you customized the stack names, adjust the commands correspondingly with your stack names.

### Delete data science environment quickstart
```sh
aws cloudformation delete-stack --stack-name ds-quickstart
aws cloudformation wait stack-delete-complete --stack-name ds-quickstart
aws cloudformation delete-stack --stack-name sagemaker-mlops-package-cfn
```

### Delete two-step deployment via CloudFormation
```sh
aws cloudformation delete-stack --stack-name sm-mlops-env
aws cloudformation wait stack-delete-complete --stack-name sm-mlops-env
aws cloudformation delete-stack --stack-name sm-mlops-core 
aws cloudformation wait stack-delete-complete --stack-name sm-mlops-core
aws cloudformation delete-stack --stack-name sagemaker-mlops-package-cfn
```

### Delete two-step deployment via CloudFormation and AWS Service Catalog
1. Assume DS Administrator IAM role via link in the CloudFormation output.
```sh
aws cloudformation describe-stacks \
    --stack-name sm-mlops-core  \
    --output table \
    --query "Stacks[0].Outputs[*].[OutputKey, OutputValue]"
```

2. In AWS Service Catalog console go to the [_Provisioned Products_](https://console.aws.amazon.com/servicecatalog/home?#provisioned-products), select your product and click **Terminate** from the **Action** button. Wait until the delete process ends.

![terminate-product](../img/terminate-product.png)

![product-terminate](../img/product-terminate.png)

3. Delete the core infrastructure CloudFormation stack:
```sh
aws cloudformation delete-stack --stack-name sm-mlops-core
aws cloudformation wait stack-delete-complete --stack-name sm-mlops-core
aws cloudformation delete-stack --stack-name sagemaker-mlops-package-cfn
```
---

[Back to README](../README.md)

---

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
