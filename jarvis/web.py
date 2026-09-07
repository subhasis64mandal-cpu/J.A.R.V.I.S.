"""Small local web interface for talking to J.A.R.V.I.S."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import urlparse

from .core import Jarvis


assistant = Jarvis()


HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>J.A.R.V.I.S.</title>
<style>
:root { color-scheme: dark; font-family: Inter, system-ui, sans-serif; }
body { margin:0; min-height:100vh; background:#07090d; color:#f4f7fb; display:grid; place-items:center; }
.app { width:min(900px,92vw); height:min(760px,90vh); display:flex; flex-direction:column; border:1px solid #202631; border-radius:24px; background:#0d1118; box-shadow:0 24px 80px #0008; overflow:hidden; }
header { padding:22px 26px; border-bottom:1px solid #202631; display:flex; justify-content:space-between; align-items:center; }
.brand { font-weight:800; letter-spacing:.12em; } .status { font-size:13px; color:#7ee787; }
#chat { flex:1; overflow:auto; padding:28px; display:flex; flex-direction:column; gap:14px; }
.msg { max-width:75%; padding:13px 16px; border-radius:16px; line-height:1.45; white-space:pre-wrap; }
.user { align-self:flex-end; background:#243044; } .jarvis { align-self:flex-start; background:#151b24; }
form { display:flex; gap:10px; padding:18px; border-top:1px solid #202631; } input { flex:1; padding:15px 16px; border:1px solid #2b3442; border-radius:14px; background:#080b10; color:inherit; outline:none; } button { padding:0 20px; border:0; border-radius:14px; background:#f4f7fb; color:#080b10; font-weight:700; cursor:pointer; }
</style>
</head>
<body><main class="app">
<header><div class="brand">J.A.R.V.I.S.</div><div class="status">● ONLINE</div></header>
<section id="chat"><div class="msg jarvis">J.A.R.V.I.S. online. How can I help?</div></section>
<form id="form"><input id="input" autocomplete="off" placeholder="Talk to JARVIS..." autofocus><button>Send</button></form>
</main>
<script>
const chat=document.querySelector('#chat'), input=document.querySelector('#input'), form=document.querySelector('#form');
function add(text,who){const d=document.createElement('div');d.className='msg '+who;d.textContent=text;chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
form.addEventListener('submit',async e=>{e.preventDefault();const message=input.value.trim();if(!message)return;add(message,'user');input.value='';try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message})});const data=await r.json();add(data.response,'jarvis')}catch(err){add('Connection error. JARVIS is still starting up.','jarvis')}});
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if urlparse(self.path).path != "/":
            self.send_error(404)
            return
        data = HTML.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if urlparse(self.path).path != "/api/chat":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            message = str(payload.get("message", ""))
            self.send_json({"response": assistant.respond(message)})
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "Invalid request"}, 400)

    def log_message(self, *_args):
        return


def run(host="127.0.0.1", port=8765):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"J.A.R.V.I.S. interface running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
