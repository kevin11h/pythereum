import os
import base64
import hashlib
import random
import binascii
from pathlib import Path
from typing import Dict

from pythereum.ecdsa import SigningKey, VerifyingKey, BadSignatureError
from pythereum.ecdsa.util import PRNG

SEED_WORD_COUNT = 24
ROOT_DIR = Path(os.path.dirname(__file__))


def create_wallet(*seed: str) -> Dict[str, str]:
    """
    Creates the key pair of a wallet. Converts the public key to an address.
    If seed is not passed, random words are picked from a wordlist.

    :param seed: Entropy for the key generate function
    :return: Dictionary -> {
                            "public_key": "pub_key_in_pem_format",
                            "private_key": "priv_key_in_pem_format",
                            "address": "pub_key_hashed_to_address_format",
                            "seed": ("list", "of", "words", "used", "to", "generate", "wallet")
                            }
    """

    if not seed:
        with open(str(ROOT_DIR / "seed_wordlist")) as seed_file:
            seed = random.sample(seed_file.read().split("\n"), SEED_WORD_COUNT)
    else:
        seed = list(map(str, seed))
    rng = PRNG(''.join(seed))
    private_key = SigningKey.generate(entropy=rng)
    public_key = private_key.get_verifying_key()

    pem_pub_key = public_key.to_pem().decode("utf-8")

    return {"public_key": pem_pub_key,
            "private_key": private_key.to_pem().decode("utf-8"),
            "address": generate_address(pem_pub_key),
            "seed": tuple(seed)}


def generate_address(public_key: str) -> str:
    """
    Given a PEM formatted public_key, this function will generate and return
    the corresponding address to that key.

    :param public_key: Public Key in PEM format
    :return str: address corresponding to that public key
    """
    hash_pub_key = hashlib.sha256(public_key.encode()).hexdigest()
    ripe_pub_key = hashlib.new("ripemd160")
    ripe_pub_key.update(hash_pub_key.encode())
    hash_pub_key = hashlib.sha256(hashlib.sha256(ripe_pub_key.hexdigest().encode()).hexdigest().encode())
    address = base64.b64encode(hash_pub_key.hexdigest().encode()).decode("utf-8")[:-2]

    return address


def generate_public_key(private_key: str) -> str:
    """
    Given a PEM formatted private key, this function will generate and return
    the corresponding public key to that private key

    :param private_key: Private Key in PEM format
    :return str: Public Key corresponding to that private key
    """
    private_key = SigningKey.from_pem(private_key)
    return private_key.get_verifying_key().to_pem().decode("utf-8")


def sign_item(private_key, item):
    """
    Can sign a string using a PEM formatted private key

    :param private_key: Private Key in PEM format
    :param item: a string that is to be signed
    :return str: a base64 encoded representation of the signature
    """

    private_key = SigningKey.from_pem(private_key)
    signed_item = private_key.sign_deterministic(item.encode())

    return binascii.b2a_base64(signed_item, newline=False).decode("utf-8")


def verify_signature(signature, item, public_key) -> bool:
    """
    Given a base64 encoded signature, a string representation of an item and the public key,
    this function is able to verify the signature.

    :param signature: Base64 encoded representation of the signature
    :param item: String representation of an item
    :param public_key: Public key in PEM format
    :return: bool indicating if the signature is correct or not
    """
    public_key = VerifyingKey.from_pem(public_key)
    signature = binascii.a2b_base64(signature)

    try:
        public_key.verify(signature, item.encode())
        return True
    except BadSignatureError:
        return False


def verify_address(public_key, address) -> bool:
    """
    Given a PEM formatted public_key and an address, this function is able to verify
    that the address corresponds to that specific public key

    :param public_key: Public key in PEM format
    :param address: Address to be checked against
    :return: bool indicating if the address is correct or not
    """
    return address == generate_address(public_key)


def verify_key_pair(public_key, private_key) -> bool:
    """
    Given a public / private key pair in PEM format, this function is able to
    verify that they are the correct corresponding key pair to each other

    :param public_key: Public Key in PEM format
    :param private_key: Private Key in PEM format
    :return: bool indicating if the key pair is correct or not
    """
    
    private_key = SigningKey.from_pem(private_key)
    expected_public_key = private_key.get_verifying_key()

    return expected_public_key.to_pem().decode("utf-8") == public_key
