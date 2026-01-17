"""Local web server for Plaid Link authentication flow."""

import http.server
import json
import socketserver
import threading
import webbrowser
from urllib.parse import parse_qs, urlparse

from finances.plaid_service import create_link_token


# Will be set by the callback handler
_result = {"public_token": None, "error": None, "done": False}
_server = None


def get_link_html(link_token: str) -> str:
    """Generate the HTML page for Plaid Link."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Connect Your Bank</title>
    <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f5f5f5;
        }}
        .container {{
            text-align: center;
            padding: 40px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        p {{ color: #666; margin-bottom: 30px; }}
        #status {{ margin-top: 20px; color: #666; }}
        .success {{ color: #22c55e !important; }}
        .error {{ color: #ef4444 !important; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Connect Your Bank</h1>
        <p>Click the button below to securely link your bank account.</p>
        <button id="link-button" style="
            background: #0066ff;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 6px;
            cursor: pointer;
        ">Connect Bank Account</button>
        <p id="status"></p>
    </div>

    <script>
        const handler = Plaid.create({{
            token: '{link_token}',
            onSuccess: async (public_token, metadata) => {{
                document.getElementById('status').textContent = 'Connecting...';

                const response = await fetch('/callback', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        public_token: public_token,
                        institution: metadata.institution,
                        accounts: metadata.accounts
                    }})
                }});

                if (response.ok) {{
                    document.getElementById('status').textContent = 'Success! You can close this window.';
                    document.getElementById('status').className = 'success';
                    document.getElementById('link-button').style.display = 'none';
                }} else {{
                    document.getElementById('status').textContent = 'Error connecting account.';
                    document.getElementById('status').className = 'error';
                }}
            }},
            onExit: (err, metadata) => {{
                if (err != null) {{
                    document.getElementById('status').textContent = 'Error: ' + err.display_message;
                    document.getElementById('status').className = 'error';
                }}
            }},
        }});

        document.getElementById('link-button').addEventListener('click', () => {{
            handler.open();
        }});
    </script>
</body>
</html>"""


class LinkHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for Plaid Link flow."""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Serve the Plaid Link page."""
        if self.path == "/" or self.path.startswith("/?"):
            link_token = create_link_token()
            html = get_link_html(link_token)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle the callback from Plaid Link."""
        global _result

        if self.path == "/callback":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode())
                _result["public_token"] = data.get("public_token")
                _result["metadata"] = {
                    "institution": data.get("institution"),
                    "accounts": data.get("accounts"),
                }
                _result["done"] = True

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())

            except Exception as e:
                _result["error"] = str(e)
                _result["done"] = True

                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


def run_link_flow(port: int = 8765) -> dict | None:
    """
    Run the Plaid Link flow.

    Opens a browser to complete bank authentication, waits for the callback.

    Args:
        port: Local port to run the server on

    Returns:
        Dict with public_token and metadata, or None if cancelled/failed
    """
    global _result, _server
    _result = {"public_token": None, "error": None, "done": False}

    # Start server
    _server = socketserver.TCPServer(("", port), LinkHandler)
    _server.allow_reuse_address = True

    server_thread = threading.Thread(target=_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Open browser
    url = f"http://localhost:{port}"
    webbrowser.open(url)

    print(f"Opened browser to {url}")
    print("Complete the bank connection in your browser...")
    print("(Press Ctrl+C to cancel)\n")

    # Wait for callback
    try:
        while not _result["done"]:
            pass
    except KeyboardInterrupt:
        print("\nCancelled.")
        return None
    finally:
        _server.shutdown()

    if _result["error"]:
        print(f"Error: {_result['error']}")
        return None

    return {
        "public_token": _result["public_token"],
        "metadata": _result.get("metadata", {}),
    }
