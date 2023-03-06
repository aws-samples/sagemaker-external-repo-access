# If not already cloned, clone remote repository and change working directory to CloudFormation folder
git clone https://github.com/aws-samples/sagemaker-external-repo-access.git
cd sagemaker-external-repo-access/cfn/

# Use defaults or provide your own parameter values
STACK_NAME="external-repo-access"
CODEPIPELINE_NAME="external-repo-pipeline"

# Below parameter values acquired from 'Gather Private GitHub Repository Configuration Settings' pre-deployment section
GITHUB_BRANCH=<private repository branch>
GITHUB_OWNER=<private repository owner>
GITHUB_REPO=<private repository name>
GITHUB_TOKEN=<AWS Secrets Manager name for private repository PAT>

# Below parameter values acquired from 'Establish VPC Networking Configuration' pre-deployment section
VPC_ID=<vpc with NGW and IGW>
SUBNET_ID1=<private subnet 1 from above VPC>
SUBNET_ID2=<private subnet 2 from above VPC>

aws cloudformation create-stack \
--stack-name ${STACK_NAME} \
--template-body file://$(pwd)/cfn/external-repo-access.yaml \
--parameters ParameterKey=SourceActionVersion,ParameterValue=${SOURCE_VERSION} \
ParameterKey=CodePipelineName,ParameterValue=${CODEPIPELINE_NAME} \
ParameterKey=GitHubBranch,ParameterValue=${GITHUB_BRANCH} \
ParameterKey=GitHubOwner,ParameterValue=${GITHUB_OWNER} \
ParameterKey=GitHubRepo,ParameterValue=${GITHUB_REPO} \
ParameterKey=GitHubToken,ParameterValue=${GITHUB_TOKEN} \
ParameterKey=RepoCloneLambdaSubnet,ParameterValue=${SUBNET_ID1}\\,${SUBNET_ID2} \
ParameterKey=RepoCloneLambdaVpc,ParameterValue=${VPC_ID} \
--capabilities CAPABILITY_IAM
