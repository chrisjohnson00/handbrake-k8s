# PyPi Dependencies

    pip install --upgrade kafka-python prometheus-client python-consul pygogo jinja2
    pip freeze > requirements.txt
    sed -i '/pkg-resources/d' requirements.txt

# Run it manually

    docker build . -t handbrakecli
    docker run -it --rm -v /mnt/video/Television/The\ Simpsons/Season\ 1:/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    export HANDBRAKE_VIDEO_BITRATE="10000"
    python3 wrapper.py 'The Simpsons - S01E11 - The Crepes of Wrath WEBDL-1080p.mkv' 'The Simpsons - S01E11 - The Crepes of Wrath WEBDL-1080p.mkv' 'My 1080p'
    
    docker run -it --rm -v /mnt/video/Television/SpongeBob\ SquarePants/Season\ 1:/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    export HANDBRAKE_VIDEO_BITRATE="10000"
    python3 wrapper.py 'SpongeBob SquarePants - S01E02 - Reef Blower SDTV.mkv' 'SpongeBob SquarePants - S01E02 - Reef Blower SDTV.mkv' 'My 1080p'

    docker run -it --rm -v /mnt/video/Movies/Bad\ Words\ \(2013\):/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    export HANDBRAKE_VIDEO_BITRATE="10000"
    python3 wrapper.py 'Bad Words (2013).mp4' 'Bad Words (2013).mp4' 'My 1080p'

    docker build . -t handbrakecli
    docker run -it --rm -v /home/chris/Documents/JERSEY\ GIRL:/input handbrakecli bash
    export HANDBRAKE_ENCODER="x265_10bit"
    export HANDBRAKE_QUALITY="40.0"
    export HANDBRAKE_VIDEO_BITRATE="10000000"
    python3 wrapper.py 'JERSEY GIRL_t00.mkv' 'JERSEY GIRL_t00.mkv' 'My 1080p'
