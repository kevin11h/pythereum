import time
import hashlib

from pythereum.compile import CompileContract
from pythereum.wallet import verify_signature


class Transaction:
    """
    Send coins from an external wallet to another external wallet. Can include an optional data field for
    message / notes.
    """

    def __init__(self, t_from, t_to, value, signature, input_txids, *, data=None):
        self.__from = str(t_from)
        self.__to = str(t_to)
        self.__amount = float(value)
        self.__data = str(data)
        self.__signature = str(signature)

        assert verify_signature(signature=self.__signature, item=f"{value}{t_from}", public_key=self.__from), \
            "Invalid Signature"

        self.__time = None

        if isinstance(input_txids, list):
            self.__input_txids = [*input_txids]
        elif isinstance(input_txids, str):
            self.__input_txids = [input_txids]
        else:
            self.__input_txids = []

        self.__time = time.time()

        self.__txid = hashlib.sha256(f"{self.__from}{self.__to}{self.__amount}{self.__time}"
                                     f"{''.join(self.__input_txids)}".encode()
                                     ).hexdigest()

    @property
    def txid(self):
        return self.__txid

    @property
    def t_from(self):
        return self.__from

    @property
    def t_to(self):
        return self.__to

    @property
    def amount(self):
        return self.__amount

    @property
    def signature(self):
        return self.__signature

    @property
    def input_txids(self):
        return self.__input_txids

    def jsonify(self):
        return {
            "from": self.__from,
            "to": self.__to,
            "time": self.__time,
            "signature": self.__signature,
            "amount": self.__amount,
            "txid": self.txid,
            "input_txids": self.input_txids,
            "data": self.__data
        }


class Contract:
    def __init__(self, code, t_from, signature):
        self.__time = time.time()
        self.__code = str(code)
        self.__from = str(t_from)
        self.__signature = str(signature)

        assert verify_signature(signature=self.__signature, item=self.__code, public_key=self.__from), \
            "Invalid Signature"

        contract = CompileContract(code)
        self.__state = contract.jsonify()

        self.__cxid = hashlib.sha256(f"{self.__from}{self.__code}{self.__time}".encode()).hexdigest()

    @property
    def cxid(self):
        return self.__cxid

    def jsonify(self):
        return {
            "cxid": self.__cxid,
            "from": self.__from,
            "time": self.__time,
            "code": self.__code,
            "state": {
                "state_vars": self.__state["state_vars"],
                "emits": self.__state["emits"]
            }
        }


class Message:
    """
    Call a contract
    """

    def __init__(self, t_from, t_to, signature, data, gas):
        self.__from = str(t_from)
        self.__to = str(t_to),
        self.__signature = str(signature)
        self.__data = data,
        self.__gas = int(gas),
        self.__time = time.time()

        assert verify_signature(signature=signature, item=str(data), public_key=t_from), \
            "Invalid Signature"

        self.__mxid = hashlib.sha256(f"{self.__from}{self.__to}{self.__time}{self.__data}".encode()).hexdigest()

    @property
    def mxid(self):
        return self.__mxid

    def jsonify(self):
        return {
            "from": self.__from,
            "to": self.__to,
            "time": self.__time,
            "gas": self.__gas,
            "data": {
                "args": self.__data,
                "reply": None
            }
        }
