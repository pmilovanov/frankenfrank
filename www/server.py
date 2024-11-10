import http.server
import os
import socketserver

class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = super().translate_path(path)
        # Resolve any symlinks in the path
        return os.path.realpath(path)

PORT = 8000
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
