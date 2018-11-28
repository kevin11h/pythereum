import pythereum
from pythereum.api.bottle import request, get, post, run

pth = pythereum.pythereum.Pythereum(difficulty=0)


@get('/create_wallet')
def create_wallet():
    seeds = request.query.decode().get("seeds", None)
    if not seeds:
        seeds = seeds.split(",")
    return pythereum.wallet.generate_wallet(*seeds)


@get('/get_difficulty')
def get_difficulty():
    return {"difficulty": pth.difficulty}


@get('/get_blocks')
def get_blocks():
    return {"blocks": pth.blocks}


@get('/get_block')
def get_block():
    block_hash = request.query.get("block_id")
    if block_hash:
        return {"block": pth[block_hash]}
    return {"block": None}


@get('/get_balance')
@get('/get_balance/<public_key>')
def get_balance(public_key=None):
    if not public_key:
        public_key = request.query.get("public_key")
    if public_key:
        return {"public_key": public_key, "balance": pth.get_balance(public_key)}
    return {"public_key": public_key, "balance": None}


@post('/mine')
@post('/mine_block')
def mine():
    return pth.mine_block()


@post('/create_transaction')
def transaction():
    try:
        t_from = request.POST.get("from")
        t_to = request.POST.get("to")
        amount = int(request.POST.get("amount"))
        private_key = request.POST.get("private_key")

        if not t_from or not t_to or not amount or not private_key:
            raise ValueError

        tx = pth.send_pth(t_from, t_to, amount, private_key)
        return {"transaction": tx}
    except ValueError:
        return {"transaction": None}


@post('/create_contract')
def create_contract():
    try:
        code = request.POST.get("code")
        public_key = request.POST.get("public_key")
        private_key = request.POST.get("private_key")

        if not code or not public_key or not private_key:
            raise ValueError

        cx = pth.create_contract(code, public_key, private_key)
        return {"contract": cx}
    except ValueError:
        return {"contract": None}


@get('/mempool')
@get('/mempool/<mem_type>')
def mempool(mem_type=None):
    if not mem_type:
        return {"transactions": pth.get_mempool("transactions"),
                "contracts": pth.get_mempool("contracts"),
                "messages": pth.get_mempool("messages")}
    if mem_type not in ["transactions", "contracts", "messages"]:
        return None
    return {mem_type: pth.get_mempool(mem_type)}


@post('/validate')
def validate():
    pass


def start_server():
    run(host='localhost', port=8080)
