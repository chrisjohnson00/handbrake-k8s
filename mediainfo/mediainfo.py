import subprocess
from json import loads


class Mediainfo:

    def __init__(self, full_path: str):
        self.full_path = full_path
        self.mediainfo_json = None

    def execute_mediainfo(self):
        """
        This method calls to mediainfo to get all the details of the media file and returns a dict object
        :return: The mediainfo output as a dict
        """
        command = ['mediainfo', '-f', '--Output=JSON', self.full_path]
        completed_process = subprocess.run(command, check=True, capture_output=True)
        mediainfo_json = loads(completed_process.stdout)
        self.mediainfo_json = mediainfo_json
        return mediainfo_json

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
        return self.get_tracks_by_type(type)

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
