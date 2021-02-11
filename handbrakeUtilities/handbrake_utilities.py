def get_codec_flag(codec):
    codec_map = [
        {'codec_id': 'A_DTS', 'copy': 'copy:dts,copy:dtshd'},
        {'codec_id': 'A_AC3', 'copy': 'copy:ac3'},
        {'codec_id': 'ac-3', 'copy': 'copy:ac3'},
        {'codec_id': 'A_TRUEHD', 'copy': 'copy:truehd'},
        {'codec_id': 'A_MPEG/L3', 'copy': 'copy:mp3'},
        {'codec_id': 'A_AAC-2', 'copy': 'copy:aac'},
        {'codec_id': 'mp4a-40-2', 'copy': 'copy:aac'},
    ]
    for item in codec_map:
        if item['codec_id'] == codec:
            return item['copy']
    return None


def get_mixing_flag(channels):
    map = [
        {'channels': '6', 'mix': '5point1'},
        {'channels': '2', 'mix': 'stereo'},
        {'channels': '1', 'mix': 'mono'},
        {'channels': '8', 'mix': '7point1'},
    ]
    for item in map:
        if item['channels'] == channels:
            return item['mix']
    raise Exception("BARF!!! Encountered un-configured channel... {}".format(channels))
