FROM continuumio/miniconda3

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg git

RUN conda create -n whisperx-env python=3.10 
RUN conda update -n base conda

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "whisperx-env", "/bin/bash", "-c"]

RUN conda install -y pytorch==2.0.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c nvidia -c pytorch
RUN pip install flask gunicorn flask_swagger_ui
RUN pip install git+https://github.com/m-bain/whisperx.git whisperx

WORKDIR /root/

COPY whisperx_rest /root/whisperx_rest
COPY gunicorn.conf.py /root/gunicorn.conf.py

RUN python whisperx_rest/configure.py

EXPOSE 5001

ENTRYPOINT ["conda", "run", "-n", "whisperx-env", "gunicorn", "whisperx_rest.app:app"]