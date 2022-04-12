## Create stack
```
aws cloudformation create-stack \
--stack-name lambda-cicd-post \
--template-body file://.cloudformation/main.yml \
--parameters \
ParameterKey=FunctionName,ParameterValue=<LAMBDA_FUNCTION_NAME> \
ParameterKey=Environment,ParameterValue=<ENVIRONMENT> \
ParameterKey=GitHubUser,ParameterValue=<GITHUB_USER> \
ParameterKey=GitHubRepo,ParameterValue=<REPO_NAME> \
ParameterKey=GitHubOAuthToken,ParameterValue=<GITHUB_OAUTH_TOKEN> \
--region us-east-1 \
--capabilities CAPABILITY_IAM
```
