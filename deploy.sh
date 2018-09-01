[ -z "$1" ] && echo "Stage argument is required." && exit 1

stage=$1
stack_name=say-it-$stage

sam validate

sam package \
   --template-file template.yaml \
   --s3-bucket say-it-build \
   --output-template-file serverless-output.yaml \
   --region us-east-1 

sam deploy \
   --template-file serverless-output.yaml \
   --stack-name $stack_name \
   --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
   --region us-east-1 \
   --parameter-overrides \
        StageName=$stage \
        TableName=say-it-messages \
        BucketName=say-it-messages
