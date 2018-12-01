#!/usr/bin/env python3

from pythereum import generate_wallet, sign_item


wallet = generate_wallet()

print(wallet)

input("\n...\n")
print("Signing the following string -> 'Hello World'")

sign = sign_item(w["private_key"], "Hello World")

print(sign)




