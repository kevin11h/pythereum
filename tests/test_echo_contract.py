#!/usr/bin/env python3

from pythereum import Pythereum, generate_wallet

w1 = generate_wallet("bob", "the", "builder")

pth = Pythereum(0)

print("Creating a simple 'echo' contract")
pth.create_contract("""
def main(x):
    print(x)
    return state(), printed
""", w1["public_key"], w1["private_key"])
pth.mine_block()

input("\nPress RETURN to see block with contract")
print(pth.top_block)

input("\nPress RETURN to move to next section")
print("Calling echo contract with 3 different calls")
print("Calling contract with values 'Hello World', 'Hello Earth', 'Hi Garrett'")
cxid = list(pth.top_block["data"]["contracts"].keys())[0]
pth.call_contract(cxid, 5000, "Hello World", w1["public_key"], w1["private_key"])
pth.call_contract(cxid, 5000, "Hello Earth", w1["public_key"], w1["private_key"])
pth.call_contract(cxid, 5000, "Hi Garrett", w1["public_key"], w1["private_key"])

pth.mine_block()

input("\nPress RETURN to move to next section")
print("\nAll emits done by contract {message_id => [emits]}")
print(pth.get_all_emits(cxid))
print("\nGetting all emits again, but without the message ids")
print(pth.get_all_emits(cxid, True))


input("\nPress RETURN to see block with messages")
print(pth.top_block)

