from BFilteredTrace import *
import re, os.path

class BDiagnoser:
	__this_instance = None
	__filtered_trace = None
	__commands_file_path = None

	__commands_rexp = {}

	def __init__(self, filtered_trace, commands_file_path):
		if (isinstance(filtered_trace, BFilteredTrace) == False):
			raise TypeError("Filtered trace must be a BFilteredTrace.")
		if (filtered_trace == None):
			raise ValueError("Filtered trace is a mandatory parameter.")
		if (isinstance(commands_file_path, str) == False):
			raise TypeError("Commands file path must be given as string.")
		if (commands_file_path == ""):
			raise ValueError("Commands file path must not be empty.")
		self.__filtered_trace = filtered_trace
		self.__commands_file_path = commands_file_path
		try:
			self.__register_commands(self.__commands_file_path)
		except IOError as e:
			print e

	def __register_commands(self, input_file_path):
		try:
			input_file = open(input_file_path)
		except Exception as e:
			raise IOError("Cannot open file " + input_file_path)
		for line in input_file:
			result = re.search("(\S+)(\s+)(\S+)", line)
			if result:
				self.__commands_rexp[result.group(1)] = result.group(3)
		input_file.close()

	def __get_command_re(self, keyword):
		if keyword in self.__commands_rexp:
			return self.__commands_rexp[keyword]
		else:
			return None

	def __get_command_from_re(self, re):
		return [k for k, v in self.__commands_rexp.iteritems() if v == re][0]

	def __get_function_name(self, key):
		return "_BDiagnoser__" + key

	# Command-specific functions

	def __and(self, command_result, trace_file):
		trespassed = 0
		first = str(command_result.group(1))
		second = str(command_result.group(2))
		print "*** Diagnosing:", first, "needs", second, "***"
		for tline in trace_file:
			if re.search(self.__filtered_trace.get_regexp(first), tline) and not \
			   re.search(self.__filtered_trace.get_regexp(second), tline):
				print "WARN: second action does not exist in line"
				print tline
				trespassed += 1
		return trespassed

	def __and_not(self, command_result, trace_file):
		trespassed = 0
		first = str(command_result.group(1))
		second = str(command_result.group(2))
		print "*** Diagnosing: when", first, "not", second, "***"
		for tline in trace_file:
			if re.search(self.__filtered_trace.get_regexp(first), tline) and \
			   re.search(self.__filtered_trace.get_regexp(second), tline):
				print "WARN: both actions match in line"
				print tline
				trespassed += 1
		return trespassed

	def __unique_from_to(self, command_result, trace_file):
		trespassed = 0
		key_regexp = str(command_result.group(1))
		first = str(command_result.group(2))
		second = str(command_result.group(3))
		interval = float(command_result.group(4))
		print "*** Diagnosing: unique", key_regexp, "from", first, "to", second, "MAX", interval, "seconds ***"
		queue_dict = {}
		for tline in trace_file:
			# Restrict results to lines that match the key regexp (make sure there is a unique identifier)
			key_result = re.search(key_regexp, tline)
			if key_result == None:
				key = None
				continue
			else:
				key = key_result.group(1)
			start_result = re.search(self.__filtered_trace.get_regexp(first), tline)
			# We found a first action, we queue it
			if start_result:
				# If there is no FIFO for this unique identifier (it is the first time we
				# encounter it), create one
				if key not in queue_dict:
					queue_dict[key] = Queue()
				queue_dict[key].put(tline)
			end_result = re.search(self.__filtered_trace.get_regexp(second), tline)
			# We found a second action, we get a first action from the FIFO associated
			# to the unique identifier and we assume it is the corresponding one.
			# If there is no queue for the unique identifier, we assume we stumbled into
			# a lone second action and we do nothing.
			if end_result and key is not None and key in queue_dict and not queue_dict[key].empty():
				start_act = queue_dict[key].get()
				end_act = tline
				start_time_obj = re.search(self.__filtered_trace.get_regexp("timestamp"), start_act)
				if not start_time_obj:
					trace_file.close()
					directives_file.close()
					raise IOError("FATAL: no timestamp found in start action; aborting.")
				end_time_obj = re.search(self.__filtered_trace.get_regexp("timestamp"), end_act)
				if not end_time_obj:
					trace_file.close()
					directives_file.close()
					raise IOError("FATAL: no timestamp found in end action; aborting.")
				start_time = float(start_time_obj.group(2))
				end_time = float(end_time_obj.group(2))
				if (end_time - start_time) > interval:
					print "WARN: action began at", start_time, "and ended at", end_time
					print "WARN: action took", (end_time - start_time), "seconds"
					print start_act
					print end_act
					trespassed += 1
				queue_dict[key].task_done()
		# Here there may be unmatched first actions, which implies no error
		return trespassed

	def __from_to(self, command_result, trace_file):
		trespassed = 0
		first = str(command_result.group(1))
		second = str(command_result.group(2))
		interval = float(command_result.group(3))
		print "*** Diagnosing: from", first, "to", second, "MAX", interval, "seconds ***"
		q = Queue()
		for tline in trace_file:
			start_result = re.search(self.__filtered_trace.get_regexp(first), tline)
			# We found a first action, we queue it
			if start_result:
				q.put(tline)
			end_result = re.search(self.__filtered_trace.get_regexp(second), tline)
			# We found a second action, we get a first action from the FIFO and
			# we assume it is the corresponding one.
			# There is nothing queued --> we stumbled into a lone second action.
			if end_result and not q.empty():
				start_act = q.get()
				end_act = tline
				start_time_obj = re.search(self.__filtered_trace.get_regexp("timestamp"), start_act)
				if not start_time_obj:
					trace_file.close()
					directives_file.close()
					raise IOError("FATAL: no timestamp found in start action; aborting.")
				end_time_obj = re.search(self.__filtered_trace.get_regexp("timestamp"), end_act)
				if not end_time_obj:
					trace_file.close()
					directives_file.close()
					raise IOError("FATAL: no timestamp found in end action; aborting.")
				start_time = float(start_time_obj.group(2))
				end_time = float(end_time_obj.group(2))
				if (end_time - start_time) > interval:
					print "WARN: action began at", start_time, "and ended at", end_time
					print "WARN: action took", (end_time - start_time), "seconds"
					print start_act
					print end_act
					trespassed += 1
				q.task_done()
		# Here there may be unmatched first actions, which implies no error
		return trespassed

	def __between(self, command_result, trace_file):
		trespassed = 0
		left = str(command_result.group(2))
		right = str(command_result.group(3))
		middle = str(command_result.group(1))
		print "*** Diagnosing:", middle, "between", left, "and", right, "***" 
		left_found = right_found = middle_found = False
		left_line = right_line = middle_line = ""
		for tline in trace_file:
			# Mark the first action in the sequence (the "left" one)
			left_obj = re.search(self.__filtered_trace.get_regexp(left), tline)
			if left_obj != None:
				left_found = True
				left_line = tline
			# Count the second action only if the left action has been found
			middle_obj = re.search(self.__filtered_trace.get_regexp(middle), tline)
			if middle_obj != None and left_found == True:
				middle_found = True
				middle_line = tline
			# Count the third action only if the left action has been found
			right_obj = re.search(self.__filtered_trace.get_regexp(right), tline)
			if right_obj != None and left_found == True:
				right_found = True
				right_line = tline
			# Make sure we did not match more than one action in the same line (would be weird)
			if (left_obj and middle_obj) or (left_obj and right_obj) or (middle_obj and right_obj):
				raise IOError("FATAL: more than one action matches; aborting.")
			# Check if we found the first and last action without the middle one
			if left_found and right_found and not middle_found:
				print "WARN: action"
				print right_line
				print "occurred without action", middle
				print "after action"
				print left_line
				trespassed +=1
				left_found = right_found = middle_found = False
			if left_found and right_found and middle_found:
				left_found = right_found = middle_found = False
		return trespassed

	def __after(self, command_result, trace_file):
		trespassed = 0
		first = str(command_result.group(2))
		second = str(command_result.group(1))
		first_found = second_found = False
		first_line = ""
		print "*** Diagnosing: always", second, "after", first, "***"
		for tline in trace_file:
			first_obj = re.search(self.__filtered_trace.get_regexp(first), tline)
			if first_obj != None:
				if first_found == False:
					# Beginning of sequence: we found a first action
					first_found = True
					first_line = tline
				else:
					# We found another first action, check whether
					# the second action has been found
					if second_found == True:
						# Just reset second_found, we already
						# have another first action
						second_found = False
					else:
						# Here be lions
						print "WARN: action", first, "occurred twice"
						print first_line
						print tline
						trespassed += 1
						# Reset first_found, we're just interested
						# in action pairs
						first_found = False
						first_line = tline
			second_obj = re.search(self.__filtered_trace.get_regexp(second), tline)
			if second_obj != None:
				second_found = True
		return trespassed

	# Diagnoser

	def diagnose(self, directives_file_path):
		if (isinstance(directives_file_path, str) == False):
			raise TypeError("Directives file path must be given as string.")
		if (directives_file_path == ""):
			raise ValueError("Directives file path must not be empty.")
		# Test trace file existence
		trace_file_path = self.__filtered_trace.get_tracename()
		if not os.path.exists(trace_file_path):
			raise IOError("Unable to find file " + trace_file_path)
		# Body of function
		trespassed = 0
		directives_file = open(directives_file_path)
		for line in directives_file:
			# Skip comments
			comment_result = re.search(self.__filtered_trace.get_regexp("comment"), line)
			if comment_result:
				continue
			# Evaluate single commands
			for command_key in self.__commands_rexp.keys():
				result = re.search(self.__get_command_re(command_key), line)
				if result:
					trace_file = open(trace_file_path)
					trespassed += eval("self." + self.__get_function_name(command_key))(result, trace_file)
					trace_file.close()
		print "*** Found", trespassed, "non-compliances ***"
		directives_file.close()
		return 0

