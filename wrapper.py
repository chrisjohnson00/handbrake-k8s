from json import dumps
from kafka import KafkaProducer
import sys
import os
from prometheus_client import Gauge, start_http_server, Summary
import subprocess
import time
import calendar

if len(sys.argv) != 4:
    exit("Must pass infile outfile encprofile")

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

file_encoding_time = Gauge('handbrake_job_encoding_duration', "Job Encoding Duration",
                           labelnames=["type", "profile", "filename"])
start_time = calendar.timegm(time.gmtime())
command = ["HandBrakeCLI", "-i", "/encode_in/{}".format(in_file_name), "-o", "/encode_out/{}".format(out_file_name),
           "--preset", "{}".format(enc_profile), "--preset-import-file", "/profiles/myprofiles.json", "--aencoder",
           "copy:ac3,copy:aac,copy:dts,copy:dtshd,copy:mp3,copy:flac,copy:eac3,copy:truehd", "-s",
           "'1,2,3,4,5,6,7,8,9,10'"]
print(command, flush=True)
handbrake_command = subprocess.run(command, check=True)
end_time = calendar.timegm(time.gmtime())
file_encoding_time.labels(move_type, enc_profile, in_file_name).set((end_time - start_time))

print("INFO: Moving output file from container FS to mounted output dir", flush=True)
subprocess.run(["mv", "/encode_out/{}".format(out_file_name), "/output/{}".format(out_file_name)], check=True)

print("INFO: Removing input file", flush=True)
subprocess.run(["rm", "-f", "/input/{}".format(in_file_name)], check=True)

producer = KafkaProducer(bootstrap_servers=['kafka-headless.kafka.svc.cluster.local:9092'],
                         acks=1,
                         api_version_auto_timeout_ms=10000,
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'))

future = producer.send(topic='handbrakeFile', value={'filename': out_file_name, 'move_type': move_type})
result = future.get(timeout=60)

file_encoding_metrics.labels(move_type, enc_profile, in_file_name).dec()
print("INFO: Sent notification for {}".format(in_file_name), flush=True)

file_encoding_complete = Gauge('handbrake_job_encoding_complete', 'Job Encoding Complete',
                               labelnames=["type", "profile", "filename"])
file_encoding_complete.labels(move_type, enc_profile, in_file_name).set(1)

# sleep for 90s to ensure that prometheus scrapes the last set of stats
time.sleep(90)
