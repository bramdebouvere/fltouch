class TrackManager:
    def __init__(self, trackCount: int = 0, firstTrack: int = 0):
        self._trackCount = trackCount
        self._firstTrack = firstTrack

    @property
    def TrackCount(self) -> int:
        """ Returns the total number of tracks that we can bank trough """
        return self._trackCount
    
    @property
    def FirstTrack(self) -> int:
        """ The index of the first track that will be displayed on the Xtouch """
        return self._firstTrack
    
    @FirstTrack.setter
    def FirstTrack(self, value: int):
        self._firstTrack = value
        
    

    