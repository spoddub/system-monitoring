import json
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(random.uniform(0.05, 0.3))
        if random.random() < 0.03:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"internal error")
            return

        payload = {
            "cpu": random.randint(0, 100),
            "mem": f"{random.randint(0, 100)}%",
            "disk": f"{random.randint(0, 100)}%",
            "uptime": "1d 2h 37m 6s",
        }
        body = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run():
    server = HTTPServer(("127.0.0.1", 9001), Handler)
    print("Mock listening on http://127.0.0.1:9001/")
    server.serve_forever()


if __name__ == "__main__":
    run()
