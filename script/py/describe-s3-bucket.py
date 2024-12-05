import subprocess
import json


def run_aws_command(command):
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout


def list_buckets():
    command = "aws s3api list-buckets"
    result = run_aws_command(command)
    if result:
        buckets = json.loads(result).get("Buckets", [])
        return [bucket["Name"] for bucket in buckets]
    return []


def get_bucket_details(bucket_name):
    # Get bucket location
    location_command = f"aws s3api get-bucket-location --bucket {bucket_name}"
    location = run_aws_command(location_command)
    if location:
        print(f"\nBucket Location: {location}")

    # Get bucket policy
    policy_command = f"aws s3api get-bucket-policy --bucket {bucket_name}"
    policy = run_aws_command(policy_command)
    if policy:
        print(f"\nBucket Policy: {policy}")

    # Get bucket ACL
    acl_command = f"aws s3api get-bucket-acl --bucket {bucket_name}"
    acl = run_aws_command(acl_command)
    if acl:
        print(f"\nBucket ACL: {acl}")

    # Get bucket CORS configuration
    cors_command = f"aws s3api get-bucket-cors --bucket {bucket_name}"
    cors = run_aws_command(cors_command)
    if cors:
        print(f"\nBucket CORS Configuration: {cors}")


def select_bucket(buckets):
    for index, bucket in enumerate(buckets):
        print(f"{index + 1}. {bucket}")

    choice = int(input("\nSelect a bucket by number: "))
    if 1 <= choice <= len(buckets):
        return buckets[choice - 1]
    else:
        print("Invalid selection.")
        return None


if __name__ == "__main__":
    buckets = list_buckets()
    if buckets:
        print("Available S3 Buckets:")
        selected_bucket = select_bucket(buckets)
        if selected_bucket:
            print(f"\nFetching details for bucket: {selected_bucket}")
            get_bucket_details(selected_bucket)
    else:
        print("No S3 buckets found.")
