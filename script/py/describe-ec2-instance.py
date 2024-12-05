import boto3


def list_instances():
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances()

    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append(instance)

    return instances


def describe_instance(instance_id):
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances(InstanceIds=[instance_id])

    return response["Reservations"][0]["Instances"][0]


def main():
    instances = list_instances()

    for i, instance in enumerate(instances):
        print(
            f"{i+1}: Instance ID: {instance['InstanceId']} - State: {instance['State']['Name']}"
        )

    while True:
        try:
            choice = int(input("インスタンス番号を選択してください: ")) - 1
            if choice < 0 or choice >= len(instances):
                print("無効な番号です。もう一度試してください。")
            else:
                break
        except ValueError:
            print("番号を入力してください。")

    selected_instance_id = instances[choice]["InstanceId"]
    instance_details = describe_instance(selected_instance_id)

    print("インスタンスの詳細情報:")
    for key, value in instance_details.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
