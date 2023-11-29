#!flask/bin/python

import os
from flask import Flask, request
from tempfile import mktemp, gettempdir
import subprocess


app = Flask(__name__)


@app.route("/whisperx", methods=["POST"])
def transcribe_file():
    params = []
    audio_file = None
    filename = mktemp()
    if "file" in request.files:
        request.files["file"].save(filename)
    else:
        audio_file = request.get_data()
        with open(filename, "wb") as f:
            f.write(audio_file)

    if "output_format" in request.args.keys():
        output_format = request.args.get("output_format")
    else:
        output_format = "json"

    params = [f"--{p} {v}" for p, v in request.args.items()]
    params += [f"--output_dir {gettempdir()}"]

    # TODO add parameters check to avoid shell injection
    subprocess.call(
        "conda run -n whisperx-env whisperx " + " ".join([filename] + params),
        shell=True,
        stderr=subprocess.STDOUT,
    )

    os.unlink(filename)

    # TODO return error output
    try:
        with open(f"{filename}.{output_format}", "r") as f:
            result = f.read()
            os.unlink(f"{filename}.{output_format}")
    except FileNotFoundError:
        return

    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
