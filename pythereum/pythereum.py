import secrets

from pythereum.block import Block
from pythereum.mempool import Mempool
from pythereum.transaction import Transaction, Contract, Message
from pythereum.wallet import verify_key_pair, sign_item, verify_signature


class Pythereum:
    def __init__(self, difficulty=4):
        self.__difficulty = int(difficulty)

        genesis_transaction = Transaction(t_from="luPzDifFO0PBHx9MoVrEuBDuJ3DPvBdWm4PTeltKMewt6HG7gkwqyWcRULb5l37Y",
                                          t_to="luPzDifFO0PBHx9MoVrEuBDuJ3DPvBdWm4PTeltKMewt6HG7gkwqyWcRULb5l37Y",
                                          signature="0FAB5A6X8h7amAkjiuz5IbQUdKdNUQmvDDW50/hXrFykg6BYbzcJ4Ar9s2v1B09z",
                                          input_txids="null",
                                          value=1000000000000,
                                          txid_amount=1000000000000)
        self.__chain = [Block(block_number=1, block_nonce=secrets.token_hex(16),
                              previous_block_hash=None,
                              transactions=[genesis_transaction]).jsonify()]

        self.__mempool = Mempool

    def send_pth(self, t_from, t_to, value, private_key, *, data=None, change_address=None):
        assert t_from != t_to, "Cannot send PTH to yourself"
        assert verify_key_pair(t_from, private_key), "Invalid key pair (t_from / private_key)"
        assert self.get_balance(t_from) > value, f"Not enough balance to send {value} PTH"

        value = float(value)

        utxos = self.get_utxo(t_from)
        txs = []
        for block in self.__chain[::-1]:
            for txid, tx in block["data"]["transactions"].items():
                if txid in utxos:
                    txs.append(tx)

        utxos = []
        tx_total = 0
        value_left = value
        for tx in txs:
            if tx["amount"] > value:
                utxos = [tx["txid"]]
                tx_total = tx["amount"]
                break
            elif value_left - tx["amount"] <= 0:
                utxos.append(tx["txid"])
                tx_total += tx["amount"]
                break
            else:
                utxos.append(tx["txid"])
                value_left -= tx["amount"]
                tx_total += tx["amount"]

        signature = sign_item(private_key, f"{value}{t_from}")
        tx = Transaction(t_from=t_from, t_to=t_to, value=value, signature=signature, input_txids=utxos,
                         txid_amount=tx_total, data=data, change_address=change_address)
        self.__mempool.add_transaction(tx)

    def get_transaction(self, txid):
        for block in self.__chain[::-1]:
            for ttxid in block["data"]["transactions"].keys():
                if ttxid == txid:
                    return block["data"]["transactions"][txid]
        return None

    def get_balance(self, public_key):
        balance = 0
        for block in self.__chain[::-1]:
            for _, tx in block["data"]["transactions"].items():
                if tx["to"] == public_key:
                    balance += tx["amount"]
                elif tx["from"] == public_key:
                    balance -= tx["value"]
        return balance

    def get_utxo(self, public_key):
        utxos = []
        for block in self.__chain[::-1]:
            for txid, tx in block["data"]["transactions"].items():
                if tx["to"] == public_key:
                    utxos.append(txid)

                for input_txs in tx["input_txids"]:
                    if input_txs in utxos:
                        utxos.remove(input_txs)
        return utxos

    def get_contract(self, cxid):
        for block in self.__chain[::-1]:
            for ccxid, cx in block["data"]["contracts"].items():
                if ccxid == cxid:
                    return cxid
        return None

    def get_contract_state(self, cxid):
        pass

    def get_block(self, block_id):
        if isinstance(block_id, int):
            return self.__chain[block_id]
        for block in self.__chain[::-1]:
            if block["block_hash"] == block_id:
                return block
        return None

    def create_contract(self, code, public_key, private_key):
        pass

    def call_contract(self, cxid, gas, public_key, private_key):
        pass

    def __getitem__(self, item):
        return self.get_block(item)

    def __iadd__(self, other):
        pass

    def mine_block(self):
        pass
