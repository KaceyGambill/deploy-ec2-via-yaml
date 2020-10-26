import time
import os
import subprocess
import boto3
import yaml_parser
import setup_machine
from dotenv import load_dotenv

# load env vars
load_dotenv()

# get settings from parsed yaml file
server_settings = yaml_parser.get_server_config('ec2_config.yaml')

# declare empty variable, later used in creating ec2_instance
ec2_instance_ami_type = ''
# map to linux ami in aws marketplace
if('amzn2' in server_settings['ami_type']):
   ec2_instance_ami_type = 'ami-0528a5175983e7f28'

# initialize boto3 w/key
ec2_client = boto3.client('ec2',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name=os.environ['AWS_REGION_NAME'])

# build security group allowing port 22, which we will attach to ec2_instance to allow ssh
def build_ssh_ingress_sec_grp(security_group_name):
    security_group_port_22 = ec2_client.create_security_group(
        Description='allow_ssh',
        GroupName=security_group_name,
    )
    security_group_ingress = ec2_client.authorize_security_group_ingress(
        GroupId=security_group_port_22.get('GroupId'),
        IpPermissions=[
            {
                'FromPort': 22,
                'ToPort': 22,
                'IpProtocol': 'tcp',
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
    return security_group_port_22.get('GroupId')

sec_grp_id = build_ssh_ingress_sec_grp(server_settings['security_group_name'])

# map ebs volumes from yaml
ebs_volume_mapping = []
for volume in server_settings["volumes"]:
   ebs_volume_mapping.append({
       'DeviceName': volume.get('device'),
       'Ebs': {
           'DeleteOnTermination': volume.get('delete_on_termination'),
           'VolumeSize': volume.get('size_gb'),
           'VolumeType': 'standard',
           'Encrypted': False
        }
       })


# create ec2_key_pair that will be used to ssh / setup instance
ec2_key_pair = ec2_client.create_key_pair(
        KeyName=server_settings['key_pair_name']
        )
ec2_key_pair_name = server_settings['key_pair_name']
ec2_key_pair_file_name = '{}.pem'.format(server_settings['key_pair_name'])
# save .pem version to file after creating in aws, we need this to connect to instance for the first time
f = open(ec2_key_pair_file_name, 'w+')
f.write(ec2_key_pair['KeyMaterial'])
f.close()


# creates the ec2_instance
ec2_instance = ec2_client.run_instances(

        BlockDeviceMappings=ebs_volume_mapping,
        ImageId=ec2_instance_ami_type,
        InstanceType=server_settings['instance_type'],
        MinCount=server_settings['min_count'],
        MaxCount=server_settings['max_count'],
        KeyName=ec2_key_pair_name,
        Monitoring = {
            'Enabled': False
            },
        SecurityGroupIds=[
            sec_grp_id
        ]
)
ec2_instance_id = ec2_instance["Instances"][0].get("InstanceId")

# sleep 3 seconds before describing the instance, this allows time for a public Ip address to be assigned
time.sleep(3)

ec2_instance_info = ec2_client.describe_instances(
        InstanceIds=[
            ec2_instance_id
        ]
)
ec2_public_ip_address = ec2_instance_info["Reservations"][0]["Instances"][0].get("PublicIpAddress")


# build ssh_commands list, which will be used to provide the ssh_commands that set up the volumes & users
volume_config_commands = setup_machine.format_and_mount_ebs(server_settings["volumes"])
user_setup_commands = setup_machine.create_user_ssh_command_array(server_settings["users"])
ssh_commands = volume_config_commands + user_setup_commands

# supposed to be able to use the ec2.resource wait until instance is running -buggy-
# could alternatively poll instance with a describe status and once it was ready then execute the connect_to_instance function
# due to time, going with time.sleep(180) for now
time.sleep(180)
setup_machine.connect_to_instance(ec2_key_pair_file_name, ec2_public_ip_address, ssh_commands)
