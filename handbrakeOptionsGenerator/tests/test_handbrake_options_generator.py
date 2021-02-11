import pytest
from mediainfo.mediainfo import Mediainfo
from handbrakeOptionsGenerator.handbrake_options_generator import HandbrakeOptionGenerator
import os
import json
from unittest import mock

fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def my_fixtures(fs):
    fs.add_real_directory(fixture_path, target_path='/src')
    yield fs


def test_get_subtitle_flags(fs):
    file_name = "harry_potter_prizoner.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    handbrake_options = HandbrakeOptionGenerator(mediainfo)
    flags = handbrake_options.generate_subtitle_flags()
    assert flags == ['-s', '1,2,3,4,5,6,7,8,9,10,11,12,13']


def test_get_subtitle_flags_simpsons(fs):
    file_name = "simpsons_s01e11.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    handbrake_options = HandbrakeOptionGenerator(mediainfo)
    flags = handbrake_options.generate_subtitle_flags()
    assert flags == []


def test_get_audio_codec_flags():
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {'get_audio_codec_ids.return_value': ['A_DTS', 'A_AC3', 'A_TRUEHD'],
                       'get_audio_track_count.return_value': 3}
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    handbrake_options = HandbrakeOptionGenerator(mock_mediainfo)
    handbrake_options.get_audio_codec_flags()
    flags = handbrake_options.audio_flags
    assert flags == ['--aencoder', 'copy:ac3,copy:dts,copy:dtshd,copy:truehd', '--audio-fallback', 'av_aac']


def test_get_audio_codec_flags_no_copy_matches():
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {'get_audio_codec_ids.return_value': ['x'], 'get_audio_track_count.return_value': 1}
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    handbrake_options = HandbrakeOptionGenerator(mock_mediainfo)
    handbrake_options.get_audio_codec_flags()
    flags = handbrake_options.audio_flags
    assert flags == ['--audio-fallback', 'av_aac']


def test_get_audio_codec_flags_duplicate_codecs():
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {'get_audio_codec_ids.return_value': ['A_AC3', 'A_AC3'], 'get_audio_track_count.return_value': 2}
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    handbrake_options = HandbrakeOptionGenerator(mock_mediainfo)
    handbrake_options.get_audio_codec_flags()
    flags = handbrake_options.audio_flags
    assert flags == ['--aencoder', 'copy:ac3', '--audio-fallback', 'av_aac']


def test_get_video_flags():
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {'get_video_frame_rate.return_value': '99.234', 'get_video_frame_rate_mode.return_value': 'CFR'}
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    handbrake_options = HandbrakeOptionGenerator(mock_mediainfo)
    assert handbrake_options.generate_video_flags() == ['-r', '99.234', '--cfr']


def test_get_audio_track_number_flags():
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {'get_audio_track_count.return_value': 2}
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    handbrake_options = HandbrakeOptionGenerator(mock_mediainfo)
    handbrake_options.get_audio_track_number_flags()
    flags = handbrake_options.audio_flags
    assert flags == ['-a', '1,2']


def test_get_audio_track_bitrates():
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {'get_audio_tracks.return_value': [{'BitRate': '1000'}, {'BitRate': '2000'}]}
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    handbrake_options = HandbrakeOptionGenerator(mock_mediainfo)
    handbrake_options.get_audio_track_bitrates()
    flags = handbrake_options.audio_flags
    assert flags == ['--ab', '1,2']


def test_get_audio_track_sample_rate():
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {'get_audio_tracks.return_value': [{'SamplingRate': '48000'}, {'SamplingRate': '48000'}]}
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    handbrake_options = HandbrakeOptionGenerator(mock_mediainfo)
    handbrake_options.get_audio_track_sample_rate()
    flags = handbrake_options.audio_flags
    assert flags == ['--arate', 'auto,auto']


def test_get_audio_mixing_flags(fs):
    file_name = "jersey_girl.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    handbrake_options = HandbrakeOptionGenerator(mediainfo)
    handbrake_options.get_audio_mixing_flags()
    flags = handbrake_options.audio_flags
    assert flags == ['--mixdown', '5point1,5point1,stereo,stereo,stereo,stereo']
