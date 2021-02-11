from handbrakeUtilities.handbrake_utilities import get_mixing_flag, get_codec_flag


def test_get_codec_flag():
    flag = get_codec_flag('A_AAC-2')
    assert flag == 'copy:aac'


def test_get_mixing_flag():
    flag = get_mixing_flag('6')
    assert flag == '5point1'
