import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.providers.rpc import HTTPProvider

'''
If you use one of the suggested infrastructure providers, the url will be of the form
now_url  = f"https://eth.nownodes.io/{now_token}"
alchemy_url = f"https://eth-mainnet.alchemyapi.io/v2/{alchemy_token}"
infura_url = f"https://mainnet.infura.io/v3/{infura_token}"
'''

def connect_to_eth():
	url = "https://eth-mainnet.g.alchemy.com/v2/BnMvbBO9hx8A9CycZiP9jwDi2848y6vq"  # I'm using Alchemy to connect to Ethereum
	w3 = Web3(HTTPProvider(url))
	assert w3.is_connected(), f"Failed to connect to provider at {url}"
	return w3


def connect_with_middleware(contract_json):
	with open(contract_json, "r") as f:
		d = json.load(f)
		d = d['bsc']
		address = d['address']
		abi = d['abi']

	# The first section will be the same as "connect_to_eth()" but with a BNB url
	# Connect to BNB testnet: copied one url from this website: https://chainlist.org/chain/97?testnets=true
	bnb_testnet_url = "https://bsc-testnet.public.blastapi.io"
	w3 = Web3(HTTPProvider(bnb_testnet_url))

	if not w3.is_connected():
		raise ConnectionError(f"Failed to connect to BNB Testnet at {bnb_testnet_url}")

	# The second section requires you to inject middleware into your w3 object and
	w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

	# create a contract object. Read more on the docs pages at https://web3py.readthedocs.io/en/stable/middleware.html
	# and https://web3py.readthedocs.io/en/stable/web3.contract.html
	contract = w3.eth.contract(address=w3.to_checksum_address(address), abi=abi)

	return w3, contract


if __name__ == "__main__":
	connect_to_eth()
