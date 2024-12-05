import boto3


def list_api_gateways():
    client = boto3.client("apigateway")
    response = client.get_rest_apis()
    apis = response["items"]
    for i, api in enumerate(apis):
        print(f"{i + 1}. {api['name']} (ID: {api['id']})")
    return apis


def delete_api_gateway(api_id):
    client = boto3.client("apigateway")
    try:
        client.delete_rest_api(restApiId=api_id)
        print(f"API Gateway '{api_id}' が削除されました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


def main():
    apis = list_api_gateways()
    choice = input(
        "削除するAPI Gatewayの番号をカンマ区切りで入力してください。すべて削除する場合は 'all' と入力してください: "
    )

    if choice.lower() == "all":
        for api in apis:
            delete_api_gateway(api["id"])
    else:
        try:
            selected_indices = [int(index.strip()) - 1 for index in choice.split(",")]
            for selected_index in selected_indices:
                if 0 <= selected_index < len(apis):
                    delete_api_gateway(apis[selected_index]["id"])
                else:
                    print(f"無効な番号が選択されました: {selected_index + 1}")
        except ValueError:
            print("無効な入力です。数字または 'all' を入力してください。")


if __name__ == "__main__":
    main()
