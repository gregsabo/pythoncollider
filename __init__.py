import timeflow
import random
import math

def freq(midi):
	return 440 * math.pow(2, float(midi - 57) / 12)

def randpop(in_list):
    return in_list.pop(random.randrange(0,len(in_list))) 
