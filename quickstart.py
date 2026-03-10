#!/usr/bin/env python3

import os
import subprocess
import sys


def main() -> int:
    compose_cmd = [
        "docker",
        "compose",
        "--env-file",
        ".env",
        "-f",
        "docker/docker-compose.yml",
        "up",
    ]

    if os.name == "nt":  #windows
        cmd = compose_cmd
    else:
        cmd = ["sudo", *compose_cmd]

    return subprocess.run(cmd, cwd=".").returncode


if __name__ == "__main__":
    sys.exit(main())
