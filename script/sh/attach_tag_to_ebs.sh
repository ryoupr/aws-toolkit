#!/bin/bash

# ボリュームIDのリスト（必要に応じて変更してください）
volume_ids=("vol-00209bae8acfb3f23" "vol-0148f83826f136965" "vol-0bccd58f645087df6" "vol-0c9f7f7e58f1e028f" "vol-07b8dc0b1baef5f69" "vol-0873f301651664734" "vol-04cce48a9ae51bc4f")

# タグのキーと値（必要に応じて変更してください）
tag_key="Application"
tag_value="sap-mig"

# 各ボリュームIDに対してタグを追加
for volume_id in "${volume_ids[@]}"; do
    echo "Adding tag to volume $volume_id"
    aws ec2 create-tags --resources "$volume_id" --tags Key="$tag_key",Value="$tag_value"
    if [ $? -eq 0 ]; then
        echo "Successfully added tag $tag_key=$tag_value to volume $volume_id"
    else
        echo "Failed to add tag to volume $volume_id"
    fi
done

tag_key="ServerNAME"
tag_value="TIS-SAPS4HANA-DB"

# 各ボリュームIDに対してタグを追加
for volume_id in "${volume_ids[@]}"; do
    echo "Adding tag to volume $volume_id"
    aws ec2 create-tags --resources "$volume_id" --tags Key="$tag_key",Value="$tag_value"
    if [ $? -eq 0 ]; then
        echo "Successfully added tag $tag_key=$tag_value to volume $volume_id"
    else
        echo "Failed to add tag to volume $volume_id"
    fi
done

tag_key="Owner"
tag_value="test"

# 各ボリュームIDに対してタグを追加
for volume_id in "${volume_ids[@]}"; do
    echo "Adding tag to volume $volume_id"
    aws ec2 create-tags --resources "$volume_id" --tags Key="$tag_key",Value="$tag_value"
    if [ $? -eq 0 ]; then
        echo "Successfully added tag $tag_key=$tag_value to volume $volume_id"
    else
        echo "Failed to add tag to volume $volume_id"
    fi
done

tag_key="Environment"
tag_value="poc"

# 各ボリュームIDに対してタグを追加
for volume_id in "${volume_ids[@]}"; do
    echo "Adding tag to volume $volume_id"
    aws ec2 create-tags --resources "$volume_id" --tags Key="$tag_key",Value="$tag_value"
    if [ $? -eq 0 ]; then
        echo "Successfully added tag $tag_key=$tag_value to volume $volume_id"
    else
        echo "Failed to add tag to volume $volume_id"
    fi
done
