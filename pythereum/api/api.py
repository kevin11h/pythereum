import ast
import json

import pythereum
from pythereum.api.bottle import request, response, get, post, run, error

pth = pythereum.pythereum.Pythereum(difficulty=0)


@get('/create_wallet')
def create_wallet():
    seeds = request.query.decode().get("seeds", None)
    if not seeds:
        seeds = request.query.decode().get("seed", None)
    if seeds:
        seeds = seeds.split(",")
        return pythereum.wallet.generate_wallet(*seeds)
    return {"status_code": 200, "wallet": pythereum.wallet.generate_wallet()}


@get('/get_difficulty')
def get_difficulty():
    return {"status_code": 200, "difficulty": pth.difficulty}


@get('/get_blocks')
def get_blocks():
    return {"status_code": 200, "blocks": pth.blocks}


@get('/get_block')
@get('/get_block/<block_id>')
def get_block(block_id=None):
    if not block_id:
        block_id = request.query.get("block_id")
    if block_id:
        return {"status_code": 200, "block": pth[block_id]}
    response.status = 400
    return {"status_code": 400, "block": None, "message": "Not block_id/hash passed"}


@get('/get_balance')
def get_balance():
    public_key = request.query.get("public_key")
    if public_key:
        return {"status_code": 200, "public_key": public_key, "balance": pth.get_balance(public_key)}
    response.status = 400
    return {"status_code": 400, "public_key": public_key, "balance": None, "message": "No public_key "
                                                                                      "passed with request"}


@post('/mine')
@post('/mine_block')
def mine():
    blk = pth.mine_block()
    if blk:
        return {"status_code": 200, "block": blk}
    response.status = 400
    return {"status_code": 400, "block": None, "message": "Mempool empty. Nothing to mine."}


@post('/create_transaction')
def transaction():
    try:
        t_from = request.POST.get("from")
        t_to = request.POST.get("to")
        amount = request.POST.get("amount")
        private_key = request.POST.get("private_key")
        data = request.POST.get("data")

        if not t_from or not t_to or not amount or not private_key:
            if private_key:
                raise ValueError(f"Empty parameter. from: {t_from}, to: {t_to}, amount: {amount}")
            raise ValueError("Empty parameter. Did not receive private key")

        try:
            amount = float(amount)
        except TypeError:
            raise TypeError("Invalid amount. Expected float")

        tx = pth.send_pth(t_from, t_to, amount, private_key, data=data)
        return {"status_code": 200, "transaction": tx}
    except Exception as tx:
        response.status = 400
        return {"status_code": 400, "transaction": None, "message": str(tx)}


@post('/create_contract')
def create_contract():
    try:
        code = request.POST.get("code")
        public_key = request.POST.get("public_key")
        private_key = request.POST.get("private_key")

        if not code or not public_key or not private_key:
            if not code:
                raise ValueError("No code received")
            elif private_key:
                raise ValueError("No public_key received")
            raise ValueError("No private_key received")

        cx = pth.create_contract(code, public_key, private_key)
        return {"status_code": 200, "contract": cx}
    except Exception as e:
        response.status = 400
        return {"status_code": 400, "contract": None, "message": str(e)}


@post('/call_contract')
def call_contract():
    try:
        cxid = request.POST.get("contract_id")
        gas = request.POST.get("gas")
        data = request.POST.get("data")
        public_key = request.POST.get("public_key")
        private_key = request.POST.get("private_key")

        if not cxid or not gas or not public_key or not private_key:
            if private_key:
                raise ValueError(f"Empty parameter. contract_id: {cxid}, gas: {gas}, data: {data}, "
                                 f"public_key: {public_key}")
            raise ValueError(f"Empty parameter. Private key not sent")
        try:
            gas = int(gas)
        except ValueError:
            raise ValueError("Malformed gas value. Must be a valid integer")
        try:
            data = '[' + data + ']'
            data = ast.literal_eval(data)
        except ValueError:
            raise ValueError("Malformed call arguments. Function arguments should be comma separated")
        mx = pth.call_contract(cxid, gas, data, public_key, private_key)
        return {"status_code": 200, "contract_reply": mx}
    except (ValueError, LookupError, AssertionError) as v:
        response.status = 400
        return {"status_code": 400, "contract_reply": None, "message": str(v)}
    except Exception as e:
        response.status = 500
        return {"status_code": 500, "contract_reply": None, "message": "Error running contract. Issues may exist inside"
                                                                       f"contract. ERROR: {str(e)}"}


@get('/mempool')
@get('/mempool/<mem_type>')
def mempool(mem_type=None):
    if not mem_type:
        return {"status_code": 200,
                "transactions": pth.get_mempool("transactions"),
                "contracts": pth.get_mempool("contracts"),
                "messages": pth.get_mempool("messages")}
    if mem_type not in ["transactions", "contracts", "messages"]:
        response.status = 404
        return {"status_code": 404, "message": "Invalid mempool. Type not found"}
    return {"status_code": 200, mem_type: pth.get_mempool(mem_type)}


@post('/validate')
def validate():
    return {"status_code": 200, **pth.verify_chain()}


@error(404)
def page_not_found(error):
    response.content_type = "application/json"
    return json.dumps({"status_code": 404, "message": "URI not found"})


@error(500)
def internal_error(error):
    response.content_type = "application/json"
    return json.dumps({"status_code": 500, "message": "Internal Server error"})


def start_api(port=8080, debug=False):
    run(host='localhost', port=port, debug=debug)
