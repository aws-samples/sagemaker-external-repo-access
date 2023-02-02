# If not already cloned, clone remote repository and change working directory to CloudFormation folder
git clone https://github.com/kyleblocksom/sagemaker-external-repo-access.git
cd sagemaker-external-repo-access/

# Use defaults or provide your own parameter values
STACK_NAME="external-repo-access"
CODEPIPELINE_NAME="external-repo-pipeline"
SOURCE_PROVIDER='CustomGitSource'
SOURCE_VERSION='1'

# Below parameter values acquired from 'Gather Third-Party Repository Configuration Settings' pre-deployment section
GIT_BRANCH=<remote repo branch name>
GIT_URL=<remote repo Git URL>
GIT_WEBHOOK_IP=<webhook IP used by remote repo> #https://api.github.com/meta

# Below parameter values acquired from 'Establish VPC Networking Configuration' pre-deployment section
VPC_ID=<vpc with NGW and IGW>
SUBNET_ID1=<private subnet 1 from above VPC>
SUBNET_ID2=<private subnet 2 from above VPC>

# Below parameter values acquired from 'Create SSH Key Pair' pre-deployment section
SECRETS_MANAGER_SSH_ARN=<ARN of SSH Secret>

# Below parameter values acquired from 'Create S3 and Upload Lambda Function' pre-deployment section
LAMBDA_S3_BUCKET=<S3 bucket with compressed Lambda code>
LAMBDA_S3_KEY=<S3 key of compressed Lambda code>

aws cloudformation create-stack \
--stack-name ${STACK_NAME} \
--template-body file://../cfn/external-repo-access.yaml \
--parameters ParameterKey=SourceActionVersion,ParameterValue=${SOURCE_VERSION} \
ParameterKey=SourceActionProvider,ParameterValue=${CustomSourceForGit} \
ParameterKey=GitBranch,ParameterValue=${GIT_BRANCH} \
ParameterKey=GitUrl,ParameterValue=${GIT_URL} \
ParameterKey=GitWebHookIpAddress,ParameterValue=${GIT_WEBHOOK_IP} \
ParameterKey=SecretsManagerArnForSSHPrivateKey,ParameterValue=${SECRETS_MANAGER_SSH_ARN} \
ParameterKey=RepoCloneLambdaSubnet,ParameterValue=${SUBNET_ID1}\\,${SUBNET_ID2} \
ParameterKey=RepoCloneLambdaVpc,ParameterValue=${VPC_ID} \
ParameterKey=LambdaCodeS3Bucket,ParameterValue=${LAMBDA_S3_BUCKET} \
ParameterKey=LambdaCodeS3Key,ParameterValue=${LAMBDA_S3_KEY} \
ParameterKey=CodePipelineName,ParameterValue=${CODEPIPELINE_NAME} \
--capabilities CAPABILITY_IAM