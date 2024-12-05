#!/bin/bash

# AWS CLI V2のバージョンチェック
if aws --version 2>&1 | grep -q 'aws-cli/2'; then
    echo "AWS CLI V2 is already installed. Upgrading..."
    # AWS CLI V2がインストールされている場合はアップグレード
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install --update
else
    echo "AWS CLI V2 is not installed. Installing..."
    # AWS CLI V2がインストールされていない場合はインストール
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo -rf ./aws/install
fi

# インストールファイルのクリーンアップ
rm -rf ./aws
rm awscliv2.zip

# インストールまたはアップグレードの結果を表示
aws --version
