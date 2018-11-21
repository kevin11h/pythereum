import os
import random
import binascii
from pathlib import Path
from typing import Dict

from pythereum.ecdsa import SigningKey, VerifyingKey, BadSignatureError, NIST192p
from pythereum.ecdsa.util import PRNG

SEED_WORD_COUNT = 24
ROOT_DIR = Path(os.path.dirname(__file__))


def generate_wallet(*seed: str) -> Dict[str, str]:
    """
    Creates the key pair of a wallet. Converts the public key to an address.
    If seed is not passed, random words are picked from a wordlist.

    :param seed: Entropy for the key generate function
    :return: Dictionary -> {
                            "public_key": "pub_key_base64_encoded",
                            "private_key": "priv_key_base64_encoded",
                            "seed": ("list", "of", "words", "used", "to", "generate", "wallet")
                            }
    """

    if not seed:
        with open(str(ROOT_DIR / "seed_wordlist")) as seed_file:
            seed = random.sample(seed_file.read().split("\n"), SEED_WORD_COUNT)
    else:
        seed = list(map(str, seed))
    rng = PRNG(''.join(seed))
    private_key = SigningKey.generate(entropy=rng, curve=NIST192p)
    public_key = private_key.get_verifying_key()

    return {"public_key": binascii.b2a_base64(public_key.to_string(), newline=False).decode("utf-8"),
            "private_key": binascii.b2a_base64(private_key.to_string(), newline=False).decode("utf-8"),
            "seed": tuple(seed)}


def generate_public_key(private_key: str) -> str:
    """
    Given a private key, this function will generate and return
    the corresponding public key to that private key

    :param private_key: Private Key
    :return str: Public Key corresponding to that private key
    """
    private_key = SigningKey.from_string(binascii.a2b_base64(private_key), curve=NIST192p)
    return private_key.get_verifying_key().to_pem().decode("utf-8")


def sign_item(private_key, item):
    """
    Can sign a string using a private key

    :param private_key: Private Key
    :param item: a string that is to be signed
    :return str: a base64 encoded representation of the signature
    """

    private_key = SigningKey.from_string(binascii.a2b_base64(private_key), curve=NIST192p)
    signed_item = private_key.sign_deterministic(item.encode())

    return binascii.b2a_base64(signed_item, newline=False).decode("utf-8")


def verify_signature(signature, item, public_key) -> bool:
    """
    Given a base64 encoded signature, a string representation of an item and the public key,
    this function is able to verify the signature.

    :param signature: Base64 encoded representation of the signature
    :param item: String representation of an item
    :param public_key: Public key
    :return: bool indicating if the signature is correct or not
    """
    public_key = VerifyingKey.from_string(binascii.a2b_base64(public_key), curve=NIST192p)
    signature = binascii.a2b_base64(signature)

    try:
        public_key.verify(signature, item.encode())
        return True
    except BadSignatureError:
        return False


def verify_key_pair(public_key, private_key) -> bool:
    """
    Given a public / private key pair in PEM format, this function is able to
    verify that they are the correct corresponding key pair to each other

    :param public_key: Public Key
    :param private_key: Private Key
    :return: bool indicating if the key pair is correct or not
    """

    private_key = SigningKey.from_string(binascii.a2b_base64(private_key), curve=NIST192p)
    expected_public_key = private_key.get_verifying_key()

    return binascii.b2a_base64(expected_public_key.to_string(), newline=False).decode("utf-8") == public_key
