from simulator.drawer.PictureDrawer import PictureDrawer

from PIL import Image as img
from PIL import ImageFont
from PIL import ImageDraw as draw

import random
import re


class PILDrawer(PictureDrawer):
    def __init__(self, simu, stop):
        super().__init__(simu, stop)

    def custom_init(self):
        self.outImg = img.new("RGB", (self.width, self.height), "white")
        self.fontRoboto = ImageFont.truetype("res/Roboto-Medium.ttf", 9)
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

    def drawArrow(self, x1, y1, x2, y2, color):
        self.drawLine(x1, y1, x2, y2, width=2, color=color)
        r = 2
        self.drawCircle(x2, y2, r, color)

    def drawText(self, xT, yT, text, color):
        self.outDraw.text((xT, yT), str(text), font=self.fontRoboto, fill=color)

    def black(self):
        return "black"

    def white(self):
        return "white"

    def gray(self):
        return "gray"

    def red(self):
        return "red"

    def blue(self):
        return "blue"

    def drawLine(self, x1, y1, x2, y2, width, color):
        self.outDraw.line([x1, y1, x2, y2], width=width, fill=color)

    def drawRectangle(self, x1, y1, x2, y2, fillColor, outlineColor):
        self.outDraw.rectangle([x1, y1, x2, y2], outline=outlineColor, fill=fillColor)

    def drawCircle(self, xC, yC, rad, color):
        self.outDraw.ellipse([xC - rad, yC - rad, xC + rad, yC + rad], fill=color)

    def terminate(self):
        super().terminate()
        self.outImg.save("out.png")

    def outputName(self):
        return "out.png"
