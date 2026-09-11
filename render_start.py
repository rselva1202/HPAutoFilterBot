import os
import signal
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


PORT = int(os.environ.get("PORT", "10000"))


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                b'{"status":"ok","service":"AutoFilterPro"}'
            )
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"AutoFilterPro is running.")

    def log_message(self, format, *args):
        return


def start_health_server():
    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )

    print(f"🌐 Health server listening on port {PORT}")

    server.serve_forever()


def main():
    print("🚀 Starting AutoFilterPro...")

    health_thread = threading.Thread(
        target=start_health_server,
        daemon=True
    )
    health_thread.start()

    bot_process = subprocess.Popen(
        [sys.executable, "bot.py"]
    )

    print(
        f"🤖 AutoFilterPro started "
        f"(PID: {bot_process.pid})"
    )

    def shutdown_handler(signum, frame):
        print("🛑 Shutting down AutoFilterPro...")

        if bot_process.poll() is None:
            bot_process.terminate()

            try:
                bot_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                bot_process.kill()

        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    exit_code = bot_process.wait()

    print(
        f"⚠️ AutoFilterPro stopped "
        f"with exit code {exit_code}"
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()