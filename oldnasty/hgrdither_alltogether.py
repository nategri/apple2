from PIL import Image
from math import *

import sys

import struct




def getStupidClosestColor(colorTuple):

    global orange,blue,purple,green,white,black


    # the 'whatever' color values (playing around)
    #blue = (0xee,0x80,0xee)
    #orange = (0xcd,0x5b

    # taken from the wikipedia page on 8-bit computer palettes (from GNOME dropper)



    hgrRGBtuple = {'blue': blue, 'orange': orange, 'purple': purple, 'green': green, 'black': black, 'white': white}
    #hgrRGB = {'blue': 0x14cffd, 'orange': 0xff6a3c, 'purple': 0xff44fd, 'green': 0x14f53c, 'black': 0x000000}

    # have no idea where these colors came from (saving this for backup)
    #hgrDisplayColor = {'blue': (0x19,0x8b,0xe5), 'orange': (0xcd,0x5b,0x01), 'purple': (0xcd,0x2f,0xe5), 'green': (0x19,0xb7,0x01), 'black': (0x00,0x00,0x00)}


    mindist = sqrt(255*255*3+1) # everything should be closer than this


    for color, value in hgrRGBtuple.iteritems():
        #if (color == 'green') or (color == 'orange') or (color == 'black'):
        dist = sqrt(pow((value[0]-colorTuple[0]),2)+pow((value[1]-colorTuple[1]),2)+pow((value[2]-colorTuple[2]),2))
        if color == 'green':
            greenDist = dist
        if color == 'orange':
            orangeDist = dist
        if color == 'blue':
            blueDist = dist
        if color == 'purple':
            purpleDist = dist
        if color == 'black':
            blackDist = dist
        if dist < mindist:
            mindist = dist
            mincolor = color
                        
    return mincolor

def stupidDither(file):

    global orange,blue,purple,green,white,black
    
    hgrRGBtuple = {'blue': blue, 'orange': orange, 'purple': purple, 'green': green, 'black': black, 'white': white}

    im = Image.open(file)
    
    pix = im.load()

    hgrDisplayColor = {'blue': blue, 'orange': orange, 'purple': purple, 'green': green, 'black': black, 'white': white}

    # hard coded to accept only native HGR size for now
    xMax = 280
    yMax = 192

    quantErr = [0,0,0]
    newColor = [0,0,0]

    colorDelta = [[ [0 for i in range(yMax)] for j in range(xMax)],[ [0 for i in range(yMax)] for j in range(xMax)],[ [0 for i in range(yMax)] for j in range(xMax)]]

    pix = im.load()
        
    for y in range(yMax):
        for x in range(xMax):
            newColor = [pix[x,y][0]+colorDelta[0][x][y],pix[x,y][1]+colorDelta[1][x][y],pix[x,y][2]+colorDelta[2][x][y]]

            for i in range(3):
                newColor[i] = int(newColor[i]+0.5)
                if newColor[i] > 255:
                    newColor[i] = 255
                if newColor[i] < 0:
                    newColor[i] = 0

            bestColor = getStupidClosestColor((newColor[0],newColor[1],newColor[2]))
            for i in range(3):
                #print bestColor
                quantErr[i] = pix[x,y][i] + colorDelta[i][x][y] - hgrRGBtuple[bestColor][i]

            im.putpixel((x,y),hgrDisplayColor[bestColor])

            # STUFF TO PERFORM ATKINSON DITHERING ALGORITHM
            if (x+1) < xMax:
                for i in range(3):
                    #print i
                    #print x+1
                    #print y
                    #print colorDelta[i][x+1][y]
                    colorDelta[i][x+1][y] = colorDelta[i][x+1][y] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x+1][y] > 255:
                        colorDelta[i][x+1][y] = 255
                    if colorDelta[i][x+1][y] < 0:
                        colorDelta[i][x+1][y] = 0
                    #print colorDelta[i][x+1][y]
                    #print ""

            if ((y+1) < yMax) and ((x-1) > 0):
                for i in range(3):
                    colorDelta[i][x-1][y+1] = colorDelta[i][x-1][y+1] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x-1][y+1] > 255:
                        colorDelta[i][x-1][y+1] = 255
                    if colorDelta[i][x-1][y+1] < 0:
                        colorDelta[i][x-1][y+1] = 0

            if (y+1) < yMax:
                for i in range(3):
                    colorDelta[i][x][y+1] = colorDelta[i][x][y+1] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x][y+1] > 255:
                        colorDelta[i][x][y+1] = 255
                    if colorDelta[i][x][y+1] < 0:
                        colorDelta[i][x][y+1] = 0

            if ((y+1) < yMax) and ((x+1) < xMax):
                for i in range(3):
                    colorDelta[i][x+1][y+1] = colorDelta[i][x+1][y+1] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x+1][y+1] > 255:
                        colorDelta[i][x+1][y+1] = 255
                    if colorDelta[i][x+1][y+1] < 0:
                        colorDelta[i][x+1][y+1] = 0

            if (y+2) < yMax:
                for i in range(3):
                    colorDelta[i][x][y+2] = colorDelta[i][x][y+2] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x][y+2] > 255:
                        colorDelta[i][x][y+2] = 255
                    if colorDelta[i][x][y+2] < 0:
                        colorDelta[i][x][y+2] = 0

            if (x+2) < xMax:
                for i in range(3):
                    colorDelta[i][x+2][y] = colorDelta[i][x+2][y] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x+2][y] > 255:
                        colorDelta[i][x+2][y] = 255
                    if colorDelta[i][x+2][y] < 0:
                        colorDelta[i][x+2][y] = 0

    im.save("stupid_dither.png")

