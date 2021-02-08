import pytest
import os
from mediainfo.mediainfo import Mediainfo
import json

fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def my_fixtures(fs):
    fs.add_real_directory(fixture_path, target_path='/src')
    yield fs


def test_get_audio_tracks_from_json(fs):
    file_name = "simpsons_s01e11.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    audio_tracks = mediainfo.get_audio_tracks()
    assert len(audio_tracks) == 2


def test_get_audio_codec_ids(fs):
    file_name = "harry_potter_prizoner.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    codecs = mediainfo.get_audio_codec_ids()
    assert len(codecs) == 12
    assert codecs[0] == 'A_DTS'
    assert codecs[2] == 'A_AC3'


def test_get_subtitle_count(fs):
    file_name = "harry_potter_prizoner.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    subtitle_count = mediainfo.get_subtitle_count()
    assert subtitle_count == 13


def test_get_audio_track_count(fs):
    file_name = "simpsons_s01e11.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    track_count = mediainfo.get_audio_track_count()
    assert track_count == 2


def test_get_video_frame_rate(fs):
    file_name = "harry_potter_prizoner.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    fr = mediainfo.get_video_frame_rate()
    assert fr == '23.976'
