#!/bin/bash

# CloudFormationテンプレートファイルのパスを入力から取得（TAB補完有効化）
read -p "CloudFormationテンプレートファイルのパスを入力してください: " TEMPLATE_FILE

# スタック名を入力から取得
read -p "デプロイするスタック名を入力してください: " STACK_NAME

# テンプレートファイルからパラメータ名とデフォルト値を抽出
PARAM_KEYS=$(yq eval '.Parameters | keys' "$TEMPLATE_FILE" | sed 's/- //g')

# パラメータの値をユーザーから取得
PARAMETERS=""
for KEY in $PARAM_KEYS; do
    DEFAULT_VALUE=$(yq eval ".Parameters.$KEY.Default // \"\"" "$TEMPLATE_FILE")
    read -p "パラメータ $KEY の値を入力してください (デフォルト: $DEFAULT_VALUE): " VALUE
    VALUE=${VALUE:-$DEFAULT_VALUE}
    PARAMETERS="$PARAMETERS $KEY=$VALUE"
done

# CloudFormationデプロイコマンドを実行
# AWS CloudFormationスタックのデプロイを実行します
# --template-file: 使用するテンプレートファイルのパス
# --stack-name: デプロイするスタックの名前
# --parameter-overrides: テンプレートパラメータのオーバーライド
# --capabilities: IAMリソースの作成権限を付与
echo "AWS CloudFormationスタックをデプロイ中..."
DEPLOY_COMMAND="aws cloudformation deploy --template-file \"$TEMPLATE_FILE\" --stack-name \"$STACK_NAME\" --parameter-overrides $PARAMETERS --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM"
eval $DEPLOY_COMMAND

# デプロイ完了メッセージを表示する前に完了を待機
# デプロイ完了を確認するまで待機します
echo "スタックのデプロイが完了するまで待機しています..."
aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME"

# デプロイ完了メッセージ
echo "スタック '$STACK_NAME' のデプロイが完了しました。"

# 実行したコマンドを出力
echo "実行したコマンド"
echo "$DEPLOY_COMMAND"
