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


def test_get_video_frame_rate_variable(fs):
    file_name = "thegreatoutdoors.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    fr = mediainfo.get_video_frame_rate()
    assert fr == '30'


def test_get_video_frame_rate_mode(fs):
    file_name = "harry_potter_prizoner.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    frm = mediainfo.get_video_frame_rate_mode()
    assert frm == 'CFR'

def test_get_video_frame_rate_mode_avi(fs):
    file_name = "troll_hunter.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    frm = mediainfo.get_video_frame_rate_mode()
    assert frm == 'VFR'


@pytest.mark.parametrize("file, exoected_bitrate",
                         [
                             ('harry_potter_prizoner.json', '19299022'),
                             ('drstones02e06.json', None),
                         ])
def test_get_video_bit_rate(fs, file, exoected_bitrate):
    file_name = file
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    br = mediainfo.get_video_bit_rate()
    assert br == exoected_bitrate


def test_get_video_bit_rate_maximum(fs):
    file_name = "jersey_girl.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    br = mediainfo.get_video_bit_rate_maximum()
    assert br == '24999936'


def test_get_video_bit_rate_mode(fs):
    file_name = "jersey_girl.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    brm = mediainfo.get_video_bit_rate_mode()
    assert brm == 'VBR'


def test_get_video_bit_depth(fs):
    file_name = "jersey_girl.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    bd = mediainfo.get_video_bit_depth()
    assert bd == '8'


def test_get_video_tracks_not_found(fs):
    """
    This tests for when the mkv doesn't actually contain a video track... wtf... EXCEPTION!!
    """
    with pytest.raises(KeyError):
        file_name = "americansniper.json"
        file_path = '/src' + "/" + file_name
        fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
        with open(file_path) as f:
            mediainfo = Mediainfo(file_path)
            mediainfo.set_mediainfo_json(json.load(f))
        mediainfo.get_video_tracks()


def test_get_video_bit_depth_10(fs):
    file_name = "simpsons_s01e11.json"
    file_path = '/src' + "/" + file_name
    fs.add_real_file(fixture_path + "/" + file_name, target_path=file_path)
    with open(file_path) as f:
        mediainfo = Mediainfo(file_path)
        mediainfo.set_mediainfo_json(json.load(f))
    bd = mediainfo.get_video_bit_depth()
    assert bd == '10'


def test_remove_accents():
    mediainfo = Mediainfo('x')
    original_file_name = 'Regé-'
    new_file_name = mediainfo.remove_accents(original_file_name)
    assert new_file_name != original_file_name


def test_pre_checks():
    import tempfile
    tf = tempfile.NamedTemporaryFile(delete=False, prefix='Regé-')
    mediainfo = Mediainfo(tf.name)
    mediainfo.pre_checks()
    assert mediainfo.file_renamed
    assert not os.path.exists(tf.name)


def test_pre_checks_no_rename():
    import tempfile
    tf = tempfile.NamedTemporaryFile(delete=False)
    mediainfo = Mediainfo(tf.name)
    mediainfo.pre_checks()
    assert not mediainfo.file_renamed
    assert os.path.exists(tf.name)


def test_post_checks():
    import tempfile
    tf1 = tempfile.NamedTemporaryFile(delete=False)
    tf2 = tempfile.NamedTemporaryFile(delete=False)
    mediainfo = Mediainfo(tf1.name)
    mediainfo.file_renamed = True
    mediainfo.full_path = tf1.name
    mediainfo.original_file_path = tf2.name
    mediainfo.post_checks()
    assert not os.path.exists(tf1.name)
    assert os.path.exists(tf2.name)


def test_post_checks_no_opp():
    import tempfile
    tf = tempfile.NamedTemporaryFile(delete=False)
    mediainfo = Mediainfo(tf.name)
    mediainfo.post_checks()
    assert os.path.exists(tf.name)
