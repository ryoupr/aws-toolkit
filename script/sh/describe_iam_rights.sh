#!/bin/bash

# プロンプトでIAMユーザー名を入力
read -p "Enter the IAM username: " username

echo "========================================"
echo "IAM User: $username"
echo "========================================"

# IAMユーザーにアタッチされている管理ポリシーをリスト
echo "Attached Managed Policies:"
managed_policies=$(aws iam list-attached-user-policies --user-name "$username" --query 'AttachedPolicies[*].PolicyName' --output text)

if [ -z "$managed_policies" ]; then
    echo " - No managed policies found"
else
    echo "$managed_policies" | tr '\t' '\n' | sed 's/^/ - /'
fi

echo "----------------------------------------"

# IAMユーザーにアタッチされているインラインポリシーをリスト
echo "Inline Policies:"
inline_policies=$(aws iam list-user-policies --user-name "$username" --query 'PolicyNames[*]' --output text)

if [ -z "$inline_policies" ]; then
    echo " - No inline policies found"
else
    echo "$inline_policies" | tr '\t' '\n' | sed 's/^/ - /'
fi

echo "----------------------------------------"

# IAMユーザーが所属するグループをリスト
echo "Groups:"
groups=$(aws iam list-groups-for-user --user-name "$username" --query 'Groups[*].GroupName' --output text)

if [ -z "$groups" ]; then
    echo " - No groups found"
else
    echo "$groups" | tr '\t' '\n' | sed 's/^/ - /'
fi

echo "========================================"
