./deploy.sh int us-east-1

tox

aws cloudformation delete-stack \
    --stack-name say-it-int \
    --region us-east-1 \


