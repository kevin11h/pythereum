import hashlib

from pythereum.wallet import verify_signature


class Transaction:
    def __init__(self, t_from, t_to, value, signature, input_txids, change_address=None):
        self.__from = t_from
        self.__to = t_to
        self.__amount = value
        self.__signature = signature

        assert verify_signature(signature=self.__signature, item=f"{value}{t_from}", public_key=self.__from)

        self.__change_address = change_address or t_from

        if isinstance(input_txids, list):
            self.__input_txids = [*input_txids]
        elif isinstance(input_txids, str):
            self.__input_txids = [input_txids]
        else:
            self.__input_txids = []

        self.__is_ready = False

        self.__txid = None

    def add_input_txid(self, txid):
        if not self.is_ready:
            self.__input_txids.append(txid)

    @property
    def txid(self):
        return self.__txid

    @property
    def input_txids(self):
        return self.__input_txids

    @property
    def is_ready(self):
        return self.__is_ready

    def make_ready(self):
        self.__txid = hashlib.sha256(f"{self.__from}{self.__to}{self.__amount}{''.join(self.__input_txids)}".encode()
                                     ).hexdigest()
        self.__is_ready = True

    def jsonify(self):
        if not self.is_ready:
            return None
        return {
            "from": self.__from,
            "to": self.__to,
            "signature": self.__signature,
            "amount": self.__amount,
            "txid": self.txid,
            "input_txids": self.input_txids
        }
