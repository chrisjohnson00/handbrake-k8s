from mediainfo.mediainfo import Mediainfo
from handbrakeUtilities.handbrake_utilities import get_mixing_flag, get_codec_flag


class HandbrakeOptionGenerator:
    def __init__(self, mediainfo: Mediainfo):
        self.mediainfo = mediainfo
        self.audio_flags = []

    def generate_audio_flags(self):
        track_count = self.mediainfo.get_audio_track_count()
        if track_count > 0:
            self.get_audio_codec_flags()
            self.get_audio_track_number_flags()
            self.get_audio_track_bitrates()
            self.get_audio_track_sample_rate()
            self.get_audio_mixing_flags()
        return self.audio_flags

    def get_audio_track_number_flags(self):
        self.audio_flags.append('-a')
        track_indexes = []
        for i in range(1, (self.mediainfo.get_audio_track_count() + 1)):
            track_indexes.append(str(i))
        self.audio_flags.append(",".join(track_indexes))

    def get_audio_track_bitrates(self):
        self.audio_flags.append('--ab')
        audio_tracks = self.mediainfo.get_audio_tracks()
        bit_rates = []
        for track in audio_tracks:
            # convert from string to int, do the math, then convert from float to int, then finally to string!
            bit_rates.append(str(int(int(track['BitRate']) / 1000)))
        self.audio_flags.append(",".join(bit_rates))

    def get_audio_track_sample_rate(self):
        self.audio_flags.append('--arate')
        audio_tracks = self.mediainfo.get_audio_tracks()
        samples = []
        for track in audio_tracks:
            samples.append('auto')
        self.audio_flags.append(",".join(samples))

    def get_audio_codec_flags(self):
        codecs = self.mediainfo.get_audio_codec_ids()
        copy_flags = []
        for codec in codecs:
            flag = get_codec_flag(codec)
            if flag:
                copy_flags.append(flag)
        if copy_flags:
            self.audio_flags.append('--aencoder')
            flag_list = list(set(copy_flags))
            flag_list.sort()
            self.audio_flags.append(",".join(flag_list))
        self.audio_flags.append('--audio-fallback')
        self.audio_flags.append('av_aac')

    def get_audio_mixing_flags(self):
        self.audio_flags.append('--mixdown')
        audio_tracks = self.mediainfo.get_audio_tracks()
        mix_flags = []
        for track in audio_tracks:
            mix_flags.append(get_mixing_flag(track['Channels']))
        self.audio_flags.append(",".join(mix_flags))

    def generate_subtitle_flags(self):
        subtitle_flags = []
        if self.mediainfo.get_subtitle_count() > 0:
            subtitle_flags = ["-s"]
            subtitle_indexes = []
            for i in range(1, self.mediainfo.get_subtitle_count() + 1):
                subtitle_indexes.append(str(i))
            subtitle_flags.append(",".join(subtitle_indexes))
        return subtitle_flags

    def generate_video_flags(self):
        # --vfr, --cfr, --pfr
        if self.mediainfo.get_video_frame_rate_mode() != 'CFR':
            raise Exception("Found a new frame rate mode, add it to handbrake-container")
        frame_rate_mode = '--cfr'
        return ['-r', self.mediainfo.get_video_frame_rate(), frame_rate_mode]
