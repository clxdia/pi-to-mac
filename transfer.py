import os
import re
import subprocess
import time

from config import DESTINATION


class FileTransfer:

    def __init__(self, on_progress=None):
        self.on_progress = on_progress

    def send_files(self, files):
        success = []
        failed = []

        for file_path in files:

            filename = os.path.basename(file_path)

            try:
                self.send_file(file_path)
                success.append(filename)

            except Exception as error:
                print(
                    f"Failed to send {filename}: {error}"
                )
                failed.append(filename)

        return success, failed

    def send_file(self, file_path):

        process = subprocess.Popen(
            [
                "scp",
                "-v",
                file_path,
                DESTINATION
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        start_time = time.time()

        while True:

            char = process.stderr.read(1)

            if not char:
                break

            if char == "\r":

                line = process.stderr.readline()

                self.parse_progress(
                    line,
                    start_time
                )

        return_code = process.wait()

        if return_code != 0:
            raise subprocess.CalledProcessError(
                return_code,
                process.args
            )

    def parse_progress(self, line, start_time):

        match = re.search(
            r"(\d+)%.*?([\d.]+\s*[KMG]?B/s)\s+(\d+:\d+:\d+)",
            line
        )

        if not match:
            return

        percentage = int(match.group(1))
        speed = match.group(2)
        eta = match.group(3)

        if self.on_progress:
            self.on_progress(
                percentage,
                speed,
                eta
            )