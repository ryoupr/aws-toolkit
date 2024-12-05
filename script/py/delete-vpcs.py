import boto3
import argparse
import time

def list_vpcs():
    client = boto3.client('ec2')
    response = client.describe_vpcs()
    vpcs = response['Vpcs']
    return vpcs

def delete_vpc_resources(vpc_id):
    ec2 = boto3.resource('ec2')
    client = boto3.client('ec2')

    total_steps = 12
    current_step = 0

    def print_progress(step):
        progress = (step / total_steps) * 100
        print(f"Progress: {progress:.2f}%")

    vpc = ec2.Vpc(vpc_id)

    # EC2インスタンスの終了
    print("EC2インスタンスを終了しています...")
    for instance in vpc.instances.all():
        instance.terminate()
        instance.wait_until_terminated()
    current_step += 1
    print_progress(current_step)

    # ネットワークインターフェイスのデタッチと削除
    print("ネットワークインターフェイスをデタッチおよび削除しています...")
    for eni in vpc.network_interfaces.all():
        try:
            if eni.attachment:
                client.detach_network_interface(AttachmentId=eni.attachment['AttachmentId'])
            client.delete_network_interface(NetworkInterfaceId=eni.id)
            waiter = client.get_waiter('network_interface_deleted')
            waiter.wait(NetworkInterfaceIds=[eni.id])
        except client.exceptions.ClientError as e:
            print(f"ネットワークインターフェイス {eni.id} の削除中にエラーが発生しました: {e}")
    current_step += 1
    print_progress(current_step)

    # NATゲートウェイの削除
    print("NATゲートウェイを削除しています...")
    nat_gateways = client.describe_nat_gateways(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['NatGateways']
    for nat in nat_gateways:
        client.delete_nat_gateway(NatGatewayId=nat['NatGatewayId'])
        waiter = client.get_waiter('nat_gateway_deleted')
        waiter.wait(NatGatewayIds=[nat['NatGatewayId']])
    current_step += 1
    print_progress(current_step)

    # Elastic IPの解放
    print("Elastic IPを解放しています...")
    addresses = client.describe_addresses(Filters=[{'Name': 'domain', 'Values': ['vpc']}])['Addresses']
    for address in addresses:
        if 'AssociationId' in address:
            client.disassociate_address(AssociationId=address['AssociationId'])
        client.release_address(AllocationId=address['AllocationId'])
    current_step += 1
    print_progress(current_step)

    # ロードバランサーの削除
    print("ロードバランサーを削除しています...")
    elb = boto3.client('elb')
    elbv2 = boto3.client('elbv2')
    load_balancers = elb.describe_load_balancers()['LoadBalancerDescriptions']
    for lb in load_balancers:
        if lb['VPCId'] == vpc_id:
            elb.delete_load_balancer(LoadBalancerName=lb['LoadBalancerName'])
            waiter = elb.get_waiter('load_balancer_deleted')
            waiter.wait(LoadBalancerNames=[lb['LoadBalancerName']])
    load_balancers_v2 = elbv2.describe_load_balancers()['LoadBalancers']
    for lb in load_balancers_v2:
        if lb['VpcId'] == vpc_id:
            elbv2.delete_load_balancer(LoadBalancerArn=lb['LoadBalancerArn'])
            waiter = elbv2.get_waiter('load_balancer_deleted')
            waiter.wait(LoadBalancerArns=[lb['LoadBalancerArn']])
    current_step += 1
    print_progress(current_step)

    # インターネットゲートウェイのデタッチと削除
    print("インターネットゲートウェイをデタッチおよび削除しています...")
    for igw in vpc.internet_gateways.all():
        vpc.detach_internet_gateway(InternetGatewayId=igw.id)
        igw.delete()
    current_step += 1
    print_progress(current_step)

    # ルートテーブルの削除
    print("ルートテーブルを削除しています...")
    for rt in vpc.route_tables.all():
        for association in rt.associations:
            if not association.main:
                association.delete()
        if not rt.associations:
            rt.delete()
    current_step += 1
    print_progress(current_step)

    # サブネットの削除
    print("サブネットを削除しています...")
    for subnet in vpc.subnets.all():
        subnet.delete()
    current_step += 1
    print_progress(current_step)

    # セキュリティグループの削除
    print("セキュリティグループを削除しています...")
    for sg in vpc.security_groups.all():
        if sg.group_name != 'default':
            try:
                sg.delete()
            except client.exceptions.ClientError as e:
                print(f"セキュリティグループ {sg.id} の削除中にエラーが発生しました: {e}")
    current_step += 1
    print_progress(current_step)

    # ネットワークACLの削除
    print("ネットワークACLを削除しています...")
    for acl in vpc.network_acls.all():
        if not acl.is_default:
            acl.delete()
    current_step += 1
    print_progress(current_step)

    # VPCピアリング接続の削除
    print("VPCピアリング接続を削除しています...")
    peering_connections = client.describe_vpc_peering_connections(Filters=[{'Name': 'requester-vpc-info.vpc-id', 'Values': [vpc_id]}])['VpcPeeringConnections']
    for peer in peering_connections:
        client.delete_vpc_peering_connection(VpcPeeringConnectionId=peer['VpcPeeringConnectionId'])
    current_step += 1
    print_progress(current_step)

    # VPCの削除
    print("VPCを削除しています...")
    vpc.delete()
    current_step += 1
    print_progress(current_step)

    print("すべてのリソースが正常に削除されました！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VPC内のすべてのリソースを削除します。")
    args = parser.parse_args()

    vpcs = list_vpcs()

    print("削除したいVPCを選択してください:")
    for i, vpc in enumerate(vpcs):
        print(f"{i + 1}: {vpc['VpcId']} ({vpc['CidrBlock']})")

    choice = int(input("VPCの番号を入力してください: ")) - 1
    selected_vpc_id = vpcs[choice]['VpcId']

    delete_vpc_resources(selected_vpc_id)
