from json import dumps
from kafka import KafkaProducer
import sys
import os
from prometheus_client import Gauge, start_http_server, Summary
import subprocess
import time

if len(sys.argv) != 4:
    exit("Must pass infile outfile encprofile")

producer = KafkaProducer(bootstrap_servers=['kafka-headless.kafka.svc.cluster.local:9092'],
                         acks=1,
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'))

in_file_name = sys.argv[1]
out_file_name = sys.argv[2]
enc_profile = sys.argv[3]
move_type = os.environ.get("JOB_TYPE")

start_http_server(8080)

file_encoding_metrics = Gauge('handbrake_job_encoding_in_process', 'Job Encoding',
                              labelnames=["type", "profile", "filename"])
file_encoding_metrics.labels(move_type, enc_profile, in_file_name).inc()

print("INFO: Copying file into container FS", flush=True)
subprocess.run(["cp", "/input/{}".format(in_file_name), "/encode_in/{}".format(in_file_name)], check=True)

file_encoding_time = Summary('handbrake_job_encoding_duration', "Job Encoding Duration",
                             labelnames=["type", "profile", "filename"])
with file_encoding_time.time():
    command = ["HandBrakeCLI", "-i", "/encode_in/{}".format(in_file_name), "-o", "/encode_out/{}".format(out_file_name),
               "--preset", "{}".format(enc_profile)]
    print(command, flush=True)
    handbrake_command = subprocess.run(command, check=True)

print("INFO: Moving output file from container FS to mounted output dir", flush=True)
subprocess.run(["mv", "/encode_out/{}".format(out_file_name), "/output/{}".format(out_file_name)], check=True)

print("INFO: Removing input file", flush=True)
subprocess.run(["rm", "-f", "/input/{}".format(in_file_name)], check=True)

future = producer.send(topic='completedHandbrakeEncoding', value={'filename': in_file_name, 'move_type': move_type})
result = future.get(timeout=60)

file_encoding_metrics.labels(move_type, enc_profile, in_file_name).dec
print("INFO: Sent notification for {}".format(in_file_name), flush=True)

# sleep for 20s to ensure tha prometheus scrapes the last set of stats
time.sleep(20)
