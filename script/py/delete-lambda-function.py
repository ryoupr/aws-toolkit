import boto3


def list_lambdas():
    client = boto3.client("lambda")
    response = client.list_functions()
    functions = response["Functions"]
    for i, function in enumerate(functions):
        print(f"{i + 1}. {function['FunctionName']}")
    return functions


def delete_lambda(function_name):
    client = boto3.client("lambda")
    try:
        client.delete_function(FunctionName=function_name)
        print(f"Lambda関数 '{function_name}' が削除されました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


def main():
    functions = list_lambdas()
    choice = input(
        "削除するLambda関数の番号をカンマ区切りで入力してください。すべて削除する場合は 'all' と入力してください: "
    )

    if choice.lower() == "all":
        for function in functions:
            delete_lambda(function["FunctionName"])
    else:
        try:
            selected_indices = [int(index.strip()) - 1 for index in choice.split(",")]
            for selected_index in selected_indices:
                if 0 <= selected_index < len(functions):
                    delete_lambda(functions[selected_index]["FunctionName"])
                else:
                    print(f"無効な番号が選択されました: {selected_index + 1}")
        except ValueError:
            print("無効な入力です。数字または 'all' を入力してください。")


if __name__ == "__main__":
    main()
