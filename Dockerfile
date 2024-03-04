FROM continuumio/miniconda3

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg git

RUN groupadd --gid 2000 appuser && \
    useradd --uid 2000 --gid appuser --shell /bin/bash --create-home appuser

COPY whisperx_rest /home/appuser/whisperx_rest
COPY gunicorn.conf.py /home/appuser/gunicorn.conf.py

RUN chown -R appuser /home/appuser/whisperx_rest/static

USER appuser
WORKDIR /home/appuser

RUN conda create -n whisperx-env python=3.10 
RUN conda update -n base conda

SHELL ["conda", "run", "-n", "whisperx-env", "/bin/bash", "-c"]

RUN conda install -y python=3.10 pytorch=2.0.0 torchaudio=2.0.0 \
    pytorch-cuda=11.8 -c nvidia -c pytorch
RUN pip install flask gunicorn flask_swagger_ui
RUN pip install git+https://github.com/m-bain/whisperx.git whisperx

RUN python whisperx_rest/configure.py

EXPOSE 5001

ENTRYPOINT ["conda", "run", "-n", "whisperx-env", "gunicorn", "whisperx_rest.app:app"]