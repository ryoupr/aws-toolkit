#!/bin/bash

# リージョンとALBのARNを指定
REGION="ap-northeast-1"
# ALBのARNを入力として受け付ける
read -p "Enter the Load Balancer ARN: " LOAD_BALANCER_ARN

# タグのキーと値を指定（複数のタグを追加可能）
TAGS=(
  # "Key=Name,Value=Production"
  "Key=Owner,Value=zeon"
  "Key=Environment,Value=dev"
  "Key=Application,Value=reverse-proxy"
)

# ALBに関連付けられたリスナーのARNを取得
LISTENER_ARNS=$(aws elbv2 describe-listeners \
  --region "$REGION" \
  --load-balancer-arn "$LOAD_BALANCER_ARN" \
  --query "Listeners[*].ListenerArn" \
  --output text)

# 各リスナーにタグを追加
for LISTENER_ARN in $LISTENER_ARNS; do
  if [ -n "$LISTENER_ARN" ]; then
    aws elbv2 add-tags \
      --region "$REGION" \
      --resource-arns "$LISTENER_ARN" \
      --tags ${TAGS[@]}

    # 完了メッセージ
    echo "Tags added to ALB Listener: $LISTENER_ARN"
  else
    echo "Skipping empty LISTENER_ARN"
  fi
done

# 各リスナーに関連付けられたルールのARNを取得
for LISTENER_ARN in $LISTENER_ARNS; do
  RULE_ARNS=$(aws elbv2 describe-rules \
    --region "$REGION" \
    --listener-arn "$LISTENER_ARN" \
    --query "Rules[*].RuleArn" \
    --output text)

  # 各ルールにタグを追加
  for RULE_ARN in $RULE_ARNS; do
    if [ -n "$RULE_ARN" ]; then
      aws elbv2 add-tags \
        --region "$REGION" \
        --resource-arns "$RULE_ARN" \
        --tags ${TAGS[@]}

      # 完了メッセージ
      echo "Tags added to ALB Listener Rule: $RULE_ARN"
    else
      echo "Skipping empty RULE_ARN"
    fi
  done
done
