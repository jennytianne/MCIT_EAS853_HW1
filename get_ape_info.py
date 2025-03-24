from web3 import Web3
from web3.providers.rpc import HTTPProvider
import requests
import json

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

# You will need the ABI to connect to the contract
# The file 'abi.json' has the ABI for the bored ape contract
# In general, you can get contract ABIs from etherscan
# https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('ape_abi.json', 'r') as f:
    abi = json.load(f)

############################
# Connect to an Ethereum node
api_url = "https://eth-mainnet.g.alchemy.com/v2/BnMvbBO9hx8A9CycZiP9jwDi2848y6vq"  # I'm using Alchemy to connect to Ethereum
provider = HTTPProvider(api_url)
w3 = Web3(provider)

# Get the BAYC contract using its contract address and ABI
contract = w3.eth.contract(address=contract_address, abi=abi)

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



def get_ape_info(ape_id):
    assert isinstance(ape_id, int), f"{ape_id} is not an int"
    assert 0 <= ape_id, f"{ape_id} must be at least 0"
    assert 9999 >= ape_id, f"{ape_id} must be less than 10,000"
    # Get the ape_id, f"{ape_id} must be less than 10,000"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # Get the owner of the ape by ape_id
    data['owner'] = contract.functions.ownerOf(ape_id).call()

    # Get the IPFS URI of the ape by ape_id:
    uri = contract.functions.tokenURI(ape_id).call()

    # Extract the CID from IPFS link: keep the string after "ipfs://"
    cid = uri.replace("ipfs://", "")

    # Get the dictionary at that CID
    metadata = get_from_ipfs(cid)

    # Get the image and eye trait:
    data['image'] = metadata.get("image", "")
    
    for attr in metadata.get("attributes", []):
        if attr.get("trait_type") == "Eyes":
            data['eyes'] = attr.get("value")
            break

    assert isinstance(data, dict), f'get_ape_info{ape_id} should return a dict'
    assert all([a in data.keys() for a in
                 ['owner', 'image', 'eyes']]), f"return value should include the keys 'owner','image' and 'eyes'"
    return data



print(get_ape_info(99))