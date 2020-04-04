Something like this:

    docker run --rm -d  \
                -v /source:/input \
                -v /dest:/output \
                chrisjohnson00/handbrakecli \
                -i /input/movie.mkv \
                -o /output/movie.mkv \
                $HANDBRAKE_OPTIONS