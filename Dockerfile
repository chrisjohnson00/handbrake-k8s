FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y handbrake-cli && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -ms /bin/bash app && \
    mkdir /encode_in && \
    mkdir /encode_out && \
    chown app /encode_in /encode_out

USER app

COPY wrapper.sh /wrapper.sh

ENTRYPOINT ["./wrapper.sh"]
