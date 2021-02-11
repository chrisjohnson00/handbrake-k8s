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
from mediainfo.mediainfo import Mediainfo
from handbrakeProfileGenerator.handbrake_profile_generator import HandbrakeProfileGenerator
from handbrakeOptionsGenerator.handbrake_options_generator import HandbrakeOptionGenerator

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
        return ""


def main(in_file_name, out_file_name, enc_profile, move_type):
    file_encoding_metrics = Gauge('handbrake_job_encoding_in_process', 'Job Encoding',
                                  labelnames=["type", "profile", "filename"])
    file_encoding_metrics.labels(move_type, enc_profile, in_file_name).inc()

    logger.info("Copying {} into container FS".format(in_file_name))
    subprocess.run(["cp", "/input/{}".format(in_file_name), "/encode_in/{}".format(in_file_name)], check=True)

    mediainfo = Mediainfo("/encode_in/{}".format(in_file_name))
    # mediainfo = Mediainfo("/input/{}".format(in_file_name))
    mediainfo.execute_mediainfo()

    logger.debug("mediainfo.all", extra={'json': mediainfo.mediainfo_json})

    file_encoding_time = Gauge('handbrake_job_encoding_duration', "Job Encoding Duration",
                               labelnames=["type", "profile", "filename"])

    hpg = HandbrakeProfileGenerator(mediainfo)
    hpg.set_video_encoder(get_config('HANDBRAKE_ENCODER'))
    hpg.set_video_quality(get_config('HANDBRAKE_QUALITY'))
    hpg.set_video_avg_bitrate(get_config('HANDBRAKE_VIDEO_BITRATE'))
    hpg.evaluate().render_profile('/tmp/generated.json')

    command = ["HandBrakeCLI", "-i", "/encode_in/{}".format(in_file_name), "-o", "/encode_out/{}".format(out_file_name),
               "--preset", "Generated", "--preset-import-file", "/tmp/generated.json"]
    command = command + get_config('HANDBRAKE_ADDITIONAL_PARAMETERS').split()
    hb_option_generator = HandbrakeOptionGenerator(mediainfo)
    command = command + hb_option_generator.generate_subtitle_flags()
    # exports = ['--preset-export', 'generated', '--preset-export-file', '/tmp/generated.json']
    # command = command + exports + hb_option_generator.generate_video_flags()
    # command = ["HandBrakeCLI", "-i", "/input/{}".format(in_file_name), "-o", "/encode_out/{}".format(out_file_name),
    #            "--preset", "Generated", "--preset-import-file", "/tmp/generated.json"]
    original_size = os.path.getsize("/encode_in/{}".format(in_file_name))
    logger.info("Running encoding with generated preset: {}".format(command))
    start_time = calendar.timegm(time.gmtime())
    subprocess.run(command, check=True)
    end_time = calendar.timegm(time.gmtime())
    encoded_size = os.path.getsize("/encode_out/{}".format(out_file_name))
    logger.info("sizing", extra={'original_size': original_size, 'encoded_size': encoded_size})
    file_encoding_time.labels(move_type, enc_profile, in_file_name).set((end_time - start_time))

    logger.info("Moving output file from container FS to mounted output dir")
    subprocess.run(["mv", "/encode_out/{}".format(out_file_name), "/output/{}".format(out_file_name)], check=True)

    logger.info("Removing input file")
    # subprocess.run(["rm", "-f", "/input/{}".format(in_file_name)], check=True)

    kafka_server = get_config('KAFKA_SERVER')
    kafka_topic = get_config('KAFKA_TOPIC')
    if kafka_server and kafka_topic:
        producer = KafkaProducer(bootstrap_servers=[kafka_server],
                                 acks=1,
                                 api_version_auto_timeout_ms=10000,
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))

        future = producer.send(topic=kafka_topic, value={'filename': out_file_name, 'move_type': move_type})
        future.get(timeout=60)
        logger.info("Sent notification for {}".format(in_file_name))
    else:
        logger.warning("KAFKA_SERVER or KAFKA_TOPIC was not found in configs, no messages will be sent")

    file_encoding_metrics.labels(move_type, enc_profile, in_file_name).dec()
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
    c1 = get_config('HANDBRAKE_ENCODER')
    c2 = get_config('HANDBRAKE_QUALITY')
    c3 = get_config('HANDBRAKE_VIDEO_BITRATE')  # is this even used??
    if not c1 or not c2 or not c3:
        exit("Missing manditory configurations for: HANDBRAKE_ENCODER, HANDBRAKE_QUALITY, HANDBRAKE_VIDEO_BITRATE")
    main(arg_in_file_name, arg_out_file_name, arg_enc_profile, arg_move_type)
