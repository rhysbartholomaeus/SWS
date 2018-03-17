from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer




class Handler(BaseHTTPRequestHandler):
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>Hello World</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()
        self.wfile.write("This is a custom response")


def run(server_class=HTTPServer, handler_class=Handler, port=6969):
    server_address = ('',port)
    httpd = server_class(server_address, handler_class)
    print("== Init server ==")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
    
