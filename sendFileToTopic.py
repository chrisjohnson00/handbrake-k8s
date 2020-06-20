from json import dumps
from kafka import KafkaProducer
import sys
import os

if len(sys.argv) != 2:
    exit("Must pass filename")

producer = KafkaProducer(bootstrap_servers=['kafka-headless.kafka.svc.cluster.local:9092'],
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'))

filename = sys.argv[1]
move_type = os.environ.get("JOB_TYPE")

producer.send('completedHandbrakeEncoding', value={'filename': filename, 'move_type': move_type})
