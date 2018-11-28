import time
import secrets
import hashlib

from pythereum.block import Block
from pythereum.mempool import Mempool
from pythereum.compile import CompileContract
from pythereum.transaction import Transaction, Contract, Message
from pythereum.wallet import sign_item


class Pythereum:
    def __init__(self, difficulty=4):
        self.__difficulty = int(difficulty)

        genesis_transaction = Transaction(t_from="luPzDifFO0PBHx9MoVrEuBDuJ3DPvBdWm4PTeltKMewt6HG7gkwqyWcRULb5l37Y",
                                          t_to="luPzDifFO0PBHx9MoVrEuBDuJ3DPvBdWm4PTeltKMewt6HG7gkwqyWcRULb5l37Y",
                                          signature="0FAB5A6X8h7amAkjiuz5IbQUdKdNUQmvDDW50/hXrFykg6BYbzcJ4Ar9s2v1B09z",
                                          input_txids="null",
                                          value=1000000000000)
        self.__chain = [Block(block_number=0, block_nonce=secrets.token_hex(16),
                              previous_block_hash=None,
                              transactions=[genesis_transaction]).jsonify()]

        self.__mempool = Mempool

    @property
    def top_block(self):
        if self.__chain:
            return self.__chain[-1]
        return None

    @property
    def blocks(self):
        return self.__chain or None

    @property
    def difficulty(self):
        return self.__difficulty

    def get_mempool(self, mem_type):
        if mem_type == "transactions":
            return self.__mempool.transactions
        elif mem_type == "contracts":
            return self.__mempool.contracts
        elif mem_type == "messages":
            return self.__mempool.messages
        return None

    def send_pth(self, t_from, t_to, value, private_key, *, data=None):
        value = float(value)

        assert t_from != t_to, "Cannot send PTH to yourself"
        assert self.get_balance(t_from) >= value, f"Not enough balance to send {value} PTH"

        utxos = self.get_utxo(t_from)
        txs = []
        for block in self.__chain[::-1]:
            for txid, tx in block["data"]["transactions"].items():
                if txid in utxos:
                    txs.append(tx)

        utxos = []
        value_left = value
        for tx in txs:
            if tx["amount"] > value:
                utxos = [tx["txid"]]
                break
            elif value_left - tx["amount"] <= 0:
                utxos.append(tx["txid"])
                break
            else:
                utxos.append(tx["txid"])
                value_left -= tx["amount"]

        signature = sign_item(private_key, f"{value}{t_from}")
        tx = Transaction(t_from=t_from, t_to=t_to, value=value, signature=signature, input_txids=utxos,
                         data=data)
        self.__mempool.add_transaction(tx)
        return tx.jsonify()

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
                    balance -= tx["amount"]
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
            if block["data"]["contracts"]:
                for ccxid, cx in block["data"]["contracts"].items():
                    if ccxid == cxid:
                        return cx
        return None

    def get_contract_state(self, cxid):
        for block in self.__chain[::-1]:
            if block["data"]["messages"]:
                for mxid, mx in block["data"]["messages"].items():
                    if mx["to"] == cxid:
                        return mx["data"]["reply"]["state_vars"]
            if block["data"]["contracts"]:
                for ccxid, cx in block["data"]["contracts"].items():
                    if ccxid == cxid:
                        return cx["state"]["state_vars"]
        return None

    def get_all_emits(self, cxid, list_only=False):
        emits = {}
        for block in self.__chain[::-1]:
            if block["data"]["messages"]:
                for mxid, mx in block["data"]["messages"].items():
                    if mx["to"] == cxid:
                        emits[mxid] = mx["data"]["reply"]["emits"]
        return emits if not list_only else list(emits.values())

    def get_block(self, block_id):
        if isinstance(block_id, int):
            return self.__chain[block_id]
        for block in self.__chain[::-1]:
            if block["block_hash"] == block_id:
                return block
        return None

    def create_contract(self, code, public_key, private_key):
        signature = sign_item(private_key, code)
        contract = Contract(code, public_key, signature)
        self.__mempool.add_contract(contract)
        return contract.jsonify()

    def call_contract(self, cxid, gas, data, public_key, private_key):
        signature = sign_item(private_key, str(data))
        message = Message(public_key, cxid, signature, data, gas)

        contract = self.get_contract(cxid)
        if not contract:
            raise LookupError("Contract not found")
        contract_state = self.get_contract_state(cxid)

        compiled_contract = CompileContract(contract["code"], contract_state, sender=public_key)
        runtime = (gas // 1000) * 0.1  # get 100 ms for every 1000 gas sent
        if not isinstance(data, list):
            data = [data]
        compiled_contract.run(runtime, *data)
        state = compiled_contract.jsonify()
        del state["code"]

        message_json = message.jsonify()
        message_json["data"]["reply"] = state

        self.__mempool.add_message(message_json)
        return message_json

    def __getitem__(self, item):
        return self.get_block(item)

    def mine_block(self, *, n_tx=5, n_cx=5, n_mx=5):
        transactions = self.__mempool.pop_transactions(n_tx)
        tx_to_drop = []
        input_total = {}  # txid => amount
        available_utxos = {}  # user_key => [unspent, utxos]

        # Validate each transaction
        for tx in transactions:
            t_from = tx["from"]
            txid = tx["txid"]

            if t_from not in available_utxos:
                available_utxos[t_from] = self.get_utxo(t_from)
            if not available_utxos[t_from]:  # No available utxos for this person
                tx_to_drop.append(txid)
                continue
            elif "change_from" in tx:  # Change tx should not be in mempool
                tx_to_drop.append(txid)

            # Get transaction input total
            input_total[txid] = 0
            for input_txid in tx["input_txids"]:

                # Cannot reuse same utxo
                if input_txid not in available_utxos[t_from] or tx["input_txids"].count(input_txid) > 1:
                    tx_to_drop.append(txid)
                    break
                i_tx = self.get_transaction(input_txid)
                input_total[txid] += i_tx["amount"]
            if tx_to_drop and tx_to_drop[-1] == txid:
                continue
            elif tx["amount"] > input_total[txid]:
                tx_to_drop.append(txid)
                continue
            else:
                for input_txid in tx["input_txids"]:
                    available_utxos[t_from].remove(input_txid)

        # Drop all invalid transactions
        transactions[:] = [t for t in transactions if t.get("txid") not in tx_to_drop]
        for txid in tx_to_drop:
            if txid in input_total:
                del input_total[txid]

        # Create change Transaction
        change_tx = []
        for tx in transactions:
            txid = tx["txid"]
            if input_total[txid] > tx["amount"]:
                # Create change transaction here
                change_amount = input_total[txid] - tx["amount"]
                change_tx.append({
                    "from": tx["to"],
                    "to": tx["from"],
                    "time": time.time(),
                    "amount": change_amount,
                    "signature": "null",
                    "input_txids": "null",
                    "txid": hashlib.sha256(f"{tx['to']}{tx['from']}{change_amount}{time.time()}{txid}".encode()
                                           ).hexdigest(),
                    "change_from": txid
                })
            tx["amount"] = input_total[txid]
        transactions.extend(change_tx)
        contracts = self.__mempool.pop_contracts(n_cx)
        messages = self.__mempool.pop_messages(n_mx)

        block = Block(block_number=len(self.__chain), block_nonce=secrets.token_hex(17),
                      previous_block_hash=self.__chain[-1]["block_hash"],
                      transactions=transactions, contracts=contracts, messages=messages)

        while not block.hash.startswith('0'*self.__difficulty):
            block.nonce = secrets.token_hex(16)
            block.update_time()
            block.update_hash()

        self.__chain.append(block.jsonify())
        return block.jsonify()
