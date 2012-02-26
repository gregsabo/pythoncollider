import random
from pysc.time_management import Synth
from nodes import MusicNode
from time_management import read_buffer

class Pattern(object):
    def __init__(self, pattern):
        self.pattern = pattern
        
    def note_for(self, beat):
        index = beat.num % len(self.pattern)
        return self.pattern[index]

class ProbabilityPattern(object):
    def __init__(self, weights):
        if isinstance(weights, basestring):
            self.weights = []
            for item in weights.split(" "):
                self.weights.append(float(item))
        else:
            self.weights = weights
        
        self.generate()
    
    def tweak_weights(self, amount=0.2):
        old = self.weights
        self.weights = []
        for weight in old:
            if weight < 0 or weight > 1:
                self.weights.append(weight)
                continue
            new = weight + (random.random() * amount - (amount / 2))
            self.weights.append(new)
    
    def generate(self):
        self.pattern = []
        for item in self.weights:
            if random.random() < item:
                new_dict = {'velocity':item}
            else:
                new_dict = None
            self.pattern.append(new_dict)
    
    def note_for(self, beat):
        index = beat.num % len(self.pattern)
        note = self.pattern[index]
        if index == len(self.pattern) - 1:
            self.generate()
        return note
    

class PatternReader(object):
    def __init__(self, filename):
        in_file = open(filename, "r")
        self.patterns = []
        for line in in_file:
            pattern = []
            for char in line:
                if char == '0':
                    pattern.append(True)
                else:
                    pattern.append(False)
            self.patterns.append(pattern)
        print self.patterns
    
    def num(self, num):
        return Pattern(self.patterns[num-1])


class PatternPlayer(MusicNode):
    def init(self, weights, filename, subdiv=4):
        self.bufnum = read_buffer(filename)
        self.pattern = ProbabilityPattern(weights)
        self.subdiv = subdiv
        self.freq = 10000
        self.amp = 1
        self.out_bus = 0
    
    def plan(self, beat):
        note = self.pattern.note_for(beat)
        if not note:
            return
            
        synth = Synth("SampleHit")
        synth.set(bufnum=self.bufnum)
        synth.set(amp=self.amp * note.get('velociy', 1))
        synth.set(freq=self.freq)
        synth.set(out_bus=self.out_bus)
        synth.play_at(beat.time)