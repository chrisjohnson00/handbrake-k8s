FROM ubuntu:24.04

# Set the locale
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y locales && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8

# install apps and dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y handbrake-cli \
                                                      mediainfo \
                                                      python3 \
                                                      pip \
                                                      python3.12-venv && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -ms /bin/bash app && \
    mkdir /encode_in && \
    mkdir /encode_out && \
    mkdir /output && \
    chown app /encode_in /encode_out /output

RUN echo 'alias python=python3' >> ~/.bashrc

COPY requirements.txt /requirements.txt

RUN python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

ENV VIRTUAL_ENV=/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . .

USER app
