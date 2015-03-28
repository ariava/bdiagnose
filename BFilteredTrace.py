from Queue import *
import re

class BFilteredTrace:
	__regexp_file_path = None
	__trace_file_path = None

	__regexps = {}

	def __init__(self, trace_file_path, regexp_file_path):
		if (isinstance(trace_file_path, str) == False):
			raise TypeError("Trace file path must be specified as string.")
		if (trace_file_path == ""):
			raise ValueError("Trace file path must not be empty.")
		if (isinstance(regexp_file_path, str) == False):
			raise TypeError("Regexp file path must be specified as string.")
		if (regexp_file_path == ""):
			raise ValueError("Regexp file path must not be empty.")
		self.__trace_file_path = trace_file_path
		self.__regexp_file_path = regexp_file_path
		try:
			self.__register_regexps(self.__regexp_file_path)
		except IOError as e:
			print e

	# Regexp handling functions

	def __register_regexps(self, input_file_path):
		try:
			input_file = open(input_file_path)
		except Exception as e:
			raise IOError("Cannot open file " + input_file_path)
		for line in input_file:
			result = re.search("(\S+)(\s+)\"(.+)\"", line)
			if result:
				self.__regexps[result.group(1)] = result.group(3)
		input_file.close()

	def get_regexp(self, keyword):
		if keyword in self.__regexps:
			return self.__regexps[keyword]
		else:
			return ".*" + keyword + ".*"

	def get_tracename(self):
		return self.__trace_file_path

	# Filter

	def filter(self, filters):
		filtered_list = []
		trace_file = open(self.__trace_file_path)
		for line in trace_file:
			# Discard comments
			if re.match(self.get_regexp("comment"), line):
				continue
			# Get desired lines
			for filter in filters:
				if filter == "sched_msg" and len(filters) > 1:
					continue
				if re.search(self.get_regexp(filter), line) and line not in filtered_list:
					filtered_list.append(line)
		trace_file.close()
		return filtered_list
