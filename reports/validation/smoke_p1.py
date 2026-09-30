import json, sys, urllib.request, urllib.error
BASE = sys.argv[1]
def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=10); status, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    try: js = json.loads(raw)
    except Exception: js = None
    keys = sorted(js.keys()) if isinstance(js, dict) else ("list" if isinstance(js, list) else "nojson")
    inner = ""
    if isinstance(js, dict) and isinstance(js.get("dados"), dict): inner = sorted(js["dados"].keys())
    if isinstance(js, dict) and isinstance(js.get("dados"), list) and js["dados"] and isinstance(js["dados"][0], dict): inner = ["[]"] + sorted(js["dados"][0].keys())
    print(f"{method:6} {path:32} -> {status} {keys} {inner}")
    return js
P = {"nome": "Produto Teste", "descricao": "d", "preco": 10.5, "estoque": 5, "categoria": "geral"}
call("GET", "/"); call("GET", "/health")
call("GET", "/produtos"); call("GET", "/produtos/1"); call("GET", "/produtos/9999")
call("GET", "/produtos/busca?q=note&preco_max=9000")
r = call("POST", "/produtos", P); pid = r["dados"]["id"]
call("POST", "/produtos", {"nome": "x"})
call("PUT", f"/produtos/{pid}", dict(P, preco=12)); call("DELETE", f"/produtos/{pid}")
call("GET", "/usuarios"); call("GET", "/usuarios/1"); call("GET", "/usuarios/9999")
call("POST", "/usuarios", {"nome": "Novo", "email": "novo@x.com", "senha": "abc123"}); call("POST", "/usuarios", {"nome": "Novo"})
call("POST", "/login", {"email": "joao@email.com", "senha": "123456"}); call("POST", "/login", {"email": "joao@email.com", "senha": "errada"})
call("POST", "/login", {"email": "novo@x.com", "senha": "abc123"})
call("POST", "/pedidos", {"usuario_id": 2, "itens": [{"produto_id": 1, "quantidade": 1}, {"produto_id": 2, "quantidade": 2}]})
call("POST", "/pedidos", {"usuario_id": 2, "itens": [{"produto_id": 1, "quantidade": 9999}]}); call("POST", "/pedidos", {"usuario_id": 2, "itens": []})
call("GET", "/pedidos"); call("GET", "/pedidos/usuario/2")
call("PUT", "/pedidos/1/status", {"status": "aprovado"}); call("PUT", "/pedidos/1/status", {"status": "xyz"})
call("GET", "/relatorios/vendas")
call("POST", "/admin/query", {"sql": "SELECT id, nome FROM produtos LIMIT 1"})
call("POST", "/admin/reset-db")
