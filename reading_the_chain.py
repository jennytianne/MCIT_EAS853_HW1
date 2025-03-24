import random
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

def print_all_transactions(w3, block_num):
    """
    Prints all transactions in a given block.

    :param w3: Web3 instance connected to an Ethereum-compatible node.
    :param block_num: The block number to fetch transactions from.
    """
    try:
        # Retrieve the block with full transaction details
        block = w3.eth.get_block(block_num, full_transactions=True)

        # Check if the block contains transactions
        if not block.transactions:
            print(f"Block {block_num} contains no transactions.")
            return

        print(f"Transactions in Block {block_num}:")
        print("-" * 50)

        # Iterate over each transaction in the block
        for i, tx in enumerate(block.transactions):
            print(f"Transaction {i + 1}:")
            print(f"  Hash: {tx.hash.hex()}")
            print(f"  From: {tx['from']}")
            print(f"  To: {tx['to']}")
            print(f"  Value: {w3.from_wei(tx['value'], 'ether')} ETH")
            print(f"  Gas Price: {w3.from_wei(tx['gasPrice'], 'gwei')} Gwei")
            print(f"  Gas Used: {tx['gas']}")
            print(f"  Nonce: {tx['nonce']}")
            print(f"  Input Data: {tx['input'][:66]}...")  # Display only the first 32 bytes
            print("-" * 50)

    except Exception as e:
        print(f"Error fetching block {block_num}: {str(e)}")


def is_ordered_block(w3, block_num):
	"""
	Takes a block number
	Returns a boolean that tells whether all the transactions in the block are ordered by priority fee

	Before EIP-1559, a block is ordered if and only if all transactions are sorted in decreasing order of the gasPrice field

	After EIP-1559, there are two types of transactions
		*Type 0* The priority fee is tx.gasPrice - block.baseFeePerGas
		*Type 2* The priority fee is min( tx.maxPriorityFeePerGas, tx.maxFeePerGas - block.baseFeePerGas )

	Conveniently, most type 2 transactions set the gasPrice field to be min( tx.maxPriorityFeePerGas + block.baseFeePerGas, tx.maxFeePerGas )
	"""
	ordered = False

	# Get block details with transactions
	block = w3.eth.get_block(block_num, full_transactions=True)
	base_fee = block.get("baseFeePerGas", 0)  # Default to 0 if baseFeePerGas is missing (pre-EIP-1559)

	# Compute priority fees for all transactions in the block
	# store in a list:
	priority_fees = []
	for tx in block.transactions:
		if "maxPriorityFeePerGas" in tx and "maxFeePerGas" in tx:
			# Type 2 transaction (EIP-1559)
			priority_fee = min(tx["maxPriorityFeePerGas"], tx["maxFeePerGas"] - base_fee)
		else:
			# Type 0 transaction (pre-EIP-1559)
			priority_fee = tx["gasPrice"] - base_fee

		priority_fees.append(priority_fee)

	# Check if the priority fees are sorted in decreasing order
	ordered = priority_fees == sorted(priority_fees, reverse=True)

	return ordered


def get_contract_values(contract, admin_address, owner_address):
	"""
	Takes a contract object, and two addresses (as strings) to be used for calling
	the contract to check current on chain values.
	The provided "default_admin_role" is the correctly formatted solidity default
	admin value to use when checking with the contract
	To complete this method you need to make three calls to the contract to get:
	  onchain_root: Get and return the merkleRoot from the provided contract
	  has_role: Verify that the address "admin_address" has the role "default_admin_role" return True/False
	  prime: Call the contract to get and return the prime owned by "owner_address"

	check on available contract functions and transactions on the block explorer at
	https://testnet.bscscan.com/address/0xaA7CAaDA823300D18D3c43f65569a47e78220073
	"""
	default_admin_role = int.to_bytes(0, 32, byteorder="big")

	# Get and return the merkleRoot from the provided contract
	onchain_root = contract.functions.merkleRoot().call()

	# Check the contract to see if the address "admin_address" has the role "default_admin_role"
	has_role = contract.functions.hasRole(default_admin_role, Web3.to_checksum_address(admin_address)).call()

	# Call the contract to get the prime owned by "owner_address"
	prime = contract.functions.getPrimeByOwner(Web3.to_checksum_address(owner_address)).call()


	return onchain_root, has_role, prime # Returns a tuple (onchain_root, has_role, prime)


"""
	This might be useful for testing (main is not run by the grader feel free to change 
	this code anyway that is helpful)
"""
if __name__ == "__main__":
	# These are addresses associated with the Merkle contract (check on contract
	# functions and transactions on the block explorer at
	# https://testnet.bscscan.com/address/0xaA7CAaDA823300D18D3c43f65569a47e78220073
	admin_address = "0xAC55e7d73A792fE1A9e051BDF4A010c33962809A"
	owner_address = "0x793A37a85964D96ACD6368777c7C7050F05b11dE"
	contract_file = "contract_info.json"

	cont_w3, contract = connect_with_middleware(contract_file)
	onchain_root, has_role, prime = get_contract_values(contract, admin_address, owner_address)
	print(f"Root: {onchain_root}")
	print(f"has role: {has_role}")
	print(f"prime: {prime}")

	eth_w3 = connect_to_eth()
	latest_block = eth_w3.eth.get_block_number()
	london_hard_fork_block_num = 12965000
	assert latest_block > london_hard_fork_block_num, f"Error: the chain never got past the London Hard Fork"

	n = 5
	for _ in range(n):
		block_num = random.randint(1, latest_block)
		ordered = is_ordered_block(eth_w3, block_num)
		if ordered:
			print(f"Block {block_num} is ordered")
		else:
			print(f"Block {block_num} is not ordered")
			#print_all_transactions(eth_w3, block_num)