def getClosestColor(x,colorTuple,lastblack,MSB):

    # the 'whatever' color values (playing around)
    #blue = (0xee,0x80,0xee)
    #orange = (0xcd,0x5b

    global orange,blue,purple,green,black

    # taken from some guy who says it's from pre-IIgs video out circuits
    #green = (0x14,0xf5,0x3c)
    #purple = (0xff,0x44,0xfd)
    #orange = (0xff,0x6a,0x3c)
    #blue = (0x14,0xcf,0xfd)
    #black = (0x00,0x00,0x00)

    # taken from the apple iigs techical specs
    #blue = (0x22,0x22,0xff)
    #orange = (0xff,0x66,0x00)
    #purple = (0xdd,0x22,0xdd)
    #green = (0x11,0x77,0x22) #'dark green'
    #black = (0x00,0x00,0x00)

    hgrRGBtuple = {'blue': blue, 'orange': orange, 'purple': purple, 'green': green, 'black': black}
    #hgrRGB = {'blue': 0x14cffd, 'orange': 0xff6a3c, 'purple': 0xff44fd, 'green': 0x14f53c, 'black': 0x000000}

    oddColors = ( {'green': green, 'black': black}, {'orange': orange, 'black': black} )
    evenColors = ( {'purple': purple, 'black': black}, {'blue': blue, 'black': black} )

    # have no idea where these colors came from (saving this for backup)
    #hgrDisplayColor = {'blue': (0x19,0x8b,0xe5), 'orange': (0xcd,0x5b,0x01), 'purple': (0xcd,0x2f,0xe5), 'green': (0x19,0xb7,0x01), 'black': (0x00,0x00,0x00)}


    mindist = sqrt(255*255*3+1) # everything should be closer than this

    if ( x % 2 == 1):
        #odd pixel!

        if (x % 7 == 0) or lastblack:
            # here's a chance to pick set the MSB (OPTIMIZE LATER)


            for color, value in hgrRGBtuple.iteritems():
                #if (color == 'green') or (color == 'orange') or (color == 'black'):
                dist = sqrt(pow((value[0]-colorTuple[0]),2)+pow((value[1]-colorTuple[1]),2)+pow((value[2]-colorTuple[2]),2))
                if color == 'green':
                    greenDist = dist
                if color == 'orange':
                    orangeDist = dist
                if color == 'blue':
                    blueDist = dist
                if color == 'purple':
                    purpleDist = dist
                if color == 'black':
                    blackDist = dist
                if dist < mindist:
                    mindist = dist
                    mincolor = color
                        
                        
            if mincolor == 'green':
                MSB = 0
            elif mincolor == 'orange':
                MSB = 1
            elif (mincolor == 'blue'):
                if blackDist > orangeDist:
                    mincolor = 'orange'
                    MSB = 1
                    #print "triggered!"
                else:
                    mincolor = 'black'
                #if lastblack == 1:
                #    mincolor = 'black'
                #    print "triggered!"
            elif (mincolor == 'purple'):
                if blackDist > greenDist:
                    mincolor = 'green'
                    MSB = 0
                else:
                    mincolor = 'black'
                #if lastblack == 1:
                #    mincolor = 'black'					

            if mincolor == 'black':
                lastblack = 1
            else:
                lastblack = 0

            return mincolor,lastblack,MSB

        else:

            for color, value in oddColors[MSB].iteritems():
                dist = sqrt(pow((value[0]-colorTuple[0]),2)+pow((value[1]-colorTuple[1]),2)+pow((value[2]-colorTuple[2]),2))
                if dist < mindist:
                    mindist = dist
                    mincolor = color

            return mincolor,lastblack,MSB

    if ( x % 2 == 0):
        #even pixel!

        if (x % 7 == 0) or lastblack:
            # here's a chance to pick set the MSB (OPTIMIZE LATER)

            for color, value in hgrRGBtuple.iteritems():
                #if (color == 'purple') or (color == 'blue') or (color == 'black'):
                dist = sqrt(pow((value[0]-colorTuple[0]),2)+pow((value[1]-colorTuple[1]),2)+pow((value[2]-colorTuple[2]),2))
                if color == 'green':
                    greenDist = dist
                if color == 'orange':
                    orangeDist = dist
                if color == 'blue':
                    blueDist = dist
                if color == 'purple':
                    purpleDist = dist
                if color == 'black':
                    blackDist = dist
                if dist < mindist:
                    mindist = dist
                    mincolor = color
                        
            if mincolor == 'purple':
                MSB = 0
            elif mincolor == 'blue':
                MSB = 1
            elif (mincolor == 'green'):
                if blackDist > purpleDist:
                    mincolor = 'purple'
                    MSB = 0
                else:
                    mincolor = 'black'
                #if lastblack == 1:
                #    mincolor = 'black'
            elif (mincolor == 'orange'):
                if blackDist > blueDist:
                    mincolor = 'blue'
                    MSB = 1
                    #print "also triggered!"
                else:
                    mincolor = 'black'
                #if lastblack == 1:
                #    mincolor = 'black'
                    
            if mincolor == 'black':
                lastblack = 1
            else:
                lastblack = 0
                
            return mincolor,lastblack,MSB

        else:

            for color, value in evenColors[MSB].iteritems():
                dist = sqrt(pow((value[0]- colorTuple[0]),2)+pow((value[1]-colorTuple[1]),2)+pow((value[2]-colorTuple[2]),2))
                if dist < mindist:
                    mindist = dist
                    mincolor = color

            return mincolor,lastblack,MSB
            
