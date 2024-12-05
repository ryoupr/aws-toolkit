#!/bin/bash

# IAM Role name input
read -p "Enter IAM role name: " ROLE_NAME

# Get managed policies attached to the role
MANAGED_POLICIES=$(aws iam list-attached-role-policies --role-name "$ROLE_NAME" --query "AttachedPolicies[*].{PolicyName:PolicyName, PolicyArn:PolicyArn}" --output json)

# Get inline policies attached to the role
INLINE_POLICIES=$(aws iam list-role-policies --role-name "$ROLE_NAME" --query "PolicyNames" --output json)

# Get role trust relationship
TRUST_RELATIONSHIP=$(aws iam get-role --role-name "$ROLE_NAME" --query "Role.AssumeRolePolicyDocument" --output json)

# Extract custom managed policies
CUSTOM_MANAGED_POLICIES=()
for POLICY_ARN in $(echo "$MANAGED_POLICIES" | jq -r '.[].PolicyArn'); do
    if [[ $POLICY_ARN != arn:aws:iam::aws:policy/* ]]; then
        CUSTOM_MANAGED_POLICIES+=("$POLICY_ARN")
    fi
done

# Print managed policies
echo -e "\nManaged Policies:"
for POLICY in $(echo "$MANAGED_POLICIES" | jq -c '.[]'); do
    POLICY_NAME=$(echo "$POLICY" | jq -r '.PolicyName')
    POLICY_ARN=$(echo "$POLICY" | jq -r '.PolicyArn')
    echo "  - $POLICY_NAME (ARN: $POLICY_ARN)"
done

# Print custom managed policies
echo -e "\nCustom Managed Policies:"
for POLICY_ARN in "${CUSTOM_MANAGED_POLICIES[@]}"; do
    POLICY_NAME=$(aws iam get-policy --policy-arn "$POLICY_ARN" --query "Policy.PolicyName" --output text)
    echo "  - $POLICY_NAME (ARN: $POLICY_ARN)"
done

# Print inline policies
echo -e "\nInline Policies:"
for POLICY_NAME in $(echo "$INLINE_POLICIES" | jq -r '.[]'); do
    echo "  - $POLICY_NAME"
done

# Print trust relationship
echo -e "\nTrust Relationship:"
echo "$TRUST_RELATIONSHIP" | jq .

