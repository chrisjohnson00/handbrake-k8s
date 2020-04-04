Something like this:

    docker run --rm -d  \
                -v /source:/input \
                -v /dest:/output \
                handbrakecli \
                -i /input/movie.mkv \
                -o /output/movie.mkv \
                $HANDBRAKE_OPTIONS