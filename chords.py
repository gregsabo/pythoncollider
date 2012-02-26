from nodes import MusicNode

note_map = {
    'c': 0,
    'cis': 1,
    'des': 1,
    'd': 2,
    'dis': 3,
    'ees': 3,
    'e': 4,
    'f': 5,
    'fis': 6,
    'ges': 6,
    'g': 7,
    'gis': 8,
    'aes': 8,
    'a': 9,
    'ais': 10,
    'bes':10,
    'b':11
}

num_map = {}
for note, num in note_map.items():
    num_map[num] = note

class Chord(object):
    def __init__(self, root, mode="major"):
        if isinstance(root, basestring):
            root = note_map[root]
        self.root = root
        self.mode = mode
    
    def __str__(self):
        return str(num_map[self.root]) + ' ' + self.mode
    
    def get_root(self):
        return ScaleDegree(1, self.root, self.mode)

class ChordProgression(object):
    def __init__(self):
        self.progression = []
    
    def add(self, chord, length):
        self.progression.append((chord, length))
    
    def parse(self, instring):
        """
        emptys the progression and refills it with
        one described in the string.
        
        Format: space separated root-mode pairings.
        Example:
        'c-minor g-minor aes-major f-major'
        """
        self.progression = []
        for chordstr in instring.split(" "):
            items = chordstr.split("-")
            root = items[0]
            mode = items[1]
            if len(items) == 3:
                length = int(items[2])
            else:
                length = 4
            chord = Chord(root, mode)
            self.add(chord, length)

        #make chainable
        return self
    
    def total_length(self):
        total = 0
        for chord in self.progression:
            total += chord[1]
        return total
    
    def chord_for_beat(self, beat):
        beatnum = beat.num % self.total_length()
        for chord in self.progression:
            chordlength = chord[1]
            beatnum -= chordlength
            if beatnum <= 0:
                return chord[0]
        return self.progression[-1][0]

class ChordEmitter(MusicNode):
    def init(self, progression):
        if isinstance(progression, basestring):
            self.prog = ChordProgression()
            self.prog.parse(progression)
        else:
            self.prog = progression
        self.current_chord = self.prog.progression[0][0]

    subdiv = 1
    def plan(self, beat):
        self.current_chord = self.prog.chord_for_beat(beat)

class ScaleDegree(object):
    degree_map = {
        0:0,
        1:2,
        2:4,
        3:5,
        4:7,
        5:9,
        6:11
    }
    def __init__(self, num, root=0, mode=0):
        self.num = min(num, 70)
        
        if isinstance(root, basestring):
            root = note_map[root]
        self.root = root
        
        if isinstance(mode, basestring):
            if mode == 'major':
                mode = 0
            else:
                mode = 1
        self.mode = mode
    
    def __eq__(self, other):
        if not isinstance(other, ScaleDegree):
            return False
        return self.num == other.num and self.root == other.root and self.mode == other.mode
    
    
    def get_pitch(self):
        DEGREES_PER_OCTAVE = 7
        if self.mode == 1:
            degree = (self.num - 2 - 1) 
            wrapped_degree = degree % DEGREES_PER_OCTAVE
            pitch = ScaleDegree.degree_map[wrapped_degree] + 3
        else:
            degree = (self.num - 1) 
            wrapped_degree = degree % DEGREES_PER_OCTAVE
            pitch = ScaleDegree.degree_map[wrapped_degree]
            
        octave = int(degree / DEGREES_PER_OCTAVE)
        pitch += 12 * octave
        return pitch + self.root
    
    def pitch_class(self):
        return self.pitch() % 12
    
    def translate(self, amount):
        return ScaleDegree(self.num+amount, self.root, self.mode)
        
