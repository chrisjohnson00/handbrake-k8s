import subprocess
from json import loads


def get_as_json(full_path):
    """
    This method calls to mediainfo to get all the details of the media file and returns a dict object
    :param full_path: The path to the file
    :return: The mediainfo output as a dict
    """
    command = ['mediainfo', '-f', '--Output=JSON', full_path]
    completed_process = subprocess.run(command, check=True, capture_output=True)
    mediainfo_json = loads(completed_process.stdout)
    return mediainfo_json
