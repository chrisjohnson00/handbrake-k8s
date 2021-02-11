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


#
# def test_load_profile_from_file(fs):
#     file_name = "jersey_girl.json"
#     file_path = '/src' + "/" + file_name
#     fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
#     hpg = HandbrakeProfileGenerator()
#     hpg.load_profile_from_file(file_path)
#     profile = hpg.profile
#     assert profile['Metadata']['Name'] == "JERSEY GIRL"


# def test_build_audio_copy_mask_from_mediainfo():
#     mock_mediainfo = mock.Mock(Mediainfo)
#     mediainfo_attrs = {'get_audio_tracks.return_value': [{"CodecID": "A_DTS", "Format_AdditionalFeatures": "XLL"},
#                                                          {"CodecID": "A_DTS"}, {"CodecID": "foobar"}]}
#     mock_mediainfo.configure_mock(**mediainfo_attrs)
#     hpg = HandbrakeProfileGenerator()
#     hpg.set_mediainfo(mock_mediainfo)
#     copy_mask = hpg.build_audio_copy_mask_from_mediainfo()
#     assert copy_mask == ['copy:dtshd', 'copy:dts']


# def test_build_audio_list_from_mediainfo():
#     mock_mediainfo = mock.Mock(Mediainfo)
#     mediainfo_attrs = {
#         'get_audio_tracks.return_value': [{'BitRate': 160000, "CodecID": "A_DTS", "Format_AdditionalFeatures": "XLL"},
#                                           {'BitRate': 320000, "CodecID": "A_DTS"},
#                                           {'BitRate': 320000, "CodecID": "foobar"}]}
#     mock_mediainfo.configure_mock(**mediainfo_attrs)
#     hpg = HandbrakeProfileGenerator(mock_mediainfo)
#     hpg.build_audio_list_from_mediainfo()
#     audio_list = hpg.audio_list
#     assert len(audio_list) == 3
#     audio_1 = audio_list[0]
#     audio_2 = audio_list[1]
#     audio_3 = audio_list[2]
#     assert audio_1['AudioBitrate'] == 160
#     assert audio_2['AudioBitrate'] == 320
#     assert audio_3['AudioBitrate'] == 320


# def test_build_audio():
#     mock_mediainfo = mock.Mock(Mediainfo)
#     mediainfo_attrs = {
#         'get_audio_tracks.return_value': [{'BitRate': 160000, "CodecID": "A_DTS", "Format_AdditionalFeatures": "XLL"},
#                                           {'BitRate': 320000, "CodecID": "A_DTS"},
#                                           {'BitRate': 160000, "CodecID": "foobar"}]}
#     mock_mediainfo.configure_mock(**mediainfo_attrs)
#     hpg = HandbrakeProfileGenerator()
#     hpg.set_mediainfo(mock_mediainfo)
#     audio = hpg.build_audio()
#     expected = {
#         "AudioList": [
#             {
#                 "Bitrate": 160,
#                 "DRC": 0.0,
#                 "Encoder": "copy:dtshd",
#                 "Gain": 0.0,
#                 "Mixdown": "none",
#                 "Quality": -3.0,
#                 "Samplerate": 0,
#                 "Track": 0
#             },
#             {
#                 "Bitrate": 320,
#                 "DRC": 0.0,
#                 "Encoder": "copy:dts",
#                 "Gain": 0.0,
#                 "Mixdown": "none",
#                 "Quality": -3.0,
#                 "Samplerate": 0,
#                 "Track": 1
#             },
#             {
#                 "Bitrate": 160,
#                 "DRC": 0.0,
#                 "Encoder": "av_aac",
#                 "Gain": 0.0,
#                 "Mixdown": "none",
#                 "Quality": -3.0,
#                 "Samplerate": 0,
#                 "Track": 2
#             }
#         ],
#         "CopyMask": [
#             "copy:dtshd",
#             "copy:dts"
#         ],
#         "FallbackEncoder": "av_aac"
#     }
#     assert audio == expected

def test_render_profile():
    import tempfile
    tf = tempfile.NamedTemporaryFile(delete=False)
    mock_mediainfo = mock.Mock(Mediainfo)
    hpg = HandbrakeProfileGenerator(mock_mediainfo)
    hpg.audio_list = []
    hpg.video_avg_bitrate = 14818507
    hpg.audio_tracks = [{'BitRate': '650000'}, {'BitRate': '15345'}]
    hpg.video_framerate_mode = 'CFR'
    hpg.render_profile(tf.name)
    assert os.path.exists(tf.name)
    with open(tf.name) as f:
        file_contents = f.read()
        assert 'PresetList' in file_contents
        assert '"VideoAvgBitrate": 14818,' in file_contents
        assert '"AudioBitrate": 640,' in file_contents  # testing the min function
        assert '"AudioBitrate": 15,' in file_contents
        assert '"VideoFramerateMode": "cfr"' in file_contents
    # print(tf.name)
    # exit(-1)


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
    assert audio_track_list[2]['AudioEncoder'] == 'av_aac'


def test_render_profile_variable_bit_rate_audio_track():
    import tempfile
    tf = tempfile.NamedTemporaryFile(delete=False)
    mock_mediainfo = mock.Mock(Mediainfo)
    hpg = HandbrakeProfileGenerator(mock_mediainfo)
    hpg.audio_list = []
    hpg.video_avg_bitrate = 14818507
    hpg.audio_tracks = [{'BitRate_Maximum': '7194000'}, {'BitRate': '15345'}]
    hpg.video_framerate_mode = 'CFR'
    hpg.render_profile(tf.name)
    assert os.path.exists(tf.name)
    with open(tf.name) as f:
        file_contents = f.read()
        assert 'PresetList' in file_contents
        assert '"VideoAvgBitrate": 14818,' in file_contents
        assert '"AudioBitrate": 7194,' in file_contents
        assert '"AudioBitrate": 15,' in file_contents
        assert '"VideoFramerateMode": "cfr"' in file_contents
