from simulator.drawer.PictureDrawer import PictureDrawer

import cairo

import math
import random


class CairoDrawer(PictureDrawer):
    def __init__(self, simu, stop):
        super().__init__(simu, stop)

    def custom_init(self):
        self.surface = cairo.PSSurface("out.eps", self.width, self.height)
        self.ctx = cairo.Context(self.surface)

    def randomColor(self):
        return tuple((random.random() for i in range(3)))

    def black(self):
        return (0, 0, 0)

    def white(self):
        return (1, 1, 1)

    def preferredTaskColor(self):
        return (218 / 255, 165 / 255, 32 / 255)

    def gray(self):
        return (0.6, 0.6, 0.6)

    def blue(self):
        return (0, 0, 1)

    def red(self):
        return (1, 0, 0)

    def drawLine(self, x1, y1, x2, y2, width, color):
        self.ctx.set_source_rgb(*color)
        self.ctx.set_line_width(width)
        self.ctx.move_to(x1, y1)
        self.ctx.line_to(x2, y2)
        self.ctx.stroke()

    def greyColor(self, color):
        return tuple((c / 2 for c in color))

    def drawRectangle(self, x1, y1, x2, y2, fillColor, outlineColor):
        self.ctx.set_source_rgb(*outlineColor)
        self.ctx.set_line_width(1)
        width = x2 - x1
        height = y2 - y1
        self.ctx.rectangle(x1, y1, width, height)
        self.ctx.stroke_preserve()
        self.ctx.set_source_rgb(*fillColor)
        self.ctx.fill()
        # self.ctx.set_source_rgb(*outlineColor)
        # self.ctx.rectangle(x1, y1, width, height)

    def drawCircle(self, xC, yC, rad, color):
        self.ctx.set_source_rgb(*color)
        self.ctx.arc(xC, yC, rad, 0, 2 * math.pi)
        self.ctx.fill()

    def drawArrow(self, x1, y1, x2, y2, color):
        self.drawLine(x1, y1, x2, y2, width=2, color=color)
        r = 2
        self.drawCircle(x2, y2, r, color)

    def drawText(self, xT, yT, text, color):
        yT += 6  # quickfix: cairo draws the text centered on yT rather than top-left
        self.ctx.set_source_rgb(*color)
        self.ctx.select_font_face("serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.ctx.set_font_size(10)
        self.ctx.move_to(xT, yT)
        self.ctx.show_text(text)

    def terminate(self):
        super().terminate()
        self.surface.finish()

    def outputName(self):
        return "out.eps"
