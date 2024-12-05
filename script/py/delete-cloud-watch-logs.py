import boto3


def list_cloudwatch_log_groups():
    client = boto3.client("logs")
    response = client.describe_log_groups()
    log_groups = response["logGroups"]
    for i, log_group in enumerate(log_groups):
        print(f"{i + 1}. {log_group['logGroupName']}")
    return log_groups


def delete_log_group(log_group_name):
    client = boto3.client("logs")
    try:
        client.delete_log_group(logGroupName=log_group_name)
        print(f"Logグループ '{log_group_name}' が削除されました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


def main():
    log_groups = list_cloudwatch_log_groups()
    choice = input(
        "削除するLogグループの番号をカンマ区切りで入力してください。すべて削除する場合は 'all' と入力してください: "
    )

    if choice.lower() == "all":
        for log_group in log_groups:
            delete_log_group(log_group["logGroupName"])
    else:
        try:
            selected_indices = [int(index.strip()) - 1 for index in choice.split(",")]
            for selected_index in selected_indices:
                if 0 <= selected_index < len(log_groups):
                    delete_log_group(log_groups[selected_index]["logGroupName"])
                else:
                    print(f"無効な番号が選択されました: {selected_index + 1}")
        except ValueError:vscode-remote://wsl%2Bubuntu/home/ryou/dev/zeon-reverse-proxy/forTest/deploy-cfn-stack.sh
            print("無効な入力です。数字または 'all' を入力してください。")


if __name__ == "__main__":
    main()