def apple2Dither():

    global orange,blue,purple,green,black

    hgrRGBtuple = {'blue': blue, 'orange': orange, 'purple': purple, 'green': green, 'black': black}
    hgrDisplayColor = {'blue': blue, 'orange': orange, 'purple': purple, 'green': green, 'black': black}

    # hard coded to accept only native HGR size for now
    xMax = 280
    yMax = 192

    quantErr = [0,0,0]
    newColor = [0,0,0]

    colorDelta = [[ [0 for i in range(yMax)] for j in range(xMax)],[ [0 for i in range(yMax)] for j in range(xMax)],[ [0 for i in range(yMax)] for j in range(xMax)]]

    paletteBit = [ [0 for i in range(yMax)] for j in range(40)]

    mostSigBit = 0

    lastblack = 0

    im = Image.open("stupid_dither.png")

    pix = im.load()

    currXByte = -1

    for y in range(yMax):
        for x in range(xMax):
            newColor = [pix[x,y][0]+colorDelta[0][x][y],pix[x,y][1]+colorDelta[1][x][y],pix[x,y][2]+colorDelta[2][x][y]]
            
            for i in range(3):
                newColor[i] = int(newColor[i]+0.5)
                if newColor[i] > 255:
                    newColor[i] = 255
                if newColor[i] < 0:
                    newColor[i] = 0
                    
            bestColor,lastblack,mostSigBit = getClosestColor(x,(newColor[0],newColor[1],newColor[2]),lastblack,mostSigBit)
            for i in range(3):
                #print bestColor
                quantErr[i] = pix[x,y][i] + colorDelta[i][x][y] - hgrRGBtuple[bestColor][i]

            im.putpixel((x,y),hgrDisplayColor[bestColor])

            # STUFF TO PERFORM ATKINSON DITHERING ALGORITHM
            if (x+1) < xMax:
                for i in range(3):
                    #print i
                    #print x+1
                    #print y
                    #print colorDelta[i][x+1][y]
                    colorDelta[i][x+1][y] = colorDelta[i][x+1][y] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x+1][y] > 255:
                        colorDelta[i][x+1][y] = 255
                    if colorDelta[i][x+1][y] < 0:
                        colorDelta[i][x+1][y] = 0
                    #print colorDelta[i][x+1][y]
                    #print ""

            if ((y+1) < yMax) and ((x-1) > 0):
                for i in range(3):
                    colorDelta[i][x-1][y+1] = colorDelta[i][x-1][y+1] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x-1][y+1] > 255:
                        colorDelta[i][x-1][y+1] = 255
                    if colorDelta[i][x-1][y+1] < 0:
                        colorDelta[i][x-1][y+1] = 0

            if (y+1) < yMax:
                for i in range(3):
                    colorDelta[i][x][y+1] = colorDelta[i][x][y+1] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x][y+1] > 255:
                        colorDelta[i][x][y+1] = 255
                    if colorDelta[i][x][y+1] < 0:
                        colorDelta[i][x][y+1] = 0

            if ((y+1) < yMax) and ((x+1) < xMax):
                for i in range(3):
                    colorDelta[i][x+1][y+1] = colorDelta[i][x+1][y+1] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x+1][y+1] > 255:
                        colorDelta[i][x+1][y+1] = 255
                    if colorDelta[i][x+1][y+1] < 0:
                        colorDelta[i][x+1][y+1] = 0

            if (y+2) < yMax:
                for i in range(3):
                    colorDelta[i][x][y+2] = colorDelta[i][x][y+2] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x][y+2] > 255:
                        colorDelta[i][x][y+2] = 255
                    if colorDelta[i][x][y+2] < 0:
                        colorDelta[i][x][y+2] = 0

            if (x+2) < xMax:
                for i in range(3):
                    colorDelta[i][x+2][y] = colorDelta[i][x+2][y] + (1.0/8)*quantErr[i]
                    if colorDelta[i][x+2][y] > 255:
                        colorDelta[i][x+2][y] = 255
                    if colorDelta[i][x+2][y] < 0:
                        colorDelta[i][x+2][y] = 0

            
            if (x % 7) == 0:
                currXByte = currXByte+1

            paletteBit[currXByte][y] = mostSigBit 

        currXByte = -1

    im.save("hgrphoto.png")

    return paletteBit            

    
