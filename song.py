# a song class referenced to work with songs!
class Song(object):

    songList = []

    def __init__(self, audioSeg):
        self.seg = audioSeg
        self.peakArray = []
        self.threshold = None
        self.ratio = None
        self.attack = None
        self.delay = None
        self.volChange = None
        self.waveStart = 0
        Song.songList.append(self)

    def __repr__(self):
        return f'{self.seg}'

    def __eq__(self, other):
        if isinstance(other, Song):
            return self.seg == other.seg
        elif isinstance(other, str):
            return self.seg == other
        else:
            raise TypeError('Please compare with another song or an audio seg!')

    def __hash__(self):
        return hash((self.seg,))