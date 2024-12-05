import boto3
import json

# 各サービスのリソースを取得する関数
def list_resources(region, service_name):
    session = boto3.Session(region_name=region)
    client = session.client(service_name)
    resource_list = []
    
    try:
        if service_name == 'ec2':
            ec2 = session.resource('ec2')
            instances = ec2.instances.all()
            for instance in instances:
                resource_list.append(f'EC2 Instance: {instance.id}')
        
        elif service_name == 's3':
            s3 = session.client('s3')
            response = s3.list_buckets()
            for bucket in response['Buckets']:
                bucket_name = bucket['Name']
                bucket_location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
                if bucket_location is None:
                    bucket_location = 'us-east-1'
                if bucket_location == region:
                    resource_list.append(f'S3 Bucket: {bucket_name}')
        
        elif service_name == 'rds':
            response = client.describe_db_instances()
            for db_instance in response['DBInstances']:
                resource_list.append(f'RDS Instance: {db_instance["DBInstanceIdentifier"]}')
        
        elif service_name == 'lambda':
            response = client.list_functions()
            for function in response['Functions']:
                resource_list.append(f'Lambda Function: {function["FunctionName"]}')
        
    except Exception as e:
        print(f'Error listing {service_name} resources in region {region}: {e}')
    
    return resource_list

# メイン関数
def list_all_resources(specified_regions=None):
    session = boto3.Session()
    all_regions = session.get_available_regions('ec2')
    regions = specified_regions if specified_regions else all_regions
    services = ['ec2', 's3', 'rds', 'lambda']  # リストするサービスをここに追加

    all_resources = {}

    for region in regions:
        if region not in all_regions:
            print(f'Region {region} is not valid. Skipping...')
            continue
        region_resources = {}
        print(f'Starting to list resources in region: {region}')
        for service in services:
            resources = list_resources(region, service)
            if resources:
                region_resources[service] = resources
                print(f'  {service} resources in {region}:')
                for resource in resources:
                    print(f'    {resource}')
        if region_resources:
            all_resources[region] = region_resources
            print(f'Completed listing resources in region: {region}')
        else:
            print(f'No resources found in region: {region}')
        print('--------------------------------------------')

    return all_resources

# リソース情報をテキストレポート形式で出力する関数
def generate_report(resources):
    report = []
    for region, services in resources.items():
        report.append(f'Region: {region}')
        for service, res_list in services.items():
            report.append(f'  Service: {service}')
            for resource in res_list:
                report.append(f'    {resource}')
    return "\n".join(report)

if __name__ == "__main__":
    # 指定されたリージョン
    specified_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ap-south-1', 
                         'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-southeast-1', 
                         'ap-southeast-2', 'ca-central-1', 'eu-central-1', 'eu-west-1', 
                         'eu-west-2', 'eu-west-3', 'eu-north-1', 'sa-east-1']
    
    all_resources = list_all_resources(specified_regions)
    
    # テキストレポート形式で出力
    report = generate_report(all_resources)
    print('Text Report:')
    print(report)
    
    # JSON形式で出力（オプション）
    json_output = json.dumps(all_resources, indent=4)
    print('JSON Output:')
    print(json_output)
