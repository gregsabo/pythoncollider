import time
import OSC
import os
import random

from sched import scheduler
import loader

class TempoClock(object):
    """
    Converts between beats and timestamps.
    """
    
    def __init__(self, start_time = None, bpm = 120):
        self.bpm = bpm
        self.start_time = start_time
        if (self.start_time == None):
            self.start_time = time.time()
                    
    def beats_in(self, span, subdiv=1):
        beats = []
            
        if(span["bottom"] < self.start_time):
            return beats
        
        seconds_per_beat = float(60) / self.bpm / subdiv
        seconds_elapsed = span["bottom"] - self.start_time
        beats_elapsed = seconds_elapsed / seconds_per_beat
        if(beats_elapsed % 1 is not 0):
            beats_elapsed = int(beats_elapsed) + 1
        
        current_beat = beats_elapsed * seconds_per_beat + self.start_time

        while(current_beat <= span["top"]):
            beats.append(Beat(current_beat, beats_elapsed))
            current_beat = current_beat + seconds_per_beat
        
        return beats
    
    def beat_at(self, num=None, time=None):
        seconds_per_beat = float(60) / self.bpm

        if time:
            out_num = (time - self.start_time) / seconds_per_beat
            return Beat(time, out_num)

        beattime = seconds_per_beat * num + self.start_time
        return Beat(beattime, num)
        
        
class Beat(object):
    def __init__(self, time, num):
        self.time = time
        self.num = num

def synth_nodes():
    i = 0
    while True:
        i = i + 1
        yield i

synth_nodes = synth_nodes()

class Group(object):
    def __init__(self):
        self.group_id = synth_nodes.next()

    def get_message(self):
        message = OSC.OSCMessage("/g_new")
        message.append([self.group_id, 1, 0])
        return message

    def create_at(self, start_time):
        bundle = OSC.OSCBundle()
        bundle.setTimeTag(start_time)
        message = OSC.OSCMessage("/g_new")
        message.append([self.group_id, 1, 0])
        bundle.append(message)
        loader.client.send(bundle)

        return self

class Synth(object):
    """
    Representation of a SuperCollider Synth.
    Its attributes are determined by the synthdefs file.
    """
    
    def __init__(self, name, group=None, **kwargs):
        self.synth_name = name
        self.node_id = None
        self.arg_dict = {}
        self.set(**kwargs)
        self.add_action = 1
        self.group = group
        self.node_id = synth_nodes.next()
        self.has_played = False

    def set(self, **kwargs):
        for key in kwargs:
            self.arg_dict[key] = kwargs[key]

    def get(self, key):
        return self.arg_dict.get(key)
    
    def set_at(self, time, **kwargs):
        bundle = OSC.OSCBundle()
        bundle.setTimeTag(time)
        for key in kwargs:
            message = OSC.OSCMessage("/n_set")
            message.append(self.node_id)
            message.append([key, kwargs[key]])
            bundle.append(message)
        print 'setting:', self.node_id
        loader.client.send(bundle)
            
    
    def args_as_list(self):
        args_list = []
        for key in self.arg_dict:
            args_list.append(key)
            args_list.append(self.arg_dict[key])
        return args_list
    
    def get_message(self):
        message = None
        if self.has_played:
            if not self.arg_dict:
                return None
            message = OSC.OSCMessage("/n_set")
            message.append(self.node_id)
            for key in self.arg_dict:
                message.append([key, self.arg_dict[key]])
            print 'setting:', self.node_id
        else:
            message = OSC.OSCMessage("/s_new")
            target_id = 0
            if self.group:
                target_id = self.group.group_id
            message.append([self.synth_name, self.node_id, 
                self.add_action, target_id])
            message.append(self.args_as_list())
            self.has_played = True
        self.arg_dict = {}
        return message
    
    def play_at(self, start_time):
        if self.has_played:
            return self.set_at(start_time)
        bundle = OSC.OSCBundle()
        bundle.setTimeTag(start_time)
        message = OSC.OSCMessage("/s_new")
        self.node_id = synth_nodes.next()
        target_id = 0
        if self.group:
            target_id = self.group.group_id
        message.append([self.synth_name, self.node_id, 
            self.add_action, target_id])
        message.append(self.args_as_list())
        bundle.append(message)
        loader.client.send(bundle)
        self.has_played = True
        return self
    
    def release(self):
        message = OSC.OSCMessage("/n_free")
        message.append([self.node_id])
        loader.client.send(message)


