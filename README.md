# PyPi Dependencies

    pip install --upgrade kafka-python prometheus-client python-consul pygogo
    pip freeze > requirements.txt
    sed -i '/pkg-resources/d' requirements.txt
