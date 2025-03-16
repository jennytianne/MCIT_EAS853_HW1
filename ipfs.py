import requests
import json

# Pinata API keys (Replace with your actual keys)
API_KEY = "697e41ead53a291c24a1"
SECRET_API_KEY = "7444de9099049713eaae3be981a6595a1788b0b8b30e38fd355074c055d882fa"
url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
headers = {
    "pinata_api_key": API_KEY,
    "pinata_secret_api_key": SECRET_API_KEY,
    "Content-Type": "application/json"
}
## "pin_to_ipfs()" which takes a Python dictionary, and stores the dictionary (as JSON) on IPFS.
# The function should return the Content Identifier (CID) of the data stored.

def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"
    print("This is the input dictionary:", data)
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:  # Checks if the status code is 200 (successful request).
        cid = response.json()["IpfsHash"]
        print(f"✅ JSON pinned successfully! CID: {cid}")
        return cid
    else:
        print(f"❌ Error: {response.text}")
        return None

## "get_from_ipfs(cid)" which takes as input an IPFS CID and returns a Python dictionary containing the content.
# For this function, you may assume the content identified by the CID is valid JSON content.
# For example, you may assume that the CID does not refer to an image,
# video or other type of binary content that cannot be easily JSONified.

def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    response = requests.get(url)
    data = response.json()  # Convert JSON response back to a dictionary
    assert isinstance(data, dict), f"get_from_ipfs should return a dict"
    if response.status_code == 200:  # Checks if the status code is 200 (successful request).
        print("✅ JSON retrieved successfully!")
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None


# data = {'name': ['N', 'D', 'H', 'F', 'R'], 'description': ['Q', 'A', 'J', 'N', 'D', 'M', 'C', 'T', 'C', 'Y']}
# cid = pin_to_ipfs(data)
# retrieved_data = get_from_ipfs(cid)
# print("Retrieved JSON:", retrieved_data)