FROM python:3.12

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg sudo

RUN groupadd --gid 2000 appuser && \
    useradd --uid 2000 --gid appuser --shell /bin/bash --create-home appuser

COPY whisperx_rest /home/appuser/whisperx_rest
COPY gunicorn.conf.py /home/appuser/gunicorn.conf.py

RUN chown -R appuser /home/appuser/whisperx_rest/static

RUN echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER appuser
WORKDIR /home/appuser

RUN pip install --no-cache-dir flask gunicorn flask_swagger_ui
RUN pip install --no-cache-dir --default-timeout=120 whisperx
ENV LD_LIBRARY_PATH=/home/appuser/.local/lib/python3.12/site-packages/nvidia/cudnn/lib
ENV PATH=/home/appuser/.local/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin

RUN python whisperx_rest/configure.py

EXPOSE 5001

ENTRYPOINT [".local/bin/gunicorn", "whisperx_rest.app:app"]
