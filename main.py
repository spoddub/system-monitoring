import json
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlsplit


def as_int(qs, name, default):
    try:
        if name in qs:
            return int(qs[name][0])
    except Exception:
        pass
    return default


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlsplit(self.path).query)

        cpu = as_int(qs, "cpu", random.randint(10, 80))
        mem = as_int(qs, "mem", random.randint(10, 70))
        disk = as_int(qs, "disk", random.randint(10, 70))

        payload = {
            "cpu": cpu,
            "mem": f"{mem}%",
            "disk": f"{disk}%",
            "uptime": "1d 2h 37m 6s",
        }
        body = (json.dumps(payload) + "\n").encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    host, port = "127.0.0.1", 9001
    print(f"Mock listening on http://{host}:{port}/")
    HTTPServer((host, port), Handler).serve_forever()
