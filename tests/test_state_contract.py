#!/usr/bin/env python3

from pythereum import Pythereum, generate_wallet

w1 = generate_wallet("bob", "the", "builder")
w2 = generate_wallet()

pth = Pythereum(0)

print("Creating contract")
pth.create_contract("""
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
""", w1["public_key"], w1["private_key"])

pth.mine_block()
print(pth.top_block)

input("\nPress RETURN to call the function")
cxid = list(pth.top_block["data"]["contracts"].keys())[0]

print("Calling function as owner")
pth.call_contract(cxid, 10000, None, w1["public_key"], w1["private_key"])
pth.mine_block()
print(pth.get_all_emits(cxid, True))

input("\nPress RETURN to continue")
print("Calling function as another user")
pth.call_contract(cxid, 10000, None, w2["public_key"], w2["private_key"])

pth.mine_block()
print(pth.get_all_emits(cxid, True))


input("\nPress RETURN to continue")
print("Calling function again and again as owner")
for i in range(3):
    pth.call_contract(cxid, 10000, None, w1["public_key"], w1["private_key"])
    pth.mine_block()

print(pth.get_all_emits(cxid, True))
print("\n\n", pth.get_contract_state(cxid))
