#!/usr/bin/env python

import cairo
import math 

surface = cairo.SVGSurface("OoCA.svg", 200, 200)
context = cairo.Context(surface)
context.set_source_rgba(0, 0, 1, 1)
context.set_line_width(25) # Making rectangle with Jason's method of thick line
context.move_to(25,50)
context.line_to(75,50)
context.stroke()
rectangle = cairo.Context(surface)
rectangle.rectangle(100,100,50,75) # Making rectangle with an actual rectangle
rectangle.set_source_rgba(0, 1, 1, 1)
rectangle.fill()
rectangle.stroke()
surface.finish()


