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
server_settings = yaml_parser.get_server_config('fetch.yaml')

# declare empty variable, later used in creating ec2_instance
ec2_instance_ami_type = ''

# initialize boto3 w/key
ec2_client = boto3.client('ec2',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name=os.environ['AWS_REGION_NAME'])
