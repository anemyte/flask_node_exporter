#!/usr/bin/env python3
from flask import Flask
import threading
import subprocess
import random
import requests
from time import sleep


# Write here path to your node_exporter binary
NODE_EXPORTER_BINARY_PATH = "./node_exporter"


class Exporter:

    def __init__(self):
        self.port = None
        self.process = None
        self.manger_thread = None
        self.manager_loop_condition = False

    def is_alive(self):
        """Check if node_exporter process is alive."""
        try:
            if self.process.poll() is None:
                return True
        except AttributeError:
            pass
        return False

    def start(self):
        # start node exporter
        if self.process is None:
            self.port = random.randint(30000, 65000)
            cmd = [NODE_EXPORTER_BINARY_PATH, f"--web.listen-address=127.0.0.1:{self.port}"]
            self.process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        else:
            print("Run Exporter.stop() first.")

    def restart(self):
        # restart node exporter
        self.stop()
        self.start()

    def stop(self):
        # stop node exporter
        if self.process is not None:
            self.process.terminate()
            self.process = None

    def healthcheck(self):
        """Check if exporter reply to requests. Returns http status code or just 1 in case of connection problem."""
        try:
            r = requests.get(url=f"http://127.0.0.1:{self.port}")
            return r.status_code
        except requests.exceptions.ConnectionError:
            return 1

    def manage(self):
        """Loop that keeps node_exporter up and running."""
        while self.manager_loop_condition:
            if self.process is None:
                self.start()
                sleep(1)
                continue

            if not self.is_alive():
                print("Manager: process is not alive - restarting.")
                self.restart()
                sleep(1)
                continue

            hc = self.healthcheck()
            if hc != 200:
                print(f"Manager: healthcheck failed, status code: {hc}")
                print(f"Manager: restarting")
                sleep(1)
                continue

            sleep(1)  # and continue

    def start_manager(self):
        """Start manager process that'll keep node_exporter up."""
        try:
            if self.manger_thread.is_alive():
                print("Manager thread is alive - shut down first")
                return
        except AttributeError:
            # Will be raised if manager_thread is None
            pass

        self.manager_loop_condition = True
        self.manger_thread = threading.Thread(target=self.manage)
        self.manger_thread.start()

    def stop_manager(self):
        """Stop manager thread."""
        print("Stopping manger...")
        self.manager_loop_condition = False
        self.manger_thread.join(2)


application = Flask(__name__)
exporter = Exporter()


@application.before_first_request
def init_manager():
    exporter.start_manager()
    # it needs just a couple of seconds to start
    for i in range(30):
        if exporter.healthcheck() != 200:
            sleep(0.1)
        else:
            break


@application.route("/", defaults={"path": ""})
@application.route("/<path:path>")
def proxy(path):
    return requests.get(f"http://127.0.0.1:{exporter.port}/{path}").content


if __name__ == '__main__':
    application.run("0.0.0.0")
