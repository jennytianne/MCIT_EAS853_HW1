from web3 import Web3
import eth_account
from eth_account import Account
from eth_account.messages import encode_defunct

'''
Takes in a single message m, 
creates an eth account, and uses the account’s key-pair to sign the message m. 
Return the Ethereum account address that the signature is valid under, as well as the signature.
'''
def sign(m):
    w3 = Web3()

    # TODO create an account for signing the message
    account = Account.create()  # Create an Eth account
    public_key = account.address  # Eth account address
    private_key = account.key  # Eth account private key

    # TODO sign the given message "m"
    message = encode_defunct(text=m)  # Encode the message
    signed_message = w3.eth.account.sign_message(message, private_key=private_key)  # Sign the message


    """You can save the account public/private keypair that prints in the next section
     for use in future assignments. You will need a funded account to pay gas fees for 
     several upcoming assignments and the first step of funding an account is having 
     an account to send the funds too.
    """
    print('Account created:\n'
          f'private key={w3.to_hex(private_key)}\naccount={public_key}\n')
    assert isinstance(signed_message, eth_account.datastructures.SignedMessage)
    print(f"signed message {signed_message}\nr= {signed_message.r}\ns= {signed_message.s}")

    return public_key, signed_message

'''
Verify the 'signed_message' is valid given the original message 'm' and the signers 'public_key'
Return a boolean 
'''
def verify(m, public_key, signed_message):
    w3 = Web3()

    # Encode the message
    message = encode_defunct(text=m)
    # Get the address of the account that signed the given message
    signer_address = w3.eth.account.recover_message(message, signature=signed_message.signature)
    # Check if the recovered signer matches the provided Ethereum address
    valid_signature = signer_address == public_key  # True if message verifies, False if message does not verify

    assert isinstance(valid_signature, bool), "verify should return a boolean value"
    return valid_signature


if __name__ == "__main__":
    import random
    import string

    for i in range(3):
        m = "".join([random.choice(string.ascii_letters) for _ in range(20)])

        pub_key, signature = sign(m)

        print(verify(m, pub_key, signature))


        # Modifies every other message so that the signature fails to verify
        if i % 2 == 0:
            m = m + 'a'

        if verify(m, pub_key, signature):
            print("Signed Message Verified")
        else:
            print("Signed Message Failed to Verify")
