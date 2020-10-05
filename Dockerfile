FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y handbrake-cli python3 python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -ms /bin/bash app && \
    mkdir /encode_in && \
    mkdir /encode_out && \
    chown app /encode_in /encode_out

USER app

COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

COPY wrapper.py /wrapper.py

COPY profiles /profiles

ENTRYPOINT ["./wrapper.py"]
