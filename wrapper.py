from json import dumps
from kafka import KafkaProducer
import sys
import os
from prometheus_client import Gauge, start_http_server
import subprocess
import time
import calendar
import consul
import pygogo as gogo
from mediainfo.mediainfo import get_as_json

CONFIG_PATH = "handbrake-job"
# logging setup
kwargs = {}
formatter = gogo.formatters.structured_formatter
logger = gogo.Gogo('struct', low_formatter=formatter).get_logger(**kwargs)
start_http_server(8080)


def get_config(key, config_path=CONFIG_PATH):
    if os.environ.get(key):
        return os.environ.get(key)
    try:
        c = consul.Consul()
        index, data = c.kv.get("{}/{}".format(config_path, key))
        return data['Value'].decode("utf-8")
    except Exception:
        print("WARN: {} was not found in Consul".format(key), flush=True)
        return ""


def main(in_file_name, out_file_name, enc_profile, move_type):
    file_encoding_metrics = Gauge('handbrake_job_encoding_in_process', 'Job Encoding',
                                  labelnames=["type", "profile", "filename"])
    file_encoding_metrics.labels(move_type, enc_profile, in_file_name).inc()

    logger.info("Copying {} into container FS".format(in_file_name))
    subprocess.run(["cp", "/input/{}".format(in_file_name), "/encode_in/{}".format(in_file_name)], check=True)

    logger.debug("mediainfo", extra={'json': get_as_json("/encode_in/{}".format(in_file_name))})

    file_encoding_time = Gauge('handbrake_job_encoding_duration', "Job Encoding Duration",
                               labelnames=["type", "profile", "filename"])
    start_time = calendar.timegm(time.gmtime())
    command = ["HandBrakeCLI", "-i", "/encode_in/{}".format(in_file_name), "-o", "/encode_out/{}".format(out_file_name),
               "--preset", "{}".format(enc_profile), "--preset-import-file", "/profiles/myprofiles.json"]
    command = command + get_config('HANDBRAKE_ADDITIONAL_PARAMETERS').split()
    print(command, flush=True)
    subprocess.run(command, check=True)
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
    future.get(timeout=60)

    file_encoding_metrics.labels(move_type, enc_profile, in_file_name).dec()
    print("INFO: Sent notification for {}".format(in_file_name), flush=True)

    file_encoding_complete = Gauge('handbrake_job_encoding_complete', 'Job Encoding Complete',
                                   labelnames=["type", "profile", "filename"])
    file_encoding_complete.labels(move_type, enc_profile, in_file_name).set(1)

    # sleep for 90s to ensure that prometheus scrapes the last set of stats
    time.sleep(90)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        exit("Must pass infile outfile encprofile")

    arg_in_file_name = sys.argv[1]
    arg_out_file_name = sys.argv[2]
    arg_enc_profile = sys.argv[3]
    arg_move_type = os.environ.get("JOB_TYPE")
    main(arg_in_file_name, arg_out_file_name, arg_enc_profile, arg_move_type)
