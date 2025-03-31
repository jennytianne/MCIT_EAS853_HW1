import random
import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware  # Import the middleware
from web3.providers.rpc import HTTPProvider
import eth_account
from eth_account import Account
from eth_account.messages import encode_defunct
import secrets
from eth_utils import to_hex

AVALANCHE_FUJI_RPC = "https://api.avax-test.network/ext/bc/C/rpc"
w3 = Web3(Web3.HTTPProvider(AVALANCHE_FUJI_RPC))

if w3.is_connected():
    print("Connected to Avalanche Fuji Testnet")
else:
    print("Connection failed")

# The second section requires you to inject middleware into your w3 object and
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# Load ABI from the file
with open("NFT.abi", "r") as abi_file:
    NFT_CONTRACT_ABI = json.load(abi_file)

NFT_CONTRACT_ADDRESS = "0x85ac2e065d4526FBeE6a2253389669a12318A412"

# create a contract object
contract = w3.eth.contract(address=w3.to_checksum_address(NFT_CONTRACT_ADDRESS), abi=NFT_CONTRACT_ABI)
print("NFT contract loaded successfully!")

print(contract.all_functions())

# Load in my wallet:
private_key = "0xbbb83313afb7060cea7e71f5cf38d2251b16d3b1573312dc9dafcefad72baa0f"
wallet_address = "0x6eea9D6aAEd0e24FBD82A96a1710B3Fe7D368b17"

# Generate a random 32-byte nonce (a random value)
nonce = secrets.token_bytes(32)

# Convert the nonce to its hexadecimal representation
nonce_hex = to_hex(nonce)
print("nonce:", nonce_hex)
# Build the transaction for the claim() function
tx = contract.functions.claim(wallet_address, nonce_hex).build_transaction({
    'from': wallet_address,
    'gas': 200000,  # Adjust gas limit as needed
    'gasPrice': w3.eth.gas_price,  # Fetch current gas price
    'nonce': w3.eth.get_transaction_count(wallet_address),  # Fetch nonce for your wallet
    'chainId': 43113  # Fuji Testnet Chain ID
})

# Sign the transaction with your private key
signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)

# Send the signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

# Convert transaction hash to hex for readability
tx_hash_hex = w3.to_hex(tx_hash)
print(f"Transaction sent! Tx hash: {tx_hash_hex}")

# Optionally wait for transaction receipt
print("Waiting for transaction to be mined...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Transaction mined! Gas used: {tx_receipt.gasUsed}")
print(f"Transaction receipt: {tx_receipt}")
