import os
import base64
import hashlib
import random
import binascii
from pathlib import Path
from typing import Dict

from pythereum.ecdsa import SigningKey
from pythereum.ecdsa.util import PRNG

SEED_WORD_COUNT = 24
ROOT_DIR = Path(os.path.dirname(__file__))


def create_wallet(*seed) -> Dict[str, str]:
    if not seed:
        with open(str(ROOT_DIR / "seed_wordlist")) as seed_file:
            seed = random.sample(seed_file.read().split("\n"), SEED_WORD_COUNT)
    rng = PRNG(''.join(seed))
    private_key = SigningKey.generate(entropy=rng)
    public_key = private_key.get_verifying_key()

    pem_pub_key = public_key.to_pem()
    hash_pub_key = hashlib.sha256(pem_pub_key).hexdigest()
    ripe_pub_key = hashlib.new("ripemd160")
    ripe_pub_key.update(hash_pub_key.encode())
    hash_pub_key = hashlib.sha256(hashlib.sha256(ripe_pub_key.hexdigest().encode()).hexdigest().encode())
    address = base64.b64encode(hash_pub_key.hexdigest().encode()).decode("utf-8")[:-2]

    return {"public_key": public_key.to_pem().decode("utf-8"),
            "private_key": private_key.to_pem().decode("utf-8"),
            "address": address, "seeds": list(seed)}


def sign_item(private_key, item):
    private_key = SigningKey.from_pem(private_key)
    signed_item = private_key.sign_deterministic(item.encode())
    return binascii.b2a_base64(signed_item, newline=False).decode("utf-8")


def verify_signature(public_key, item):
    pass


def verify_address(public_key, address):
    pass