def saveA2Binary(outfile,paletteBit):
    #print paletteBit

    ## OK NOW LET'S TRY TO OUTPUT SOMETHING AN APPLE II CAN ACTUALLY READ

    im = Image.open("hgrphoto.png")

    pix = im.load()

    # loop over all the bytes in video memory -- going to take advantage of the 1:64 interleave

    #for pixels
    x = 0
    y = 0

    f = open(outfile, 'wb')

    times_around = 0

    timemod = 0

    for line in range(8):

        y = line
        x = 0
        times_around = 0

        for xbyte in range(120*8):

            newByte = 0

            if x >= 280:
                times_around = times_around + 1
                # various stuff has to get done every three lines
                # change y position, fill zeroes into screen holes
                if (times_around % 3) == 0:
                    y = y - 128 - 64 + 8
                    newByte = 0
                    # eight empty bytes -- these are the 'screen holes' I think
                    for i in range(8):
                        f.write(struct.pack('B',newByte))
                #print "DING"
                y = y + 64
                x = 0

            #print str(x) + " " + str(xbyte) + " " + str(y) + " " + str(times_around)

            if pix[x,y] != (0,0,0):
                newByte = newByte | 0b00000001
            if pix[x+1,y] != (0,0,0):
                newByte = newByte | 0b00000010
            if pix[x+2,y] != (0,0,0):
                newByte = newByte | 0b00000100
            if pix[x+3,y] != (0,0,0):
                newByte = newByte | 0b00001000
            if pix[x+4,y] != (0,0,0):
                newByte = newByte | 0b00010000
            if pix[x+5,y] != (0,0,0):
                newByte = newByte | 0b00100000
            if pix[x+6,y] != (0,0,0):
                newByte = newByte | 0b01000000
            if paletteBit[xbyte%40][y]:
                newByte = newByte | 0b10000000
            
            x = x + 7

            #print newByte

            #print str(x)+","+str(y)
            f.write(struct.pack('B',newByte))

        # tack on another set of screen holes to end this pass
        for i in range(8):
            f.write(struct.pack('B',newByte))


    f.close()

blue = (0x00,0x80,0xff)
orange = (0xff,0x80,0x00)
purple = (0xff,0x00,0xff)
green = (0x00,0xff,0x00)
black = (0x00,0x00,0x00)
white = (0xff,0xff,0xff)
    
infile = sys.argv[1]
outfile = sys.argv[2]

stupidDither(sys.argv[1])

palette = apple2Dither()

saveA2Binary(sys.argv[2],palette)


