#!/usr/bin/python
# Main file for bdiagnose v0.01

from BFilteredTrace import *
from BDiagnoser import *
from BStats import *
import os.path, sys, gtk
from pyx import *
# XXX optparse is deprecated, switch to argparse asap
from optparse import OptionParser

usage = "USAGE: %prog [options] arg"
parser = OptionParser(usage)
parser.add_option("-p", "--plot", action="store_const", const="plot", dest="behaviour",
			help="specify plotting behaviour")
parser.add_option("-m", "--mask", action="store", type="string", dest="mask",
			help="if plotting is enabled, specify mask")
parser.add_option("-s", "--submask", action="store", type="string", dest="submask",
			help="if plotting is enabled, specify submask")
parser.add_option("-t", "--threshold", action="store", type="int", dest="sma_values",
			help="if plotting is enabled, specify min number of values to draw SMA")
parser.add_option("-o", "--output", action="store", type="string", dest="plot_file",
			help="if plotting is enabled, specify an identifier for the output files")
parser.add_option("-d", "--diagnose", action="store_const", const="diagnose", dest="behaviour",
			help="specify diagnoser behaviour")
parser.add_option("-c", "--commands", action="store", type="string", dest="directives_file_path",
			help="if diagnoser is enabled, specify directives file path")
parser.add_option("-f", "--filter", action="append", type="string", dest="filters",
			help="add a filter (will be used if no other behaviour is specified)")

(options, args) = parser.parse_args()
if len(args) != 1:
	parser.error("incorrect number of arguments")
# File pointers
input_file_path = sys.argv[1]
directives_file_path = options.directives_file_path

# Options
filters = options.filters
behaviour = options.behaviour
mask = options.mask
submask = options.submask
sma_values = options.sma_values
plot_file = options.plot_file

# Trace variables
ftrace = BFilteredTrace(input_file_path, "regexps.bd")
dtrace = None
stats = None

# Diagnoser
if behaviour == "diagnose":
	if directives_file_path == None:
		print "FATAL: directives file path not given."
		exit(1)
	if not os.path.exists(directives_file_path) \
	   or not os.path.isfile(directives_file_path):
		print "FATAL: uncorrect directives file path given."
		exit(1)
	dtrace = BDiagnoser(ftrace, "commands.bd")
	exit(dtrace.diagnose(directives_file_path))

# Plotter
if behaviour == "plot":
	if mask == None or submask == None:
		print "FATAL: mask or submask not given."
		exit(1)
	if sma_values == None or sma_values <= 0:
		print "FATAL: SMA values out of range"
		exit(1)
	stats = BStats(input_file_path, ftrace.get_regexp(mask), ftrace.get_regexp(submask))
	values = stats.get_submask_values()
	sma = stats.get_simple_moving_average(sma_values)
	if plot_file != None:
		g = graph.graphxy(width=8)
		g.plot(graph.data.values(x=range(len(values)), y=values))
		g.writeEPSfile(plot_file)
		g.writePDFfile(plot_file)
		if len(sma) > 0:
			gsma = graph.graphxy(width=8)
			gsma.plot(graph.data.values(x=range(len(sma)), y=sma))
			gsma.writeEPSfile(plot_file + "_SMA")
			gsma.writePDFfile(plot_file + "_SMA")
		exit(0)
	stats.draw_stats()
	try:
		gtk.main()
	except KeyboardInterrupt:
		print "Cleanly exiting."
	exit(0)

# Filter
if filters == None:
	print "FATAL: no behaviour specified and no filter given. Exiting."
	exit(1)
try:
	for line in ftrace.filter(filters):
		print line
except Exception as e:
	print e
	exit(1)
