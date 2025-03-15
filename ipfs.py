import requests
import json


## "pin_to_ipfs()" which takes a Python dictionary, and stores the dictionary (as JSON) on IPFS.
# The function should return the Content Identifier (CID) of the data stored.

def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"
    print(data)
    files = {'file': '<full_path_to_your_file>'}
    #response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=files, auth=(< project_id >, < project_secret >))
    #print(response.text)
    return cid


def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"
    # YOUR CODE HERE

    assert isinstance(data, dict), f"get_from_ipfs should return a dict"
    return data
