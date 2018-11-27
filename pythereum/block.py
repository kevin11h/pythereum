import time
import hashlib
from typing import List

from pythereum.transaction import Transaction, Contract, Message


class MerkleTree:
    def __init__(self, *leaves):
        self.__leaves = list(leaves)
        self.__levels = None
        self.ready = False

    def add_leaf(self, leaves) -> None:
        self.ready = False
        if isinstance(leaves, str):
            leaves = [leaves]
        for leaf in leaves:
            self.__leaves.append(leaf)

    def __len__(self):
        return len(self.__leaves)

    def __getitem__(self, index):
        return self.__leaves[index]

    def __iter__(self):
        self.__iter = -1
        return self

    def __next__(self):
        self.__iter += 1
        if self.__iter < len(self):
            return self.__leaves[self.__iter]
        raise StopIteration

    @property
    def ready_state(self):
        return self.ready

    @property
    def root(self):
        return self.__levels[0][0] if self.ready_state and self.__levels else None

    def make_tree(self):
        if len(self):
            self.__levels = [self.__leaves]
            while len(self.__levels[0]) > 1:
                n = len(self.__levels[0])
                if n % 2:
                    solo_leaf = self.__levels[0][-1]
                    n -= 1
                else:
                    solo_leaf = None
                new_level = []
                for left, right in zip(self.__levels[0][0:n:2], self.__levels[0][1:n:2]):
                    new_level.append(hashlib.sha256(f"{left}{right}".encode()).hexdigest())
                if solo_leaf:
                    new_level.append(solo_leaf)
                self.__levels = [new_level] + self.__levels
            self.ready = True


class Block:
    def __init__(self, *, block_number, block_nonce, previous_block_hash,
                 transactions: List[Transaction]=None,
                 contracts: List[Contract]=None,
                 messages: List[Message]=None):
        self.__number = int(block_number)
        self.__time = time.time()
        self.__nonce = str(block_nonce)
        self.__previous_block_hash = previous_block_hash

        if transactions:
            if not isinstance(transactions, list):
                transactions = [transactions]
            for i, tx in enumerate(transactions):
                if isinstance(tx, Transaction):
                    transactions[i] = tx.jsonify()
            self.__transactions = {}
            for tx in transactions:
                self.__transactions[tx["txid"]] = tx
            merkle_tx = MerkleTree(*list(self.__transactions.keys()))
            merkle_tx.make_tree()
            self.__merkle_tx = merkle_tx.root
        else:
            self.__transactions = None
            self.__merkle_tx = None

        if contracts:
            if not isinstance(contracts, list):
                contracts = [contracts]
            self.__contracts = {}
            for cx in contracts:
                self.__contracts[cx["cxid"]] = cx
            merkle_cx = MerkleTree(*list(self.__contracts.keys()))
            merkle_cx.make_tree()
            self.__merkle_cx = merkle_cx.root
        else:
            self.__contracts = None
            self.__merkle_cx = None

        if messages:
            if not isinstance(messages, list):
                messages = [messages]
            self.__messages = {}
            for mx in messages:
                self.__messages[mx["mxid"]] = mx
            merkle_mx = MerkleTree(*list(self.__messages.keys()))
            merkle_mx.make_tree()
            self.__merkle_mx = merkle_mx.root
        else:
            self.__messages = None
            self.__merkle_mx = None

        self.__block_hash: str = hashlib.sha256(
            f"{self.number}{self.time}{self.nonce}{self.previous_block_hash}".encode()
        ).hexdigest()

    @property
    def number(self):
        return self.__number

    @property
    def time(self):
        return self.__time

    def update_time(self):
        self.__time = time.time()

    @property
    def nonce(self):
        return self.__nonce

    @nonce.setter
    def nonce(self, nonce):
        assert isinstance(nonce, str) and len(nonce) == 32, f"Invalid nonce {nonce}, {len(nonce)}"
        self.__nonce = nonce

    @property
    def previous_block_hash(self):
        return self.__previous_block_hash

    @property
    def transactions(self):
        return self.__transactions

    @property
    def contracts(self):
        return self.__contracts

    @property
    def messages(self):
        return self.__messages

    @property
    def hash(self):
        return self.__block_hash

    def update_hash(self):
        self.__block_hash = hashlib.sha256(
            f"{self.number}{self.time}{self.nonce}{self.previous_block_hash}".encode()
        ).hexdigest()

    def merkle_root(self, mtype):
        if mtype == "transactions":
            return self.__merkle_tx
        elif mtype == "contracts":
            return self.__merkle_cx
        elif mtype == "messages":
            return self.__merkle_mx
        return None

    def __str__(self) -> str:
        return self.hash

    def __eq__(self, other_block):
        return self.hash == other_block.hash

    def jsonify(self):
        return {
            "header": {
                "block_number": self.number,
                "block_time": self.time,
                "block_nonce": self.nonce,
                "previous_block_hash": self.previous_block_hash,
                "merkle_root": {
                    "transactions": self.merkle_root("transactions"),
                    "contracts": self.merkle_root("contracts"),
                    "messages": self.merkle_root("messages")
                }
            },
            "data": {
                "transactions": self.transactions,
                "contracts": self.contracts,
                "messages": self.messages
            },
            "block_hash": self.hash
        }

    def validate(self) -> bool:
        return hashlib.sha256(
            f"{self.number}{self.time}{self.nonce}{self.previous_block_hash}".encode()
        ).hexdigest() == self.hash
