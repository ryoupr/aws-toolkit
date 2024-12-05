import boto3


def list_s3_buckets():
    s3 = boto3.client("s3")
    response = s3.list_buckets()
    buckets = [bucket["Name"] for bucket in response["Buckets"]]
    return buckets


def delete_s3_bucket(bucket_name):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)

    # Delete all objects in the bucket
    print(f"Deleting all objects in bucket {bucket_name}...")
    bucket.objects.all().delete()

    # Delete all object versions (if versioning is enabled)
    print(f"Deleting all object versions in bucket {bucket_name} (if any)...")
    bucket.object_versions.all().delete()

    # Delete the bucket
    print(f"Deleting bucket {bucket_name}...")
    bucket.delete()
    print(f"Bucket {bucket_name} deleted successfully.")


if __name__ == "__main__":
    # List all S3 buckets
    buckets = list_s3_buckets()
    print("Available S3 buckets:")
    for i, bucket in enumerate(buckets):
        print(f"{i + 1}. {bucket}")

    # User selects the buckets to delete
    choices = input(
        "Enter the numbers of the buckets you want to delete, separated by commas (or type 'all' to delete all buckets): "
    )

    if choices.strip().lower() == "all":
        valid_choices = list(range(len(buckets)))
    else:
        choices = [int(choice.strip()) - 1 for choice in choices.split(",")]
        valid_choices = [choice for choice in choices if 0 <= choice < len(buckets)]

    if valid_choices:
        for choice in valid_choices:
            bucket_name = buckets[choice]
            delete_s3_bucket(bucket_name)
    else:
        print("No valid buckets selected. Exiting.")
