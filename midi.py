import OSC

class OSCTimeoutSignal(Exception): pass

class OSCTimeoutServer(OSC.OSCServer):
    """
    Raise timeout signals so that users can tell
    when there are no messages to read.
    """
    def handle_timeout(self):
        OSC.OSCServer.handle_timeout(self)
        raise OSCTimeoutSignal

class MIDIOsc(object):
    """
    A OSC server designed to recieve
    midi-like messages from keyboard instruments
    (probably converted via OSCulator).
    
    Create an instance, add callbacks to
    either note_handlers or noteon_handlers.
    """
    
    def __init__(self, ip='127.0.0.1', port=57111, osc_address='midi/note/1'):
        self.ip = ip
        self.port = port
        self.osc_address = osc_address
        
        self.noteon_handlers = []
        self.note_handlers = []
        self.server = None
    
    def connect(self):
        """
        Initialize the server. Calling this is optional,
        but may be useful if connecting is likely to
        produce errors.
        """
        self.server = OSCTimeoutServer((self.ip, self.port))
        self.server.timeout = 0.01
        self.server.addMsgHandler(self.osc_address, self._osc_recieve)
    
    def _osc_recieve(self, address, format, message, hostport):
        pitch = int(128 * message[0])
        vel = message[1]
        on = bool(message[2])
        
        if on:
            for handler in self.noteon_handlers:
                handler(pitch, vel)
        for handler in self.note_handlers:
            handler(pitch, vel, on)
    
    def handle(self):
        """
        Handle all buffered messages and return.
        """
        if not self.server:
            self.connect()
        while 1:
            try:
                self.server.handle_request()
            except OSCTimeoutSignal:
                return
    
    def run(self):
        """
        Block execution and handle
        requests forever.
        """
        if not self.server:
            self.connect()
        self.server.serve_forever()