#!/usr/bin/python

from pyx import *

g = graph.graphxy(width=8)
g.plot(graph.data.file("errorbar.dat", x=1, y=2, dy=3),
       [graph.style.symbol(), graph.style.errorbar()])
g.writeEPSfile("errorbar")
g.writePDFfile("errorbar")

g = graph.graphxy(width=8)
g.plot(graph.data.function("y(x)=sin(x)/x", min=-15, max=15))
g.writeEPSfile("graph")
g.writePDFfile("graph")

c = canvas.canvas()
c.text(0, 0, "Hello canvas!")
c.stroke(path.line(0, 0, 2, 0))
c.writeEPSfile("prova")
c.writePDFfile("prova")
