#!/usr/bin/env python3

from pythereum import Pythereum, generate_wallet

print("Creating two wallets; W1 & W2")
w1 = generate_wallet("bob", "the", "builder")
w2 = generate_wallet()

pth = Pythereum(0)

print("Creating contract")
code = """
owner = msg_sender
times_called = 0

def main():
    if msg_sender == owner:
        print("Thanks for calling me!")
        state("times_called", state("times_called")+1)
        print("I have updated times_called to " + str(state("times_called")))
    else:
        print("You are not my owner. GO AWAY!")

    return state(), printed
"""
print("The following code will be pushed\n\n", code, "\n\n")
pth.create_contract(code, w1["public_key"], w1["private_key"])
pth.mine_block()

input("\n...\n")


cxid = list(pth.top_block["data"]["contracts"].keys())[0]

print("Calling function as owner")
pth.call_contract(cxid, 10000, None, w1["public_key"], w1["private_key"])
pth.mine_block()
input("\n...\n")
print("Printing summary of emits made by contract")
print(pth.get_all_emits(cxid, True))

input("\nPress RETURN to continue\n")
print("Calling function as another user")
pth.call_contract(cxid, 10000, None, w2["public_key"], w2["private_key"])

pth.mine_block()
input("\n...\n")
print("Printing updated emits")
print(pth.get_all_emits(cxid, True))


input("\nPress RETURN to continue")
print("Calling function again 3 times as owner")
for i in range(3):
    pth.call_contract(cxid, 10000, None, w1["public_key"], w1["private_key"])
    pth.mine_block()
input("\n...\n")
print(pth.get_all_emits(cxid, True))
input("\n...\n")
print("\n\nEmits and state updates also include the message id", pth.get_all_emits(cxid))
input("\n...\n")
print("\n\n", pth.get_contract_state(cxid))
