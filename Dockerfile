FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y handbrake-cli && \
    rm -rf /var/lib/apt/lists/*

CMD ["-h"]
ENTRYPOINT ["HandBrakeCLI"]
