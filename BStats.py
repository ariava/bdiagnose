from BGraphViewer import *
import re

class BStats:
	__tracefile = None
	__mask = None
	__submask = None
	__val_list = None
	__avg_list = None
	
	def __init__(self, tracefile, mask, submask):
		if (isinstance(tracefile, str) == False):
			raise TypeError("Trace file must be specified as string.")
		if (tracefile == ""):
			raise ValueError("Trace file must not be empty.")
		if (isinstance(mask, str) == False):
			raise TypeError("Mask must be specified as string.")
		if (mask == ""):
			raise ValueError("Mask string must not be empty.")
		if (isinstance(submask, str) == False):
			raise TypeError("Submask must be specified as string.")
		if (submask == ""):
			raise ValueError("Submask string must not be empty.")
		self.__tracefile = tracefile
		self.__mask = mask
		self.__submask = submask

	def get_submask_values(self):
		self.__val_list = []
		try:
			trace = open(self.__tracefile)
		except Exception as e:
			raise IOError("Cannot open file" + self.__tracefile)
		for line in trace:
			result = re.search(self.__mask, line)
			if result:
				subresult = re.search(self.__submask, line)
				if subresult:
					self.__val_list.append(float(subresult.group(1)))
		return self.__val_list

	def get_simple_moving_average(self, num_values):
		if (isinstance(num_values, int) == False):
			raise TypeError("Num_values parameter must be an integer.")
		self.__avg_list = []
		if self.__val_list is None or self.__val_list == [] or len(self.__val_list) < num_values:
			return self.__avg_list
		pos = 0 
		self.__avg_list = []
		while pos + num_values < len(self.__val_list):
			counter = 0
			sum_val = 0
			while counter < num_values:
				sum_val = sum_val + self.__val_list[pos + counter]
				counter = counter + 1
			self.__avg_list.append(float(sum_val / num_values))
			pos = pos + 1
		return self.__avg_list

	def draw_stats(self):
		if self.__val_list is None or self.__avg_list is None:
			print "ERROR: function draw_stats was called with none data lists"
			return False
		try:
			BGraphViewer(range(len(self.__val_list)), self.__val_list, \
				     range(len(self.__avg_list)), self.__avg_list, \
				     self.__mask + self.__submask)
		except Exception as e:
			print str(e)
			return False
		else:
			return True
