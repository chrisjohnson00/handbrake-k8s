from mediainfo.mediainfo import Mediainfo
import jinja2


class HandbrakeProfileGenerator:
    def __init__(self, mediainfo: Mediainfo):
        self.mediainfo = mediainfo
        self.audio_tracks = []
        self.video_avg_bitrate = None
        self.video_encoder = None
        self.video_framerate = None
        self.video_framerate_mode = None
        self.video_quality = None

    def set_mediainfo(self, mediainfo: Mediainfo):
        self.mediainfo = mediainfo

    def set_video_encoder(self, encoder):
        self.video_encoder = encoder

    def set_video_quality(self, quality):
        if quality:
            self.video_quality = quality

    @staticmethod
    def get_codec_copy_name(audio_track):
        codec_map = [
            {'codec_id': 'A_DTS', 'copy': 'copy:dts'},
            {'codec_id': 'A_AC3', 'copy': 'copy:ac3'},
            {'codec_id': 'ac-3', 'copy': 'copy:ac3'},
            {'codec_id': 'A_TRUEHD', 'copy': 'copy:truehd'},
            {'codec_id': 'A_MPEG/L3', 'copy': 'copy:mp3'},
            {'codec_id': 'A_AAC-2', 'copy': 'copy:aac'},
            {'codec_id': 'mp4a-40-2', 'copy': 'copy:aac'},
        ]
        for item in codec_map:
            if item['codec_id'] == audio_track['CodecID']:
                if 'Format_AdditionalFeatures' in audio_track and audio_track['Format_AdditionalFeatures'] == "XLL" \
                        and item['codec_id'] == 'A_DTS':
                    return 'copy:dtshd'
                else:
                    return item['copy']
        return 'av_aac'

    def build_audio_track_list(self):
        audio_tracks = self.mediainfo.get_audio_tracks()
        for track in audio_tracks:
            track['AudioEncoder'] = self.get_codec_copy_name(track)
            track['AudioBitrate'] = self.get_audio_bitrate(track)
        return audio_tracks

    @staticmethod
    def get_audio_bitrate(track):
        if 'BitRate' in track:
            value = int(track['BitRate'])
            return int(min([value / 1000, 640]))
        elif 'BitRate_Maximum' in track:
            value = int(track['BitRate_Maximum'])
            return int(value / 1000)
        else:
            return 640

    def evaluate(self):
        self.audio_tracks = self.build_audio_track_list()
        self.video_framerate = self.mediainfo.get_video_frame_rate()
        self.video_framerate_mode = self.mediainfo.get_video_frame_rate_mode()
        self.set_video_avg_bitrate()
        return self

    def set_video_avg_bitrate(self):
        if not self.video_avg_bitrate:
            vbr = self.mediainfo.get_video_bit_rate()
            if vbr:
                self.video_avg_bitrate = int(vbr) / 1000
            else:
                self.video_avg_bitrate = 6000

    def render_profile(self, file_path):
        template_loader = jinja2.FileSystemLoader(searchpath="./")
        template_env = jinja2.Environment(loader=template_loader)
        template_file = "profiles/profile.jinja2"
        template = template_env.get_template(template_file)
        output_text = template.render(audio_tracks=self.audio_tracks, video_avg_bitrate=self.video_avg_bitrate,
                                      video_encoder=self.video_encoder, video_framerate=self.video_framerate,
                                      video_framerate_mode=self.video_framerate_mode, video_quality=self.video_quality)
        with open(file_path, 'w') as outfile:
            outfile.write(output_text)
