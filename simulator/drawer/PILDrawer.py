from simulator.drawer.PictureDrawer import PictureDrawer

from PIL import Image as img
from PIL import ImageFont
from PIL import ImageDraw as draw

import random
import re


class PILDrawer(PictureDrawer):
    def __init__(self, simu, stop):
        self.scale = 10
        super().__init__(simu, stop)

    def custom_init(self):
        self.outImg = img.new("RGB", (self.scale * self.width, self.scale * self.height), "white")
        fontSize = 9 * self.scale
        self.fontRoboto = ImageFont.truetype("res/Roboto-Medium.ttf", fontSize)
        self.outDraw = draw.Draw(self.outImg)


    def randomColor(self):
        return "rgb(" + ",".join([str(random.randint(0, 255)) for i in range(3)]) + ")"

    def greyColor(self, color):
        colorRe = re.compile('\d+')
        rgb = colorRe.findall(color)
        assert len(rgb) == 3
        rgb = [int(s) for s in rgb]
        rgbGrey = [c // 2 for c in rgb]
        return "rgb(" + ",".join([str(c) for c in rgbGrey]) + ")"

    def drawText(self, xT, yT, text, size, color):
        xT *= self.scale
        yT *= self.scale
        size *= self.scale
        self.outDraw.text((xT, yT), str(text), font=self.fontRoboto, fill=color)

    def black(self):
        return "black"

    def white(self):
        return "white"

    def preferredTaskColor(self):
        if self.blackandwhite:
            return "rgb(162, 205, 90)"
        else:
            return "rgb(218, 165, 32)"

    def gray(self):
        return "gray"

    def red(self):
        return "red"

    def blue(self):
        return "blue"

    def drawLine(self, x1, y1, x2, y2, width, color):
        x1 *= self.scale
        y1 *= self.scale
        x2 *= self.scale
        y2 *= self.scale
        width *= self.scale
        self.outDraw.line([x1, y1, x2, y2], width=width, fill=color)

    def drawRectangle(self, x1, y1, x2, y2, fillColor, outlineColor):
        x1 *= self.scale
        y1 *= self.scale
        x2 *= self.scale
        y2 *= self.scale
        self.outDraw.rectangle([x1, y1, x2, y2], outline=outlineColor, fill=fillColor)

    def drawCircle(self, xC, yC, rad, color):
        xC *= self.scale
        yC *= self.scale
        rad *= self.scale
        self.outDraw.ellipse([xC - rad, yC - rad, xC + rad, yC + rad], fill=color)

    def terminate(self):
        self.drawGrid(self.stop)
        super().terminate()
        self.outImg.save("out.png")

    def outputName(self):
        return "out.png"
