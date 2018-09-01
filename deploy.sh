[ -z "$1" ] && echo "Stage is required." && exit 1
[ -z "$2" ] && echo "Region Name is required." && exit 1

stage=$1
stack_name=say-it-$stage
region_name=$2

sam validate

sam package \
   --template-file template.yaml \
   --s3-bucket say-it-build \
   --output-template-file serverless-output.yaml \
   --region $region_name

sam deploy \
   --template-file serverless-output.yaml \
   --stack-name $stack_name \
   --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
   --region $region_name \
   --parameter-overrides \
        StageName=$stage \
        TableName=say-it-messages \
        BucketName=say-it-messages
