while getopts e: flag
do
    case "${flag}" in
        e) env=${OPTARG};;
    esac
done

if [[ -z "$env" ]]; then
  env=dev
fi

imageName="check-gmail-api:latest"
functionName="check_gmail_api"


docker build \
--platform linux/amd64 . -t ${imageName} && \
docker tag ${imageName} "548616401217.dkr.ecr.us-east-1.amazonaws.com/${imageName}" && \
docker push "548616401217.dkr.ecr.us-east-1.amazonaws.com/${imageName}" && \
aws lambda update-function-code --region us-east-1 --function-name ${functionName} \
    --image-uri "548616401217.dkr.ecr.us-east-1.amazonaws.com/${imageName}" 
