import boto3
import botocore
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

    # Terminate EC2 Instances
    print("Terminating EC2 Instances...")
    for instance in vpc.instances.all():
        instance.terminate()
        instance.wait_until_terminated()
    current_step += 1
    print_progress(current_step)

    # Delete Network Interfaces
    print("Deleting Network Interfaces...")
    for eni in vpc.network_interfaces.all():
        eni.delete()
    current_step += 1
    print_progress(current_step)

    # Delete NAT Gateways
    print("Deleting NAT Gateways...")
    nat_gateways = client.describe_nat_gateways(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['NatGateways']
    for nat in nat_gateways:
        client.delete_nat_gateway(NatGatewayId=nat['NatGatewayId'])
    current_step += 1
    print_progress(current_step)

    # Wait for NAT Gateways to be deleted
    time.sleep(10)

    # Release Elastic IPs
    print("Releasing Elastic IPs...")
    addresses = client.describe_addresses(Filters=[{'Name': 'domain', 'Values': ['vpc']}])['Addresses']
    for address in addresses:
        if 'AssociationId' in address:
            client.disassociate_address(AssociationId=address['AssociationId'])
        client.release_address(AllocationId=address['AllocationId'])
    current_step += 1
    print_progress(current_step)

    # Delete Load Balancers
    print("Deleting Load Balancers...")
    elb = boto3.client('elb')
    elbv2 = boto3.client('elbv2')
    load_balancers = elb.describe_load_balancers()['LoadBalancerDescriptions']
    for lb in load_balancers:
        if lb['VPCId'] == vpc_id:
            elb.delete_load_balancer(LoadBalancerName=lb['LoadBalancerName'])
    load_balancers_v2 = elbv2.describe_load_balancers()['LoadBalancers']
    for lb in load_balancers_v2:
        if lb['VpcId'] == vpc_id:
            elbv2.delete_load_balancer(LoadBalancerArn=lb['LoadBalancerArn'])
    current_step += 1
    print_progress(current_step)

    # Detach and delete Internet Gateways
    print("Detaching and Deleting Internet Gateways...")
    for igw in vpc.internet_gateways.all():
        vpc.detach_internet_gateway(InternetGatewayId=igw.id)
        igw.delete()
    current_step += 1
    print_progress(current_step)

    # Delete Route Tables
    print("Deleting Route Tables...")
    for rt in vpc.route_tables.all():
        for association in rt.associations:
            if not association.main:
                association.delete()
        if not rt.associations:
            rt.delete()
    current_step += 1
    print_progress(current_step)

    # Delete Subnets
    print("Deleting Subnets...")
    for subnet in vpc.subnets.all():
        subnet.delete()
    current_step += 1
    print_progress(current_step)

    # Delete Security Groups
    print("Deleting Security Groups...")
    for sg in vpc.security_groups.all():
        if sg.group_name != 'default':
            sg.delete()
    current_step += 1
    print_progress(current_step)

    # Delete Network ACLs
    print("Deleting Network ACLs...")
    for acl in vpc.network_acls.all():
        if not acl.is_default:
            acl.delete()
    current_step += 1
    print_progress(current_step)

    # Delete VPC Peering Connections
    print("Deleting VPC Peering Connections...")
    peering_connections = client.describe_vpc_peering_connections(Filters=[{'Name': 'requester-vpc-info.vpc-id', 'Values': [vpc_id]}])['VpcPeeringConnections']
    for peer in peering_connections:
        client.delete_vpc_peering_connection(VpcPeeringConnectionId=peer['VpcPeeringConnectionId'])
    current_step += 1
    print_progress(current_step)

    # Additional wait time to ensure dependencies are fully removed
    time.sleep(10)

    # Delete the VPC
    print("Deleting the VPC...")
    try:
        vpc.delete()
        current_step += 1
        print_progress(current_step)
        print("All resources deleted successfully!")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'DependencyViolation':
            print("Error: The VPC has dependencies and cannot be deleted. Please check for remaining resources and try again.")
        else:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete all resources within a VPC.")
    args = parser.parse_args()

    vpcs = list_vpcs()

    print("Select the VPC you want to delete:")
    for i, vpc in enumerate(vpcs):
        print(f"{i + 1}: {vpc['VpcId']} ({vpc['CidrBlock']})")

    choice = int(input("Enter the number of the VPC: ")) - 1
    selected_vpc_id = vpcs[choice]['VpcId']

    delete_vpc_resources(selected_vpc_id)
