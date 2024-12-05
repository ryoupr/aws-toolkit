import boto3


def list_stacks():
    client = boto3.client("cloudformation")
    # DELETE_FAILED も含める
    response = client.list_stacks(
        StackStatusFilter=[
            "CREATE_COMPLETE",
            "UPDATE_COMPLETE",
            "ROLLBACK_COMPLETE",
            "DELETE_FAILED",
        ]
    )
    stacks = response["StackSummaries"]
    for i, stack in enumerate(stacks):
        print(f"{i + 1}. {stack['StackName']} (Status: {stack['StackStatus']})")
    return stacks


def disable_termination_protection(stack_name):
    client = boto3.client("cloudformation")
    client.update_termination_protection(
        StackName=stack_name, EnableTerminationProtection=False
    )
    print(f"スタック '{stack_name}' の削除保護が解除されました。")


def delete_stack(stack_name):
    client = boto3.client("cloudformation")
    try:
        # 削除保護が有効な場合に解除する
        disable_termination_protection(stack_name)
        # スタックの削除を実行
        client.delete_stack(StackName=stack_name)
        print(f"スタック '{stack_name}' が削除されました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


def empty_s3_bucket(bucket_name):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.objects.all().delete()
        print(f"S3 バケット '{bucket_name}' のオブジェクトが削除されました。")
    except Exception as e:
        print(f"S3 バケットの削除中にエラーが発生しました: {e}")


def main():
    stacks = list_stacks()
    choice = input(
        "削除するスタックの番号をカンマ区切りで入力してください。すべて削除する場合は 'all' と入力してください: "
    )

    if choice.lower() == "all":
        for stack in stacks:
            delete_stack(stack["StackName"])
    else:
        try:
            selected_indices = [int(index.strip()) - 1 for index in choice.split(",")]
            for selected_index in selected_indices:
                if 0 <= selected_index < len(stacks):
                    delete_stack(stacks[selected_index]["StackName"])
                else:
                    print(f"無効な番号が選択されました: {selected_index + 1}")
        except ValueError:
            print("無効な入力です。数字または 'all' を入力してください。")


if __name__ == "__main__":
    main()
