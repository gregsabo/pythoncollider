class MusicNode(object):
    global_keys = {}
    def __init__(self, *args, **kwargs):
        print "Creating MusicNode:", self.__class__.__name__
        self.enabled = True
        
        if hasattr(self, "init"):
            self.init(*args)
        self.holding = []
    
    def get_subdiv(self):
        if hasattr(self, 'subdiv'):
            return self.subdiv
        elif hasattr(self.__class__, 'subdiv'):
            return self.__class__.subdiv
        else:
            return 1

    def release_all(self, beat):
        """
        Release all holding synths at beat.
        This is called automatically at the end of a sequence.
        """

        for holding in self.holding:
            holding.set_at(beat.time, gate=0)
        self.holding = []
