import yaml

def get_server_config(file_name):

    # open file, save contents as list
    with open(file_name, 'r') as f:
        doc = yaml.load(f)
        YAML_TEXT = doc
    server = doc["server"]

    return server

get_server_config('fetch.yaml')