# File name: image_text_filter.py
# Author: Kylamity
# Requires python module "Pillow"

#--Config---------------------------------------------------------------------------------------------------------------

# (string) relative or absolute path to source image
SOURCE_IMAGE_PATH = "Arch-hero-wallpaper-free-1080-upscaled.png"

# (string) relative or absolute path for output image, directory must exist
OUTPUT_PATH = "output.png"

# (int) adjusts blank space between columns (can be neg)
PADDING_X = 0

# (int) adjusts blank space between rows (can be neg)
PADDING_Y = 2

# (string) characters to use
#SEED_STRING = """0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%&(){}[]<>\/|~"""
SEED_STRING = "ARCH BTW "
#SEED_STRING = "█"

# (bool) if True, will randomize seed string
RANDOMIZE_SEED = False

# (string) relative or absolute path to ttf (ideally monospace)
FONT_PATH = "usr/share/fonts/TTF/DejaVuSansMono.ttf"

# (int) point size of font
FONT_SIZE = 14

# (bool) if True, FONT_COLOR / BACKGROUND_COLOR will be used, else will use color from source image
FONT_MONOCOLOR = False

# (tuple 0-255 R,G,B) maintain (,,,) format
FONT_COLOR = (255, 255, 255)

# (tuple 0-255 R,G,B) maintain (,,,) format
BACKGROUND_COLOR = (0, 0, 0)

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
from random import randint
from math import floor
from PIL import ImageFont, ImageDraw, Image

class Grid:
    def __init__(self):
        self.canvasWidth = 0 # total canvas pixel width
        self.canvasHeight = 0 # total canvas pixel height
        self.cellWidth = 0 # column width
        self.cellHeight = 0 # row height
        self.cellPaddingX = 0 # column spacing
        self.cellPaddingY = 0 # row spacing
        self.colCoords = []
        self.rowCoords = []

    def genCoords(self):
        print("Generating grid...")
        totalCellWidth = self.cellWidth + self.cellPaddingX
        totalCellHeight = self.cellHeight + self.cellPaddingY
        numCols = floor(self.canvasWidth / totalCellWidth)
        numRows = floor(self.canvasHeight / totalCellHeight)

        for col in range(numCols):
            self.colCoords.append(col * totalCellWidth)
        for row in range(numRows):
            self.rowCoords.append(row * totalCellHeight)


grid = Grid()

def sampleBrValues(sourceImage):
    print("Sampling source image...")
    brValues = []
    numSamplePixels = grid.cellWidth * grid.cellHeight
    for row in range(len(grid.rowCoords)):
        rowBrValues = []
        for col in range(len(grid.colCoords)):
            x0, y0 = grid.colCoords[col], grid.rowCoords[row]
            x1, y1 = x0 + grid.cellWidth, y0 + grid.cellHeight
            sample = sourceImage.crop((x0, y0, x1, y1))
            pixels = sample.load()
            brSum = 0
            for pY in range(sample.size[1]):
                for pX in range(sample.size[0]):
                    pixel = pixels[pX, pY]
                    pixelRGBSum = 0
                    for rgbValue in range(3):
                        pixelRGBSum += pixel[rgbValue]
                    pixelBrightness = pixelRGBSum / 3
                    brSum += pixelBrightness
            brValue = round(brSum / numSamplePixels)
            rowBrValues.append(brValue)
        brValues.append(rowBrValues)
    return brValues


def sampleRGBValues(sourceImage):
    print("Sampling source image...")
    rValues = []
    gValues = []
    bValues = []
    numSamplePixels = grid.cellWidth * grid.cellHeight
    for row in range(len(grid.rowCoords)):
        rowRValues = []
        rowGValues = []
        rowBValues = []
        for col in range(len(grid.colCoords)):
            x0, y0 = grid.colCoords[col], grid.rowCoords[row]
            x1, y1 = x0 + grid.cellWidth, y0 + grid.cellHeight
            sample = sourceImage.crop((x0, y0, x1, y1))
            pixels = sample.load()
            rSum = 0
            gSum = 0
            bSum = 0
            for pY in range(sample.size[1]):
                for pX in range(sample.size[0]):
                    pixel = pixels[pX, pY]
                    rSum += pixel[0]
                    gSum += pixel[1]
                    bSum += pixel[2]
            rValue = round(rSum / numSamplePixels)
            gValue = round(gSum / numSamplePixels)
            bValue = round(bSum / numSamplePixels)
            rowRValues.append(rValue)
            rowGValues.append(gValue)
            rowBValues.append(bValue)
        rValues.append(rowRValues)
        gValues.append(rowGValues)
        bValues.append(rowBValues)
    return rValues, gValues, bValues


def renderImage(font, brValues, rgbValues = None):
    print("Rendering output image...")
    image = Image.new("RGB", (grid.canvasWidth, grid.canvasHeight), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)
    seedIndex = 0
    for row in range(len(grid.rowCoords)):
        for col in range(len(grid.colCoords)):
            xyPos = grid.colCoords[col], grid.rowCoords[row]
            if not rgbValues:
                brValue = brValues[row][col]
                brRatio = brValue / 255
                r = round(FONT_COLOR[0] * brRatio)
                g = round(FONT_COLOR[1] * brRatio)
                b = round(FONT_COLOR[2] * brRatio)
            else:
                r = rgbValues[0][row][col]
                g = rgbValues[1][row][col]
                b = rgbValues[2][row][col]
            color = (r, g, b)
            draw.text(xyPos, SEED_STRING[seedIndex], fill = color, font = font)
            if RANDOMIZE_SEED:
                seedIndex = randint(0, len(SEED_STRING) - 1)
            else:
                seedIndex += 1
                if seedIndex >= len(SEED_STRING):
                    seedIndex = 0
    return image


def getFontDims(font):
    tempImg = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(tempImg)
    textBBox = draw.textbbox((0, 0), "█", font)
    width = textBBox[2] - textBBox[0]
    height = textBBox[3] - textBBox[1]
    del draw
    return width, height


def main():
    print("Started")
    sourceImage = Image.open(SOURCE_IMAGE_PATH)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    grid.canvasWidth, grid.canvasHeight = sourceImage.size
    grid.cellWidth, grid.cellHeight = getFontDims(font)
    grid.cellPaddingX, grid.cellPaddingY = PADDING_X, PADDING_Y
    grid.genCoords()
    rgbValues = None
    brValues = None
    if FONT_MONOCOLOR:
        brValues = sampleBrValues(sourceImage)
    else:
        rgbValues = sampleRGBValues(sourceImage)
    sourceImage.close()
    renderedImage = renderImage(font, brValues, rgbValues)
    renderedImage.save(OUTPUT_PATH)
    print("Finished")
    return None


if __name__ == '__main__':
    main()
