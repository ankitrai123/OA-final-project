"""
Service Line — local server.

Runs the dashboard AND relays AI requests, so providers that block direct
browser calls (NVIDIA NIM, and sometimes others) work normally.

    python serve.py

Then open http://localhost:8000

Your API key passes through this process to the provider and is never
written to disk or logged.
"""

import json
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"  # listen on every interface so other machines on the intranet can reach it
PORT = 8000


def lan_ip():
    """Best-effort guess at this machine's LAN address, for printing a shareable URL."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # no packet actually sent; just picks the outbound interface
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()

ALLOWED_HOSTS = {
    "api.anthropic.com",
    "api.openai.com",
    "integrate.api.nvidia.com",
    "generativelanguage.googleapis.com",
    "openrouter.ai",
}


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api":
            self.send_error(404)
            return

        try:
            size = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(size))
            url = payload["url"]
            host = urllib.parse.urlparse(url).hostname or ""

            if host not in ALLOWED_HOSTS:
                self._json(403, {"error": {"message": "Host not allowed: " + host}})
                return

            req = urllib.request.Request(
                url,
                data=json.dumps(payload.get("body", {})).encode(),
                headers=payload.get("headers", {}),
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                self._raw(r.status, r.read())

        except urllib.error.HTTPError as e:
            self._raw(e.code, e.read())
        except Exception as e:
            self._json(502, {"error": {"message": str(e)}})

    def _raw(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._raw(code, json.dumps(obj).encode())

    def log_message(self, fmt, *args):
        msg = fmt % args
        if "/api" in msg:
            return  # never log AI traffic
        sys.stderr.write("%s\n" % msg)


if __name__ == "__main__":
    print("Service Line running at:")
    print("  http://localhost:%d          (this machine)" % PORT)
    ip = lan_ip()
    if ip:
        print("  http://%s:%d   (share this on your intranet)" % (ip, PORT))
    print("AI relay active for Anthropic, OpenAI, NVIDIA, Gemini, OpenRouter.")
    print("Press Ctrl+C to stop.\n")
    try:
        ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
