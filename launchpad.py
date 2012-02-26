import pypm
from time_management import sequencer

OUTPUT_LATENCY = 0

COLORS = {
	"low-red":0x0D,
	"red":0x0F,
	"low-amber":0x1D,
	"amber":0x3E,
	"yellow":0x3E,
	"low-green":0x1C,
	"green":0x3C,
	"off": 0x00
}

class Launchpad(object):
	
	def __init__(self):
		"""Initialize MIDI"""
		pypm.Initialize()
		input_num, output_num = self.find_device_num()
		self.input = pypm.Input(input_num)
		self.output = pypm.Output(output_num, OUTPUT_LATENCY)
		#reset the launchpad hardware
		self.output.Write([[[176, 0, 0], 0]])
		
		self.previous_lights = ["red" for i in range(0, 64)]
		self.light_up(["off" for i in range(0, 64)])
	
	def read_input(self):
		events = []
		
		while self.input.Poll():
			in_message = self.input.Read(1)
			for item in in_message:
				events.append(LaunchpadEvent(item))

		return events
	
	def light_diff(self, new_states):
		diff = []
		for prev, new in zip(self.previous_lights, new_states):
			if prev is new:
				diff.append(None)
			else:
				diff.append(new)
		
		self.previous_lights = new_states
		return diff
	
	def light_up(self, new_states):
		if len(new_states) != 64:
			raise Exception("Launchpad needs exactly 64 states. Given %s." % str(len(new_states)))
		
		diff = self.light_diff(new_states)
			
		for row_num in range(0, 8):
			for col_num in range(0, 8):
				light_state = diff[(col_num * 8) + row_num]
				if light_state != None:
					velocity = COLORS[light_state]
					note_num = 16 * row_num + col_num
					self.output.Write([[[0x90, note_num, velocity], 0]])
	
	def find_device_num(self):
		device_count = pypm.CountDevices()
		device_index = 0
		while device_index < device_count:
			device_info = pypm.GetDeviceInfo(device_index)
			print device_info
			if device_info[1] == "Launchpad":
				if device_info[2] == 1:
					input_num = device_index
				elif device_info[3] == 1:
					output_num = device_index
			device_index += 1
		return (input_num, output_num)

class LaunchpadEvent(object):
	def __init__(self, in_message):
		if in_message[0][2] == 0:
			self.event_type = "note_off"
		else:
			self.event_type = "note_on"
		
		self.note = in_message[0][1]
	
	def is_a_push(self):
		return self.event_type == "note_on"
	
	def is_a_release(self):
		return self.event_type == "note_off"
	
	def get_column(self):
		return self.note % 16
		
	def get_row(self):
		return int(self.note / 16)
	
	def get_location(self):
		return self.get_row(), self.get_column()