class AutomatorPool(object):
    """
    An automator is a generator function which
    yields beats. The automator expects to be
    invoked before that beat is planned,
    but after any previous beats are planned.
    """
    
    def __init__(self):
        self.automators = []
        self.next = {'next_time':float("inf")}

    def add(self, automator):
        generator = automator()
        self.automators.append({
            'generator':generator,
            'next_time':generator.next().time
        })
        self.next = self.find_next()
        
    def find_next(self):
        soonest = {'next_time':float("inf")}
        for automator in self.automators:
            if automator['next_time'] < soonest['next_time']:
                soonest = automator
        return soonest

    def step(self):
        auto = self.next
        self.automators.remove(auto)
        if not auto['generator']:
            return
        self.next = self.find_next()
        
        try:
            next_beat = auto['generator'].next()
        except StopIteration:
            pass
        else:
            self.automators.append({
                'generator':auto['generator'],
                'next_time':next_beat.time
            })
        finally:
            self.next = self.find_next()


class Sequencer(object):
    """
    A Seqeuncer has a list of MusicNodes,
    and it periodically calls plan() on each
    of the nodes if their enabled attribute is True.
    """
    
    def __init__(self, clock=None):
        self.nodes = []
        self.automators = AutomatorPool()
        self.buffer_length = 0.1
        self.sched = scheduler(time.time, time.sleep)
        self.default_clock = clock or TempoClock()
        self._stopped = False
    
    
    def on_wake(self):
        next_sleep = self.last_sleep + self.buffer_length
        bottom = self.last_sleep

        while self.automators.next['next_time'] < next_sleep:
            span = {
                'bottom': bottom,
                'top': self.automators.next['next_time']
            }

            self.notify_nodes(span)
            self.automators.step()
            bottom = span['top']
        
        if self._stopped:
            print "Sequencer stopped!"
            return

        span = {
            'bottom': bottom,
            'top': next_sleep
        }

        self.notify_nodes(span)
        
        self.sched.enterabs(self.last_sleep, 1, self.on_wake, ())
        self.last_sleep = next_sleep
    
    def notify_nodes(self, span):
        for node in self.nodes:
            if hasattr(node, "read_input"):
                node.read_input()

            if not hasattr(node, "plan"):
                continue
            
            if not node.enabled:
                return
            
            for beat in self.default_clock.beats_in(span, subdiv=node.get_subdiv()):
                node.plan(beat)
    
    def run(self):
        self.last_sleep = time.time() + self.buffer_length
        self.on_wake()
        self.sched.run()

    def stop(self):
        last_beat = self.last_sleep + self.buffer_length
        beat = self.default_clock.beat_at(time=last_beat)
        beat.num = int(beat.num)
        print 'last beat~!', beat.num, beat.time
        for node in self.nodes:
            node.release_all(beat)
        self._stopped = True

current_bufnum = 5
def read_buffer(filename, channels=1):
    global current_bufnum

    if filename.endswith(".mp3"):
        filename = decode_mp3(filename)
    
    current_bufnum += channels
    message = OSC.OSCMessage("/b_allocRead")
    message.append(current_bufnum)
    message.append(filename)
    loader.client.send(message)
    return current_bufnum

def decode_mp3(filename):
    new_filename = "/tmp/" + str(random.randint(0, 100000000)) + ".wav"
    command = "ffmpeg -i " + filename + ' ' + new_filename
    print "Converting to WAV:", command
    os.system(command)
    return new_filename

sequencer = Sequencer()
