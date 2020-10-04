Something like this:

    docker run --rm -d \
            -v /path/to/your/movie:/input \
            -v /path/to/put/finished/file:/output \
            -e JOB_TYPE="dev/nul 
            chrisjohnson00/handbrakecli \
            input_movie_filename.mkv \
            output_movie_filename.mkv \
            "Profile name"
