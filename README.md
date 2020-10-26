# deploy-ec2-via-yaml
takes a yaml config file, parses and deploys a ec2-instance based off of settings


To run this you will need to have Python3.7.7 and run ```pip install -r requirements.txt``` to install the required packages.
You will also need to set up a .env file with AWS Credentials to establish a connection with the boto3 sdk

the structure of the env file should look like:
```.env
AWS_ACCESS_KEY = "ACCESSKEYGOESHERE"
AWS_SECRET_ACCESS_KEY = "SECRETACCESSKEYGOESHERE"
AWS_REGION_NAME = "us-west-2"
```

once you have the requirements set up and the .env file configured you should be able to run the main.py file using ```python3 main.py```


### Keep in mind
Line 13 of main.py is where you set the name of the yaml file
You must have a priavte key for the users. This will only save the public key to their authorized_keys. To connect you must edit the yaml, provide the public key value, then use the private key to connect
