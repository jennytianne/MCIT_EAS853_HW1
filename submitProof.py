import eth_account
import random
import string
import json
from pathlib import Path
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware  # Necessary for POA chains


def merkle_assignment():
    """
        The only modifications you need to make to this method are to assign
        your "random_leaf_index" and uncomment the last line when you are
        ready to attempt to claim a prime. You will need to complete the
        methods called by this method to generate the proof.
    """
    # Generate the list of primes as integers
    num_of_primes = 8192
    primes = generate_primes(num_of_primes)

    # Create a version of the list of primes in bytes32 format
    leaves = convert_leaves(primes)

    # Build a Merkle tree using the bytes32 leaves as the Merkle tree's leaves
    tree = build_merkle(leaves)

    # Select a random leaf and create a proof for that leaf
    random_leaf_index = random.randint(0, num_of_primes - 1)  # Generate a random index
    proof = prove_merkle(tree, random_leaf_index)

    # This is the same way the grader generates a challenge for sign_challenge()
    challenge = ''.join(random.choice(string.ascii_letters) for i in range(32))
    # Sign the challenge to prove to the grader you hold the account
    addr, sig = sign_challenge(challenge)

    if sign_challenge_verify(challenge, addr, sig):
        # Uncomment the following line when you are ready to attempt to claim a prime
        tx_hash = send_signed_msg(proof, leaves[random_leaf_index])
        print(f"Transaction hash: {tx_hash}")

def is_prime(n):
    """Check if a number is prime."""
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_primes(num_primes):
    """
        Function to generate the first 'num_primes' prime numbers
        returns list (with length n) of primes (as ints) in ascending order
    """
    primes = []
    num = 2
    while len(primes) < num_primes:
        if is_prime(num):
            primes.append(num)
        num += 1
    return primes

def prime_to_bytes32(prime):
        #return Web3.solidity_keccak(['uint256'], [prime])
    return prime.to_bytes(32, 'big')


def convert_leaves(primes_list):
    """
        Converts the leaves (primes_list) to bytes32 format
        returns list of primes where list entries are bytes32 encodings of primes_list entries
    """
    leaves = [prime_to_bytes32(prime) for prime in primes_list]
    return leaves

def build_merkle(leaves):
    """
        Function to build a Merkle Tree from the list of prime numbers in bytes32 format
        Returns the Merkle tree (tree) as a list where tree[0] is the list of leaves,
        tree[1] is the parent hashes, and so on until tree[n] which is the root hash
        the root hash produced by the "hash_pair" helper function
    """

    if not leaves:
        return []

    tree = [leaves]
    current_layer = leaves

    while len(current_layer) > 1:
        next_layer = []
        for i in range(0, len(current_layer), 2):
            if i + 1 < len(current_layer):
                # Normal pair hashing
                next_layer.append(hash_pair(current_layer[i], current_layer[i + 1]))
            else:
                # Odd leaf: hash with itself (OpenZeppelin style)
                next_layer.append(hash_pair(current_layer[i], current_layer[i]))
        tree.append(next_layer)
        current_layer = next_layer

    return tree

def prove_merkle(merkle_tree, random_indx):
    """
        Takes a random_index to create a proof of inclusion for and a complete Merkle tree
        as a list of lists where index 0 is the list of leaves, index 1 is the list of
        parent hash values, up to index -1 which is the list of the root hash.
        returns a proof of inclusion as list of values
    """

    proof = []
    index = random_indx

    for layer in merkle_tree[:-1]:  # Up to but not including root
        if index % 2 == 0:  # Even index: sibling is to the right
            sibling_index = index + 1
        else:  # Odd index: sibling is to the left
            sibling_index = index - 1

        # Only append sibling if it exists in the layer
        if 0 <= sibling_index < len(layer):
            proof.append(layer[sibling_index])

        # Move to parent index
        index //= 2

    return proof

def sign_challenge(challenge):
    """
        Takes a challenge (string)
        Returns address, sig
        where address is an ethereum address and sig is a signature (in hex)
        This method is to allow the auto-grader to verify that you have
        claimed a prime
    """
    acct = get_account()
    addr = acct.address
    eth_encoded_msg = eth_account.messages.encode_defunct(text=challenge)
    eth_sig_obj = acct.sign_message(eth_encoded_msg)
    return addr, eth_sig_obj.signature.hex()


def send_signed_msg(proof, random_leaf):
    """
        Takes a Merkle proof of a leaf, and that leaf (in bytes32 format)
        builds signs and sends a transaction claiming that leaf (prime)
        on the contract
    """
    chain = 'bsc'

    acct = get_account()
    address, abi = get_contract_info(chain)
    w3 = connect_to(chain)
    contract = w3.eth.contract(address=address, abi=abi)

    tx = contract.functions.submit(proof, random_leaf).build_transaction({
        'from': acct.address,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })

    signed_tx = w3.eth.account.sign_transaction(tx, acct.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx['raw_transaction'])

    return tx_hash.hex()


# Helper functions that do not need to be modified
def connect_to(chain):
    """
        Takes a chain ('avax' or 'bsc') and returns a web3 instance
        connected to that chain.
    """
    if chain not in ['avax', 'bsc']:
        print(f"{chain} is not a valid option for 'connect_to()'")
        return None
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    else:
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    w3 = Web3(Web3.HTTPProvider(api_url))
    # inject the poa compatibility middleware to the innermost layer
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    return w3


def get_account():
    """
        Returns an account object recovered from the secret key
        in "sk.txt"
    """
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath('sk.txt'), 'r') as f:
        sk = f.readline().rstrip()
    if sk[0:2] == "0x":
        sk = sk[2:]
    return eth_account.Account.from_key(sk)


def get_contract_info(chain):
    """
        Returns a contract address and contract abi from "contract_info.json"
        for the given chain
    """
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath("contract_info.json"), "r") as f:
        d = json.load(f)
        d = d[chain]
    return d['address'], d['abi']


def sign_challenge_verify(challenge, addr, sig):
    """
        Helper to verify signatures, verifies sign_challenge(challenge)
        the same way the grader will. No changes are needed for this method
    """
    eth_encoded_msg = eth_account.messages.encode_defunct(text=challenge)

    if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == addr:
        print(f"Success: signed the challenge {challenge} using address {addr}!")
        return True
    else:
        print(f"Failure: The signature does not verify!")
        print(f"signature = {sig}\naddress = {addr}\nchallenge = {challenge}")
        return False


def hash_pair(a, b):
    """
        The OpenZeppelin Merkle Tree Validator we use sorts the leaves
        https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/MerkleProof.sol#L217
        So you must sort the leaves as well

        Also, hash functions like keccak are very sensitive to input encoding, so the solidity_keccak function is the function to use

        Another potential gotcha, if you have a prime number (as an int) bytes(prime) will *not* give you the byte representation of the integer prime
        Instead, you must call int.from_bytes(prime,'big').
    """
    if a < b:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [a, b])
    else:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [b, a])


if __name__ == "__main__":
    merkle_assignment()



