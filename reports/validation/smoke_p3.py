import json, sys, urllib.request, urllib.error
BASE = sys.argv[1]
AUTH = {}
def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=dict({"Content-Type": "application/json"}, **AUTH))
    try:
        r = urllib.request.urlopen(req, timeout=10); status, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    try: js = json.loads(raw)
    except Exception: js = None
    if isinstance(js, dict): shape = sorted(js.keys())
    elif isinstance(js, list): shape = "list[%d] %s" % (len(js), sorted(js[0].keys()) if js and isinstance(js[0], dict) else "")
    else: shape = "nojson"
    print(f"{method:6} {path:28} -> {status} {shape}")
    return js
call("GET", "/"); call("GET", "/health")
call("GET", "/tasks"); call("GET", "/tasks/1"); call("GET", "/tasks/9999")
call("GET", "/tasks/search?q=bug&status=pending"); call("GET", "/tasks/stats")
t = call("POST", "/tasks", {"title": "Nova task", "description": "d", "priority": 2, "user_id": 1, "category_id": 1, "due_date": "2030-01-01", "tags": ["a", "b"]})
tid = t["id"]
call("POST", "/tasks", {"title": "x"}); call("POST", "/tasks", {"title": "Titulo ok", "status": "invalido"})
call("PUT", f"/tasks/{tid}", {"title": "Task editada", "status": "in_progress", "priority": 1})
call("DELETE", f"/tasks/{tid}")
call("GET", "/users"); call("GET", "/users/1"); call("GET", "/users/9999")
u = call("POST", "/users", {"name": "Novo", "email": "novo@x.com", "password": "abcd"}); uid = u["id"]
call("POST", "/users", {"name": "Novo"}); call("POST", "/users", {"name": "Dup", "email": "novo@x.com", "password": "abcd"})
call("PUT", f"/users/{uid}", {"name": "Novo Editado"})
call("GET", "/users/1/tasks")
lg = call("POST", "/login", {"email": "joao@email.com", "password": "1234"}); AUTH["Authorization"] = "Bearer " + lg["token"]; call("POST", "/login", {"email": "joao@email.com", "password": "x"})
call("POST", "/login", {"email": "novo@x.com", "password": "abcd"})
call("DELETE", f"/users/{uid}")
call("GET", "/reports/summary"); call("GET", "/reports/user/1"); call("GET", "/reports/user/9999")
call("GET", "/categories")
c = call("POST", "/categories", {"name": "Cat Nova", "description": "d", "color": "#123456"}); cid = c["id"]
call("PUT", f"/categories/{cid}", {"name": "Cat Editada"}); call("DELETE", f"/categories/{cid}")
call("GET", "/nao-existe")
