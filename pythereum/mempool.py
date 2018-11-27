import random
import time


class Mempool:
    transactions = {}
    contracts = {}
    messages = {}

    # Add transaction to transaction dictionary
    @classmethod
    def add_transaction(cls, transaction):
        if not isinstance(transaction, dict):
            transaction = transaction.jsonify()
        cls.transactions[transaction["txid"]] = transaction

    # Add contract to contracts dictionary
    @classmethod
    def add_contract(cls, contract):
        if isinstance(contract, dict):
            cls.contracts[contract["cxid"]] = contract
        else:
            cls.contracts[contract.cxid] = contract.jsonify()

    # Add message to messages dictionary
    @classmethod
    def add_message(cls, message):
        if isinstance(message, dict):
            cls.messages[message["mxid"]] = message
        else:
            cls.messages[message.mxid] = message.jsonify()

    # Pop transactions from transactions dictionary
    @classmethod
    def pop_transactions(cls, n=5):
        for txid, tx in cls.transactions.items():
            if time.time() - tx["time"] > 300:
                del cls.transactions[txid]

        n = min(len(cls.transactions), n, 10)
        s_tx = random.sample(cls.transactions.keys(), n)

        txs = []
        for txid in s_tx:
            txs.append(cls.transactions[txid])
            del cls.transactions[txid]
        return txs

    # Pop contracts from contracts dictionary
    @classmethod
    def pop_contracts(cls, n=5):
        for cxid, cx in cls.contracts.items():
            if time.time() - cx["time"] > 300:
                del cls.contracts[cxid]

        n = min(len(cls.contracts), n, 10)
        s_cx = random.sample(cls.contracts.keys(), n)

        cxs = []
        for cxid in s_cx:
            cxs.append(cls.contracts[cxid])
            del cls.contracts[cxid]
        return cxs

    # Pop messages from messages dictionary
    @classmethod
    def pop_messages(cls, n=5):
        for mxid, mx in cls.messages.items():
            if time.time() - mx["time"] > 300:
                del cls.messages[mxid]

        n = min(len(cls.messages), n, 10)
        s_mx = random.sample(cls.messages.keys(), n)

        mxs = []
        for mxid in s_mx:
            mxs.append(cls.messages[mxid])
            del cls.messages[mxid]
        return mxs
