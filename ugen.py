import OSC
import loader
from timeflow import Synth, Group

# TODO: this will break for long notes
def bus_generator(max_busnum):
    current = 20
    while True:
        yield current
        current += 1
        if current >= max_busnum:
            current = 20
audio_busnum = bus_generator(1024)
control_busnum = bus_generator(1024)

class Ugen(object):
    """
    Controls a SynthDef containing a single Ugen on the 
    SuperCollider server
    """
    def __init__(self, **kwargs):
        classname = self.__class__.__name__
        object.__setattr__(self, 'name', "Ugen_" + classname)
        object.__setattr__(self, "_touched_keys", set(kwargs.keys()))
        object.__setattr__(self, '_params', kwargs)
        object.__setattr__(self, 'group', None)
        object.__setattr__(self, '_synth', None)

    def set(self, key=None, value=None, **kwargs):
        if key and (value is not None):
            self._touched_keys.add(key)
            self._params[key] = value
        for key, value in kwargs.iteritems():
            self._touched_keys.add(key)
            self._params[key] = value
        return self

    def __setattr__(self, key, value):
        self._touched_keys.add(key)
        self._params[key] = value

    def __getattr__(self, key):
        return self._params.get(key)

    def __delattr__(self, key):
        if key in self._params:
            del self._params[key]

    def __add__(self, rhs):
        return Add(in_bus=self, rhs=rhs)

    def __mul__(self, rhs):
        return Mul(in_bus=self, rhs=rhs)

    def params(self, testfunc=None):
        if not testfunc:
            return self._params.copy()
        out = {}
        for param, value in self._params.iteritems():
            if testfunc(value):
                out[param] = value
        return out

    def links(self):
        testfunc = lambda x: isinstance(x, Ugen)
        return self.params(testfunc)

    def values(self):
        testfunc = lambda x: not isinstance(x, Ugen)
        return self.params(testfunc)
    
    def osc_map_message_key(self):
        """
        subclasses should return '/n_map' or '/n_mapa'
        depending on whether their output is control-rate
        or audio-rate, respectively
        """
        raise NotImplementedError

    def play_at(self, start_time):
        """
        See the play_at method for Synth objects.
        """
        messages = []

        is_new_root = bool(not self.group and not self._synth)
        if is_new_root:
            object.__setattr__(self, 'group', Group())

        self.claim(messages=messages, group=self.group, visited=set([]))
        if is_new_root:
            self._synth.set(out_bus=0)
        messages.insert(0, self._synth)

        if is_new_root:
            messages.insert(0, self.group.get_message())

        bundle = OSC.OSCBundle()
        bundle.setTimeTag(start_time)

        for m in messages:
            if isinstance(m, Synth):
                m = m.get_message()
            if m:
                bundle.append(m)

        # TODO: decent logging
        #print 'bundle:', bundle
        loader.client.send(bundle)
        return self

    def claim(self, messages, group, visited):
        """
        Recursively create a OSC message for each
        element in the graph, assigning busses
        to make connections.
        """
        if self in visited:
            return self._synth

        if self.osc_map_message_key() == '/n_mapa':
            chosen_busnum = audio_busnum.next()
        else:
            chosen_busnum = control_busnum.next()

        # clear this bus in case another Synth wrote to it
        #clear_synth = Synth('builder-clear', out_bus=chosen_busnum)
        #clear_synth.add_action = 0
        #messages.insert(0, clear_synth)

        if not self._synth:
            object.__setattr__(self, '_synth', Synth(self.name, group))
            self._synth.set(out_bus=chosen_busnum)
        else:
            print 'visited again:', self, self._touched_keys
        self._synth.add_action = 0
        values = self.values()
        for key in self._touched_keys:
            if key not in values:
                continue
            self._synth.set(**{key:values[key]})

        for name, linked_element in self.links().items():
            linked_synth = linked_element.claim(messages, group, visited | set([self]))
            if name in self._touched_keys:
                if name.startswith('in_bus'):
                    self._synth.set(in_bus=linked_synth.get('out_bus'))
                else:
                    map_message = OSC.OSCMessage(linked_element.osc_map_message_key())
                    map_message.append([self._synth.node_id, name, linked_synth.get('out_bus')])
                    messages.append(map_message)
                    #messages.insert(0, map_message)
                if linked_synth in messages:
                    messages.remove(linked_synth)
            messages.insert(0, linked_synth)
            #messages.append(linked_synth)

        self._touched_keys.clear()
        return self._synth

    def bus_map_message(self, node_id, name, in_bus):
        message = OSC.OSCMessage(self.osc_map_message_key())
        message.append([node_id, name, in_bus])
        return message

class AudioUgen(Ugen):
    def osc_map_message_key(self):
        return '/n_mapa' 
class ControlUgen(Ugen):
    def osc_map_message_key(self):
        return '/n_map'


class Add(AudioUgen): pass
class Mul(AudioUgen): pass
class SinOsc(AudioUgen): pass
class Saw(AudioUgen): pass
class LPF(AudioUgen): pass
class Env(ControlUgen): pass
class EnvPerc(ControlUgen): pass
