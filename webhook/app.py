
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        alert_data = json.loads(data)

        for alert in alert_data.get("alerts", []):
            alert_name = alert.get("labels", {}).get("alertname")
            status = alert.get("status")

            print(f"Alert received: {alert_name}")
            print(f"Status: {status}")

            if alert_name == "NginxDown" and status == "firing":
                print("Starting Ansible recovery...")

                result = subprocess.run(
                    [
                        "ansible-playbook",
                        "/ansible/restart-nginx.yml"
                    ],
                    capture_output=True,
                    text=True
                )

                print(result.stdout)

                if result.returncode != 0:
                    print("Ansible recovery failed:")
                    print(result.stderr)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Alert processed")

server = HTTPServer(("0.0.0.0", 5001), WebhookHandler)

print("Webhook server running on port 5001...")
server.serve_forever()
