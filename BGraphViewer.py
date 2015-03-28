import gtk, warnings
try:
	from matplotlib.figure import Figure
	from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
	from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
except ImportError:
	raise ImportError("It seems you have no matplotlib package installed. Cannot plot graphs.")

class BGraphViewer:
	def __init__(self, x_values, y_values, x_avg_values, y_avg_values, graphname):
		if (isinstance(x_values,list) == False):
			raise TypeError("X values parameter must be list.")
		if (isinstance(y_values,list) == False):
			raise TypeError("Y values parameter must be list.")
		if (isinstance(x_avg_values,list) == False):
                        raise TypeError("X average values parameter must be list.")
                if (isinstance(y_avg_values,list) == False):
                        raise TypeError("Y average values parameter must be list.")
		if (x_values == []):
			raise ValueError("X values must not be empty.")
		if (y_values == []):
			raise ValueError("Y values must not be empty.")
		if (len(x_values) != len(y_values)):
			raise ValueError("X and Y values must be the same in number.")
		if (len(x_avg_values) != len(y_avg_values)):
			raise ValueError("X and Y average values must be the same in number.")
		if (isinstance(graphname,str) == False):
			raise TypeError("Graph name must be string.")
		if (graphname == ""):
			raise ValueError("Graph name must not be empty.")

		warnings.filterwarnings("ignore",category=DeprecationWarning)

		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_title(str(graphname))
		window.set_default_size(700, 700)
		window.connect("destroy", lambda w: gtk.main_quit())
		vbox = gtk.VBox()

		notebook = gtk.Notebook()
		vbox.pack_start(notebook)
		notebook.show()

		vbox2 = gtk.VBox()
		fig = Figure(figsize=(5,4), dpi=100)
		ax = fig.add_subplot(111)

		ax.set_xlabel("Time")
		ax.set_ylabel(graphname)
		ax.plot(x_values,y_values,marker='x',linestyle='None',color='g')
		# Get maximum and minimum points
		max_val = None
		max_pos = None
		min_val = None
		min_pos = None
		pos = 0
		for y_coord in y_values:
			if y_coord >= max_val:
				max_val = y_coord
				max_pos = x_values[pos]
				if min_val is None:
					min_val = max_val
					min_pos = max_pos
			if y_coord <= min_val:
				min_val = y_coord
				min_pos = x_values[pos]
			pos = pos + 1
		if max_val is not None and max_pos is not None and min_val is not None and min_pos is not None:
			ax.plot(max_pos,max_val, "r^")
			ax.plot(min_pos,min_val, "bv")

		canvas = FigureCanvas(fig)
		vbox2.pack_start(canvas)
		toolbar = NavigationToolbar(canvas, window)
		vbox2.pack_start(toolbar, False, False)

		frame = gtk.Frame(str(graphname))
		frame.show()

		label = gtk.Label("Punctual Values")
		frame.add(vbox2)

		notebook.append_page(frame, label)

		vbox3 = gtk.VBox()
                fig_avg = Figure(figsize=(5,4), dpi=100)
                ax_avg = fig_avg.add_subplot(111)

                ax_avg.set_xlabel("Time")
                ax_avg.set_ylabel(graphname + " Simple Moving Average")
                ax_avg.plot(x_avg_values,y_avg_values,marker='x',linestyle='None',color='g')

		canvas_avg = FigureCanvas(fig_avg)
		if y_avg_values == []:
			vbox3.pack_start(gtk.Label("Not enough values to draw SMA."))
		else: # pragma: no cover
	                vbox3.pack_start(canvas_avg)
			toolbar_avg = NavigationToolbar(canvas_avg, window)
                	vbox3.pack_start(toolbar_avg, False, False)

                frame_avg = gtk.Frame(str(graphname))
                frame_avg.show()

                label_avg = gtk.Label("Simple Moving Average")
                frame_avg.add(vbox3)

                notebook.append_page(frame_avg, label_avg)

		window.add(vbox)
		window.show_all()

