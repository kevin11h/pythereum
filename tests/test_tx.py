#!/usr/bin/env python3

from pythereum import generate_wallet, Pythereum

w1 = generate_wallet("bob", "the", "builder")
w2 = generate_wallet()

pth = Pythereum(0)

print("Sending 5 PTH to W2 using three transactions ( 5PTH/tx )")
for i in range(3):
    pth.send_pth(w1["public_key"], w2["public_key"], 5, w1["private_key"])
    pth.mine_block()

print("W1:", pth.get_balance(w1["public_key"]))
print("W2:", pth.get_balance(w2["public_key"]))

print("\nSending 7 PTH from W2 to W3")
w3 = generate_wallet()
pth.send_pth(w2["public_key"], w3["public_key"], 7, w2["private_key"])
pth.mine_block()

print("W2:", pth.get_balance(w2["public_key"]))
print("W3:", pth.get_balance(w3["public_key"]))

print("\nSending 5 PTH from W3 to W1")
pth.send_pth(w3["public_key"], w1["public_key"], 5, w3["private_key"])
pth.mine_block()

print("W1:", pth.get_balance(w1["public_key"]))
print("W2:", pth.get_balance(w2["public_key"]))
print("W3:", pth.get_balance(w3["public_key"]))

print("\nValidating blockchain")
print(pth.verify_chain())


