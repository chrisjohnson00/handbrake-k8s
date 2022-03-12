FROM ubuntu:20.04

ENV PYTHON_VERSION=3.8.12

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y handbrake-cli \
                                                      mediainfo \
                                                      curl \
                                                      gcc \
                                                      make \
                                                      zlib1g-dev \
                                                      libssl-dev \
                                                      libbz2-dev \
                                                      liblzma-dev \
                                                      libreadline-gplv2-dev \
                                                      libncursesw5-dev \
                                                      libsqlite3-dev \
                                                      tk-dev \
                                                      libgdbm-dev \
                                                      libc6-dev \
                                                      libbz2-dev \
                                                      libffi-dev \
                                                      && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -ms /bin/bash app && \
    mkdir /encode_in && \
    mkdir /encode_out && \
    mkdir /output && \
    chown app /encode_in /encode_out /output && \
    echo "Installing python ${PYTHON_VERSION} from source" && \
    curl --silent --location https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz | tar xz -C /tmp && \
    cd /tmp/Python-${PYTHON_VERSION} && \
    ./configure && \
    make && \
    make install && \
    rm -rf /tmp/Python-${PYTHON_VERSION}

USER app

RUN echo 'alias python=python3' >> ~/.bashrc

COPY requirements.txt /requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . .
