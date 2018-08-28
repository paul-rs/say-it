sam validate

sam package \
   --template-file template.yaml \
   --s3-bucket say-it-build \
   --output-template-file serverless-output.yaml \
   --region us-east-1 

sam deploy \
   --template-file serverless-output.yaml \
   --stack-name say-it \
   --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
   --region us-east-1
