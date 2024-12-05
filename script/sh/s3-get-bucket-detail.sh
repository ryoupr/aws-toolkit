#!/bin/bash

# S3 bucket name input
read -p "Enter S3 bucket name: " BUCKET_NAME

# Get bucket location
BUCKET_LOCATION=$(aws s3api get-bucket-location --bucket "$BUCKET_NAME" --query "LocationConstraint" --output text)

# Get bucket policy
BUCKET_POLICY=$(aws s3api get-bucket-policy --bucket "$BUCKET_NAME" --query "Policy" --output text 2>/dev/null)

# Get bucket ACL
BUCKET_ACL=$(aws s3api get-bucket-acl --bucket "$BUCKET_NAME" --output json)

# Get bucket versioning status
BUCKET_VERSIONING=$(aws s3api get-bucket-versioning --bucket "$BUCKET_NAME" --output json)

# Get bucket tags
BUCKET_TAGGING=$(aws s3api get-bucket-tagging --bucket "$BUCKET_NAME" --output json 2>/dev/null)

# Print bucket details
echo -e "\nBucket Name: $BUCKET_NAME"
echo -e "\nBucket Location: $BUCKET_LOCATION"

if [ -z "$BUCKET_POLICY" ]; then
  echo -e "\nBucket Policy: No policy attached"
else
  echo -e "\nBucket Policy:"
  echo "$BUCKET_POLICY" | jq .
fi

echo -e "\nBucket ACL:"
echo "$BUCKET_ACL" | jq .

echo -e "\nBucket Versioning Status:"
echo "$BUCKET_VERSIONING" | jq .

if [ -z "$BUCKET_TAGGING" ]; then
  echo -e "\nBucket Tags: No tags attached"
else
  echo -e "\nBucket Tags:"
  echo "$BUCKET_TAGGING" | jq .
fi
