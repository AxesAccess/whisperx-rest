#!flask/bin/python

"""Flask/gunicorn application entry point."""

import os
from tempfile import mktemp, gettempdir, TemporaryFile
import subprocess
from flask import Flask, request


app = Flask(__name__)


@app.route("/whisperx", methods=["POST"])
def transcribe_file():
    """Receives audio file and parameters in POST request
    and transcribes audio using whisperx.

    Returns:
        str: contents of whisperX output file
    """
    params = []
    audio_file = None
    filename = mktemp()
    if "file" in request.files:
        request.files["file"].save(filename)
    else:
        audio_file = request.get_data()
        with open(filename, "wb", encoding="utf-8") as f:
            f.write(audio_file)

    if "output_format" in request.args.keys():
        output_format = request.args.get("output_format")
    else:
        output_format = "json"

    params = [f"--{p} {v}" for p, v in request.args.items()]
    params += [f"--output_dir {gettempdir()}"]

    with TemporaryFile() as f:
        subprocess.call(
            "conda run -n whisperx-env whisperx " + " ".join([filename] + params),
            shell=True,
            stderr=f,
        )

        os.unlink(filename)

        try:
            with open(f"{filename}.{output_format}", "r", encoding="utf-8") as f:
                result = f.read()
                os.unlink(f"{filename}.{output_format}")
        except FileNotFoundError:
            f.seek(0)
            return f.read(), 500

    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
