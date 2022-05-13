import subprocess
from json import loads
import unicodedata
import os


class Mediainfo:

    def __init__(self, full_path: str):
        self.full_path = full_path
        self.mediainfo_json = None
        self.file_renamed = False
        self.original_file_path = full_path

    def execute_mediainfo(self):
        """
        This method calls to mediainfo to get all the details of the media file and returns a dict object
        :return: The mediainfo output as a dict
        """
        self.pre_checks()
        command = ['mediainfo', '-f', '--Output=JSON', self.full_path]
        completed_process = subprocess.run(command, check=True, capture_output=True)
        mediainfo_json = loads(completed_process.stdout)
        self.mediainfo_json = mediainfo_json
        self.post_checks()
        return mediainfo_json

    def pre_checks(self):
        new_file_name = self.remove_accents(self.full_path)
        if new_file_name != self.full_path:
            try:
                os.rename(self.full_path, new_file_name)
                self.file_renamed = True
                self.full_path = new_file_name
            except Exception as e:
                print(e)
                raise e

    def post_checks(self):
        if self.file_renamed:
            os.rename(self.full_path, self.original_file_path)
            self.file_renamed = False
            self.full_path = self.original_file_path

    @staticmethod
    def remove_accents(s):
        nkfd_form = unicodedata.normalize('NFKD', s)
        return u''.join([c for c in nkfd_form if not unicodedata.combining(c)])

    def set_mediainfo_json(self, json):
        self.mediainfo_json = json

    def get_text_tracks(self):
        type = 'Text'
        return self.get_tracks_by_type(type)

    def get_tracks_by_type(self, type):
        tracks_to_return = []
        tracks = self.mediainfo_json['media']['track']
        for track in tracks:
            if track['@type'] == type:
                tracks_to_return.append(track)
        return tracks_to_return

    def get_subtitle_count(self):
        subtitles = self.get_text_tracks()
        return len(subtitles)

    def get_audio_tracks(self):
        type = 'Audio'
        return self.get_tracks_by_type(type)

    def get_audio_track_count(self):
        tracks = self.get_audio_tracks()
        return len(tracks)

    def get_video_tracks(self):
        type = 'Video'
        video_tracks = self.get_tracks_by_type(type)
        if len(video_tracks) < 1:
            raise KeyError('No video tracks found!')
        else:
            return video_tracks

    def get_audio_codec_ids(self):
        audio_tracks = self.get_audio_tracks()
        codecs = []
        for audio_track in audio_tracks:
            codecs.append(audio_track['CodecID'])
        return codecs

    def get_video_frame_rate(self):
        video_tracks = self.get_video_tracks()
        first_track = video_tracks[0]
        return first_track['FrameRate']

    def get_video_frame_rate_mode(self):
        video_tracks = self.get_video_tracks()
        first_track = video_tracks[0]
        return first_track['FrameRate_Mode']

    def get_video_bit_rate_maximum(self):
        video_tracks = self.get_video_tracks()
        first_track = video_tracks[0]
        return first_track['BitRate_Maximum']

    def get_video_bit_rate(self):
        video_tracks = self.get_video_tracks()
        first_track = video_tracks[0]
        if 'BitRate' in first_track:
            return first_track['BitRate']
        else:
            return None

    def get_video_bit_rate_mode(self):
        video_tracks = self.get_video_tracks()
        first_track = video_tracks[0]
        return first_track['BitRate_Mode']

    def get_video_bit_depth(self):
        video_tracks = self.get_video_tracks()
        first_track = video_tracks[0]
        if 'BitDepth' in first_track:
            return first_track['BitDepth']
        else:
            return None
