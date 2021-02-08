FROM ubuntu:20.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y handbrake-cli \
                                                      python3 \
                                                      python3-pip \
                                                      mediainfo \
                                                      && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -ms /bin/bash app && \
    mkdir /encode_in && \
    mkdir /encode_out && \
    mkdir /output && \
    chown app /encode_in /encode_out /output

USER app

COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
