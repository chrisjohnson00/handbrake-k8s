import pytest
from mediainfo.mediainfo import Mediainfo
from handbrakeProfileGenerator.handbrake_profile_generator import HandbrakeProfileGenerator
import os
from unittest import mock

fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def my_fixtures(fs):
    fs.add_real_directory(fixture_path, target_path='/src')
    yield fs


def test_render_profile():
    import tempfile
    tf = tempfile.NamedTemporaryFile(delete=False)
    mock_mediainfo = mock.Mock(Mediainfo)
    hpg = HandbrakeProfileGenerator(mock_mediainfo)
    hpg.audio_tracks = [{'AudioBitrate': 650, 'AudioEncoder': 'yomamma'}]
    hpg.video_avg_bitrate = 14818507
    hpg.video_framerate_mode = 'CFR'
    hpg.render_profile(tf.name)
    assert os.path.exists(tf.name)
    with open(tf.name) as f:
        file_contents = f.read()
        assert 'PresetList' in file_contents
        assert '"AudioBitrate": 650,' in file_contents
        assert '"AudioEncoder": "yomamma",' in file_contents
        assert '"VideoFramerateMode": "cfr"' in file_contents


def test_build_audio_track_list():
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {
        'get_audio_tracks.return_value': [{'BitRate': 160000, "CodecID": "A_DTS", "Format_AdditionalFeatures": "XLL"},
                                          {'BitRate': 320000, "CodecID": "A_DTS"},
                                          {'BitRate': 320000, "CodecID": "foobar"}]}
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    hpg = HandbrakeProfileGenerator(mock_mediainfo)
    audio_track_list = hpg.build_audio_track_list()
    assert audio_track_list[0]['AudioEncoder'] == 'copy:dtshd'
    assert audio_track_list[1]['AudioEncoder'] == 'copy:dts'
    assert audio_track_list[2]['AudioEncoder'] == 'ac3'
    assert audio_track_list[3]['AudioEncoder'] == 'av_aac'


@pytest.mark.parametrize("track,expected",
                         [
                             ({}, 640),
                             ({'BitRate': '15345'}, 15),
                             ({'BitRate_Maximum': '7194000'}, 7194),
                             ({'BitRate': "4608000 / 4608000"}, 4608)
                         ])
def test_get_audio_bitrate(track, expected):
    mock_mediainfo = mock.Mock(Mediainfo)
    hpg = HandbrakeProfileGenerator(mock_mediainfo)
    bitrate = hpg.get_audio_bitrate(track)
    assert bitrate == expected


def test_evaluate():
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {
        'get_audio_tracks.return_value': [],
        'get_video_frame_rate.return_value': 'None',
        'get_video_frame_rate_mode.return_value': 'None',
        'get_video_bit_rate.return_value': '99000',
    }
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    hpg = HandbrakeProfileGenerator(mock_mediainfo)
    hpg = hpg.evaluate()
    assert hpg.video_avg_bitrate == 99


def test_evaluate_pre_set_bitrate():
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {
        'get_audio_tracks.return_value': [],
        'get_video_frame_rate.return_value': 'None',
        'get_video_frame_rate_mode.return_value': 'None',
        'get_video_bit_rate.return_value': '99',
    }
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    hpg = HandbrakeProfileGenerator(mock_mediainfo)
    hpg.video_avg_bitrate = 100
    hpg = hpg.evaluate()
    assert hpg.video_avg_bitrate == 100


def test_set_video_quality():
    hpg = HandbrakeProfileGenerator(mock.Mock(Mediainfo))
    hpg.video_quality = '40'
    hpg.set_video_quality(None)
    assert hpg.video_quality == '40'
    hpg.set_video_quality('20')
    assert hpg.video_quality == '20'


def test_set_video_avg_bitrate_value_specified():
    hpg = HandbrakeProfileGenerator(mock.Mock(Mediainfo))
    hpg.video_avg_bitrate = 40
    assert hpg.video_avg_bitrate == 40


@pytest.mark.parametrize("bitrate, expected",
                         [
                             (None, 6000),
                             ('7194000', 7194)
                         ])
def test_set_video_avg_bitrate(bitrate, expected):
    mock_mediainfo = mock.Mock(Mediainfo)
    mediainfo_attrs = {'get_video_bit_rate.return_value': bitrate}
    mock_mediainfo.configure_mock(**mediainfo_attrs)
    hpg = HandbrakeProfileGenerator(mock_mediainfo)
    hpg.set_video_avg_bitrate()
    assert hpg.video_avg_bitrate == expected
