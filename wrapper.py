from json import dumps
import sys
import os
from prometheus_client import Gauge, start_http_server
import subprocess
import time
import calendar
import consul
import random
import pygogo as gogo
from mediainfo.mediainfo import Mediainfo
from handbrakeProfileGenerator.handbrake_profile_generator import HandbrakeProfileGenerator
from handbrakeOptionsGenerator.handbrake_options_generator import HandbrakeOptionGenerator
import pulsar

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


def main(in_file_name, out_file_name, move_type):
    # move the file into the container file system
    logger.info("Copying {} into container FS".format(in_file_name))
    subprocess.run(["cp", "/input/{}".format(in_file_name), "/encode_in/{}".format(in_file_name)], check=True)

    # get media info
    mediainfo = Mediainfo("/encode_in/{}".format(in_file_name))
    mediainfo.execute_mediainfo()
    logger.debug("mediainfo.all", extra={'json': mediainfo.mediainfo_json})
    logger.info("mediainfo", extra={'bit_depth': mediainfo.get_video_bit_depth()})

    # setting metrics
    # @TODO - encoder should just be x265 or whatever.  Get bit rate depth from mediainfo and build the encoder profile
    enc_profile = get_config('HANDBRAKE_ENCODER')
    file_encoding_metrics = Gauge('handbrake_job_encoding_in_process', 'Job Encoding',
                                  labelnames=["type", "profile", "filename"])
    file_encoding_metrics.labels(move_type, enc_profile, in_file_name).inc()
    file_encoding_time = Gauge('handbrake_job_encoding_duration', "Job Encoding Duration",
                               labelnames=["type", "profile", "filename"])

    # generate HB profile
    hpg = HandbrakeProfileGenerator(mediainfo)
    hpg.set_video_encoder(get_config('HANDBRAKE_ENCODER'))
    hpg.set_video_quality(get_config('HANDBRAKE_QUALITY'))
    if get_config('HANDBRAKE_VIDEO_BITRATE'):
        hpg.video_avg_bitrate = get_config('HANDBRAKE_VIDEO_BITRATE')
    hpg.evaluate().render_profile('/tmp/generated.json')
    f = open('/tmp/generated.json', 'r')
    logger.debug("Generated profile", extra={'generated_profile': f.read()})

    # build the handbrake execution command
    command = ["HandBrakeCLI", "-i", "/encode_in/{}".format(in_file_name), "-o", "/encode_out/{}".format(out_file_name),
               "--preset", "Generated", "--preset-import-file", "/tmp/generated.json"]
    # append any additional params from env config
    command = command + get_config('HANDBRAKE_ADDITIONAL_PARAMETERS').split()
    hb_option_generator = HandbrakeOptionGenerator(mediainfo)
    # add subtitle flags
    command = command + hb_option_generator.generate_subtitle_flags()
    # start encoding
    logger.info("Running encoding with generated preset: {}".format(command))
    logger.info("Encoding starting", extra={'file_name': in_file_name})
    start_time = calendar.timegm(time.gmtime())
    try:
        log_sample_rate = float(os.getenv("HANDBRAKE_LOG_SAMPLE_RATE", "0.01"))  # 1% of the log output
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as process:
            # Stream the output line by line
            for line in process.stdout:
                if random.random() < log_sample_rate:  # Log a sample of the output
                    logger.info(line.strip())
        # Check the return code
        if process.returncode != 0:
            logger.error(f"Command failed with return code {process.returncode}")
        else:
            logger.info("Command completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error("Encoding failed", extra={'error_message': e})
        raise e
    end_time = calendar.timegm(time.gmtime())
    # end encoding
    logger.info("Encoding completed", extra={'file_name': in_file_name})
    # set metrics
    original_size = os.path.getsize("/encode_in/{}".format(in_file_name))
    encoded_size = os.path.getsize("/encode_out/{}".format(out_file_name))
    logger.info("sizing", extra={'original_size': original_size, 'encoded_size': encoded_size})
    file_encoding_time.labels(move_type, enc_profile, in_file_name).set((end_time - start_time))
    file_encoding_metrics.labels(move_type, enc_profile, in_file_name).dec()
    file_encoding_complete = Gauge('handbrake_job_encoding_complete', 'Job Encoding Complete',
                                   labelnames=["type", "profile", "filename"])
    file_encoding_complete.labels(move_type, enc_profile, in_file_name).set(1)

    # move out of the container file system
    logger.info("Moving output file from container FS to mounted output dir")
    subprocess.run(["mv", "/encode_out/{}".format(out_file_name), "/output/{}".format(out_file_name)], check=True)

    # remove original/input file
    logger.info("Removing input file", extra={'file_name': in_file_name})
    subprocess.run(["rm", "-f", "/input/{}".format(in_file_name)], check=True)

    send_completion_message(in_file_name, move_type, out_file_name)

    # sleep for 90s to ensure that prometheus scrapes the last set of stats
    time.sleep(90)


def send_completion_message(in_file_name, move_type, out_file_name):
    pulsar_server = get_config('PULSAR_SERVER')
    pulsar_topic = get_config('PULSAR_TOPIC')
    if pulsar_server and pulsar_topic:
        client = pulsar.Client(f"pulsar://{pulsar_server}")
        producer = client.create_producer(pulsar_topic)
        message = {'filename': out_file_name, 'move_type': move_type}
        producer.send(dumps(message).encode('utf-8'))
        logger.info("Notification sent", extra={'message_body': message, 'topic': pulsar_topic, 'file': in_file_name})
        client.close()
    else:
        logger.warning("PULSAR_SERVER or PULSAR_TOPIC was not found in configs, no messages will be sent")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        exit("Must pass infile outfile")
    arg_in_file_name = sys.argv[1]
    arg_out_file_name = sys.argv[2]
    arg_move_type = os.environ.get("JOB_TYPE")
    c1 = get_config('HANDBRAKE_ENCODER')
    c2 = get_config('HANDBRAKE_QUALITY')
    c3 = get_config('HANDBRAKE_VIDEO_BITRATE')
    if not c1:
        exit("Missing mandatory configurations for: HANDBRAKE_ENCODER")
    if not c2 and not c3:
        exit("Missing mandatory configurations for: HANDBRAKE_QUALITY or HANDBRAKE_VIDEO_BITRATE")
    main(arg_in_file_name, arg_out_file_name, arg_move_type)
