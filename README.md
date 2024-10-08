# PyPi Dependencies

```shell
docker run -it -v ${PWD}:/app -w /app python:3.10-slim bash
pip install --upgrade pip
pip install --upgrade pulsar-client fastavro prometheus-client python-consul pygogo jinja2
pip freeze > requirements.txt
```

# Run it manually

    docker build . -t handbrakecli

    docker run -it --rm -v /mnt/video/Television/The\ Simpsons/Season\ 1:/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    export HANDBRAKE_VIDEO_BITRATE="10000"
    python3 wrapper.py 'The Simpsons - S01E11 - The Crepes of Wrath WEBRip-1080p Proper.mp4' 'The Simpsons - S01E11 - The Crepes of Wrath WEBRip-1080p Proper.mp4'
    
    docker run -it --rm -v /mnt/video/Television/SpongeBob\ SquarePants/Season\ 1:/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    export HANDBRAKE_VIDEO_BITRATE="10000"
    export HANDBRAKE_LOG_SAMPLE_RATE=0.5
    python3 wrapper.py "SpongeBob SquarePants - S01E16-17 - Sandy's Rocket + Squeaky Boots WEBDL-1080p.mkv" "SpongeBob SquarePants - S01E16-17 - Sandy's Rocket + Squeaky Boots WEBDL-1080p.mkv"

    docker run -it --rm -v /mnt/video/Movies/Bad\ Words\ \(2013\):/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    export HANDBRAKE_VIDEO_BITRATE="10000"
    python3 wrapper.py 'Bad Words (2013).mp4' 'Bad Words (2013).mp4' 'My 1080p'

    docker run -it --rm -v /mnt/video/Television/Call\ Me\ Kat/Season\ 1:/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    export HANDBRAKE_VIDEO_BITRATE="10000"
    python3 wrapper.py 'Call Me Kat - S01E08 - All Nighter WEBDL-1080p.mkv' 'Call Me Kat - S01E08 - All Nighter WEBDL-1080p.mkv'

    docker run -it --rm -v /home/chris/Documents/JERSEY\ GIRL:/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    export HANDBRAKE_VIDEO_BITRATE="10000000"
    python3 wrapper.py 'JERSEY GIRL_t00.mkv' 'JERSEY GIRL_t00.mkv' 'My 1080p'

    docker run -it --rm -v /mnt/video/copy:/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    python3 wrapper.py Saturday\ Night\ Live\ -\ S46E13\ -\ Regé-Jean\ Page\ +\ Bad\ Bunny\ WEBDL-1080p.mkv Saturday\ Night\ Live\ -\ S46E13\ -\ Regé-Jean\ Page\ +\ Bad\ Bunny\ WEBDL-1080p.mkv

    docker build . -t handbrakecli
    docker run -it --rm -v /mnt/video/Television/DC\'s\ Legends\ of\ Tomorrow/Season\ 1:/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    export HANDBRAKE_VIDEO_BITRATE="10000"
    python3 wrapper.py S01E01.mkv S01E01.mkv
    
