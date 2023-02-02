import time
import logging
import json
import boto3
import os
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Resource Variable Definitions
logger = logging.getLogger()
logger.setLevel(logging.INFO)
codebuild_client = boto3.client('codebuild')
codepipeline_client = boto3.client('codepipeline')

def lambda_handler(event, context):
    try:
        logger.info(json.dumps(event)) # 
        CUSTOM_ACTION_PROVIDER = event['detail']['type']['provider']
        CUSTOM_ACTION_VERSION = event['detail']['type']['version']
        CUSTOM_ACTION_OWNER = event['detail']['type']['owner']
        CUSTOM_ACTION_CATEGORY = event['detail']['type']['category']
        pipelineName = event['resources'][0].split(":")[5]
        counter = 0
        while counter < 10:  # capped this, so it just fails if it takes too long
            time.sleep(5)
            logger.info(counter)
            counter = counter + 1
            polled_jobs = codepipeline_client.poll_for_jobs(
                actionTypeId={
                    'category': CUSTOM_ACTION_CATEGORY,
                    'owner': CUSTOM_ACTION_OWNER,
                    'provider': CUSTOM_ACTION_PROVIDER,
                    'version': CUSTOM_ACTION_VERSION
                },
                maxBatchSize=1,
                queryParam={
                    'PipelineName': pipelineName
                })
            if (counter == 10 and polled_jobs['jobs'] == []):
                raise Exception ("Please check if the Pipeline Name in the custom configuration is same as " + pipelineName)
            if not polled_jobs['jobs'] == []:
                break
        logger.info(polled_jobs)
        if not polled_jobs['jobs'] == []:
            job = polled_jobs['jobs'][0]
            codepipeline_client.acknowledge_job(
                jobId=job['id'],
                nonce=job['nonce']
            )
            try:
                CodePipelineArtifactBucketPathsplit = job['data']['outputArtifacts'][0]['location']['s3Location'][
                    'objectKey'].split("/")
                client = boto3.client(service_name='codebuild')
                new_build = client.start_build(projectName=os.getenv('RepoCloneCodeBuild'),
                                            environmentVariablesOverride=[
                                                {
                                                    'name': 'GitUrl',
                                                    'value': job['data']['actionConfiguration']['configuration'][
                                                        'GitUrl'],
                                                    'type': 'PLAINTEXT'
                                                },
                                                {
                                                    'name': 'Branch',
                                                    'value': job['data']['actionConfiguration']['configuration'][
                                                        'Branch'],
                                                    'type': 'PLAINTEXT'
                                                },
                                                {
                                                'name': 'SSHSecretKeyName',
                                                'value': job['data']['actionConfiguration']['configuration']['SSHSecretKeyName'],
                                                'type': 'PLAINTEXT'
                                                },
                                                {
                                                    'name': 'CodePipelineArtifactBucket',
                                                    'value': job['data']['outputArtifacts'][0]['location']['s3Location'][
                                                        'bucketName'],
                                                    'type': 'PLAINTEXT'
                                                },
                                                {
                                                    'name': 'CodePipelineArtifactBucketPath',
                                                    'value': CodePipelineArtifactBucketPathsplit[0] + "/" +
                                                                CodePipelineArtifactBucketPathsplit[1],
                                                    'type': 'PLAINTEXT'
                                                },
                                                {
                                                    'name': 'CodePipelineArtifactBucketObjectKey',
                                                    'value': CodePipelineArtifactBucketPathsplit[2],
                                                    'type': 'PLAINTEXT'
                                                },
                                                {
                                                    'name': 'CodePipelineArtifactAccessKey',
                                                    'value': job['data']['artifactCredentials']['accessKeyId'],
                                                    'type': 'PLAINTEXT'
                                                },
                                                {
                                                    'name': 'CodePipelineArtifactSecretAccessKey',
                                                    'value': job['data']['artifactCredentials']['secretAccessKey'],
                                                    'type': 'PLAINTEXT'
                                                },
                                                {
                                                    'name': 'CodePipelineArtifactSessionToken',
                                                    'value': job['data']['artifactCredentials']['sessionToken'],
                                                    'type': 'PLAINTEXT'
                                                },
                                                {
                                                    'name': 'CodePipelineArtifactKMSKeyId',
                                                    'value': job['data']['encryptionKey']['id'],
                                                    'type': 'PLAINTEXT'
                                                },
                                                
                                            ])
                buildId = new_build['build']['id']
                logger.info(f"CodeBuild Build Id is {buildId}")
                buildStatus = 'NOT_KNOWN'
                counter = 0
                while (counter < 60 and buildStatus != 'SUCCEEDED'):  # capped this, so it just fails if it takes too long
                    logger.info("Waiting for Codebuild to complete")
                    time.sleep(5)
                    logger.info(counter)
                    counter = counter + 1
                    theBuild = client.batch_get_builds(ids=[buildId])
                    print(theBuild)
                    buildStatus = theBuild['builds'][0]['buildStatus']
                    logger.info(f"CodeBuild Build Status is {buildStatus}")
                    if buildStatus == 'SUCCEEDED':
                        EnvVariables = theBuild['builds'][0]['exportedEnvironmentVariables']
                        commit_id = [env for env in EnvVariables if env['name'] == 'GIT_COMMIT_ID'][0]['value']
                        commit_message = [env for env in EnvVariables if env['name'] == 'GIT_COMMIT_MSG'][0]['value'] 
                        current_revision = {
                                            'revision': "Git Commit Id:" + commit_id,
                                            'changeIdentifier': 'GitLab',
                                            'revisionSummary': "Git Commit Message:" + commit_message
                                          }
                        outputVariables = {
                            'commit_id': "Git Commit Id:" + commit_id,
                            'commit_message': "Git Commit Message:" + commit_message
                        }
                        codepipeline_client.put_job_success_result(jobId=job['id'], currentRevision=current_revision, outputVariables=outputVariables)
                        break
                    elif buildStatus == 'FAILED' or buildStatus == 'FAULT' or buildStatus == 'STOPPED' or buildStatus == 'TIMED_OUT':
                        codepipeline_client.put_job_failure_result(jobId=job['id'],
                                                                failureDetails={
                                                                    'type': 'JobFailed',
                                                                    'message': 'CodeBuild exception with buildStatus ' + buildStatus
                                                                })
                        break
            except Exception as e:
                logger.info(f"Error in Function: {e}")
                codepipeline_client.put_job_failure_result(
                    jobId=job['id'],
                    failureDetails={
                        'type': 'JobFailed',
                        'message': f"Exception in action process: {e}"
                    }
                )
    except Exception as e:
                logger.info(f"Error in Function: {e}")
                codepipeline_client.stop_pipeline_execution(
                    pipelineName=event['resources'][0].split(":")[5],
                    pipelineExecutionId=event['detail']['execution-id'],
                    abandon=True,
                    reason=str(e)
            )