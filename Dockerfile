FROM continuumio/miniconda3

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update && apt-get upgrade && \
    apt-get install -y --no-install-recommends ffmpeg git

RUN conda create -n whisperx-env python=3.10 
RUN conda update -n base conda

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "whisperx-env", "/bin/bash", "-c"]

RUN conda install -y pytorch==2.0.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c nvidia -c pytorch
RUN pip install flask gunicorn
RUN pip install git+https://github.com/m-bain/whisperx.git whisperx

WORKDIR /root/

COPY . .

EXPOSE 5000

ENTRYPOINT ["conda", "run", "-n", "whisperx-env", "gunicorn", \
    "-b", "0.0.0.0:5000", "--timeout", "1800", \
    "--error-logfile", "gunicorn_error.log", "whisperx-rest.app:app"]