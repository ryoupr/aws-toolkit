#!/bin/bash

# ユーザー名またはグループ名を入力
read -p "Enter IAM username or group name: " IAM_ENTITY

# 出力ファイルを初期化
OUTPUT_FILE="result.txt"
> $OUTPUT_FILE

# エンティティが存在するか確認
aws iam get-user --user-name "$IAM_ENTITY" &> /dev/null
USER_EXISTS=$?

aws iam get-group --group-name "$IAM_ENTITY" &> /dev/null
GROUP_EXISTS=$?

if [ $USER_EXISTS -ne 0 ] && [ $GROUP_EXISTS -ne 0 ]; then
  echo "The specified IAM user or group does not exist." | tee -a $OUTPUT_FILE
  exit 1
fi

# ユーザーの場合
if [ $USER_EXISTS -eq 0 ]; then
  echo "Getting attached policies for IAM user: $IAM_ENTITY" | tee -a $OUTPUT_FILE
  aws iam list-attached-user-policies --user-name "$IAM_ENTITY" > attached_policies.json

  echo "Getting inline policies for IAM user: $IAM_ENTITY" | tee -a $OUTPUT_FILE
  aws iam list-user-policies --user-name "$IAM_ENTITY" > inline_policies.json

  INLINE_POLICY_NAMES=$(jq -r '.PolicyNames[]' inline_policies.json)

  echo "Inline policies details for IAM user:" | tee -a $OUTPUT_FILE
  for POLICY_NAME in $INLINE_POLICY_NAMES; do
    aws iam get-user-policy --user-name "$IAM_ENTITY" --policy-name "$POLICY_NAME" > "inline_policy_$POLICY_NAME.json"
    echo "Policy Name: $POLICY_NAME" | tee -a $OUTPUT_FILE
    cat "inline_policy_$POLICY_NAME.json" | jq . | tee -a $OUTPUT_FILE
  done

  ATTACHED_POLICY_ARNS=$(jq -r '.AttachedPolicies[].PolicyArn' attached_policies.json)

  echo "Attached policies details for IAM user:" | tee -a $OUTPUT_FILE
  for POLICY_ARN in $ATTACHED_POLICY_ARNS; do
    POLICY_NAME=$(aws iam get-policy --policy-arn "$POLICY_ARN" | jq -r '.Policy.PolicyName')
    POLICY_TYPE=$(aws iam get-policy --policy-arn "$POLICY_ARN" | jq -r '.Policy.Arn' | grep -oE '(aws|customer)/')
    POLICY_TYPE=${POLICY_TYPE%/} # 'aws' or 'customer'
    aws iam get-policy-version --policy-arn "$POLICY_ARN" --version-id $(aws iam get-policy --policy-arn "$POLICY_ARN" | jq -r '.Policy.DefaultVersionId') > "attached_policy_$POLICY_NAME.json"
    echo "Policy Name: $POLICY_NAME" | tee -a $OUTPUT_FILE
    echo "Policy Type: $POLICY_TYPE-managed" | tee -a $OUTPUT_FILE
    cat "attached_policy_$POLICY_NAME.json" | jq '.PolicyVersion.Document' | tee -a $OUTPUT_FILE
  done
fi

# グループの場合
if [ $GROUP_EXISTS -eq 0 ]; then
  echo "Getting attached policies for IAM group: $IAM_ENTITY" | tee -a $OUTPUT_FILE
  aws iam list-attached-group-policies --group-name "$IAM_ENTITY" > attached_policies.json

  echo "Getting inline policies for IAM group: $IAM_ENTITY" | tee -a $OUTPUT_FILE
  aws iam list-group-policies --group-name "$IAM_ENTITY" > inline_policies.json

  INLINE_POLICY_NAMES=$(jq -r '.PolicyNames[]' inline_policies.json)

  echo "Inline policies details for IAM group:" | tee -a $OUTPUT_FILE
  for POLICY_NAME in $INLINE_POLICY_NAMES; do
    aws iam get-group-policy --group-name "$IAM_ENTITY" --policy-name "$POLICY_NAME" > "inline_policy_$POLICY_NAME.json"
    echo "Policy Name: $POLICY_NAME" | tee -a $OUTPUT_FILE
    cat "inline_policy_$POLICY_NAME.json" | jq . | tee -a $OUTPUT_FILE
  done

  ATTACHED_POLICY_ARNS=$(jq -r '.AttachedPolicies[].PolicyArn' attached_policies.json)

  echo "Attached policies details for IAM group:" | tee -a $OUTPUT_FILE
  for POLICY_ARN in $ATTACHED_POLICY_ARNS; do
    POLICY_NAME=$(aws iam get-policy --policy-arn "$POLICY_ARN" | jq -r '.Policy.PolicyName')
    POLICY_TYPE=$(aws iam get-policy --policy-arn "$POLICY_ARN" | jq -r '.Policy.Arn' | grep -oE '(aws|customer)/')
    POLICY_TYPE=${POLICY_TYPE%/} # 'aws' or 'customer'
    aws iam get-policy-version --policy-arn "$POLICY_ARN" --version-id $(aws iam get-policy --policy-arn "$POLICY_ARN" | jq -r '.Policy.DefaultVersionId') > "attached_policy_$POLICY_NAME.json"
    echo "Policy Name: $POLICY_NAME" | tee -a $OUTPUT_FILE
    echo "Policy Type: $POLICY_TYPE-managed" | tee -a $OUTPUT_FILE
    cat "attached_policy_$POLICY_NAME.json" | jq '.PolicyVersion.Document' | tee -a $OUTPUT_FILE
  done
fi

# 一時ファイルの削除
rm attached_policies.json inline_policies.json inline_policy_*.json attached_policy_*.json

echo "Results have been saved to $OUTPUT_FILE"
