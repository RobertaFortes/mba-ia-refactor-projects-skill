import json, sys, urllib.request, urllib.error
BASE = sys.argv[1]
def call(method, path, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"}; h.update(headers or {})
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=h)
    try:
        r = urllib.request.urlopen(req, timeout=10); status, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    txt = raw.decode()
    try:
        js = json.loads(txt)
        shape = sorted(js.keys()) if isinstance(js, dict) else ("list[%d] %s" % (len(js), sorted(js[0].keys()) if js and isinstance(js[0], dict) else ""))
    except Exception:
        shape = "text: " + txt[:60]
    print(f"{method:6} {path:30} -> {status} {shape}")
    return txt
TOKEN = {"X-Admin-Token": sys.argv[2]} if len(sys.argv) > 2 else {}
call("POST", "/api/checkout", {"usr": "Guilherme", "eml": "gui@fullcycle.com.br", "pwd": "senhaforte", "c_id": 2, "card": "4111222233334444"})
call("POST", "/api/checkout", {"usr": "Joao", "eml": "joao@teste.com", "pwd": "123", "c_id": 1, "card": "5111222233334444"})
call("POST", "/api/checkout", {"usr": "Leonan", "eml": "leonan@fullcycle.com.br", "c_id": 2, "card": "4999"})
call("POST", "/api/checkout", {"usr": "X"})
call("POST", "/api/checkout", {"usr": "X", "eml": "x@x.com", "c_id": 999, "card": "4111"})
r = call("GET", "/api/admin/financial-report", headers=TOKEN)
print("   report:", r[:400])
call("DELETE", "/api/users/1", headers=TOKEN)
print("   report apos delete:", call("GET", "/api/admin/financial-report", headers=TOKEN)[:300])
