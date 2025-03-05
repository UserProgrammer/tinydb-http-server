import json
from tinydb import TinyDB, Query
from http.server import BaseHTTPRequestHandler, HTTPServer
from functools import cached_property
from urllib.parse import parse_qsl, urlparse
from http.cookies import SimpleCookie

db = TinyDB('tinydb.json')


def insert(record: object):
    db.insert(record)


def get_all():
    return db.all()


def clear():
    db.truncate()


class WebRequestHandler(BaseHTTPRequestHandler):
    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query_data(self):
        return dict(parse_qsl(self.url.query))

    @cached_property
    def post_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(content_length)

    @cached_property
    def form_data(self):
        return dict(parse_qsl(self.post_data.decode("utf-8")))

    @cached_property
    def cookies(self):
        return SimpleCookie(self.headers.get("Cookie"))

    def generate_200_response(self, responseBody: object):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(responseBody).encode("utf-8"))

    def generate_201_response(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        match self.url.path:
            case "/status":
                self.generate_200_response({"status": "OK"})
            case "/get-all":
                self.generate_200_response(get_all())
            case _:
                self.generate_200_response({"message": "Request made with GET method"})

    def do_POST(self):
        match self.url.path:
            case "/insert":
                payload = self.post_data.decode("utf_8")
                insert(json.loads(payload))
                self.generate_201_response()
            case _:
                self.generate_200_response({"message": "Request made with POST method"})

    def do_PUT(self):
        match self.url.path:
            case "/clear":
                clear()
                self.generate_201_response()
            case _:
                self.generate_200_response({"message": "Request made with PUT method"})


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    server.serve_forever()
