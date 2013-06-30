from PIL import Image
from math import *

import ImageEnhance

import shutil

import sys
import os

import struct
import binascii

def processImage(infile):
    try:
        im = Image.open(infile)
    except IOError:
        print "Cant load", infile
        sys.exit(1)
    i = 0
    mypalette = im.getpalette()

    try:
        while 1:
            im.putpalette(mypalette)
            new_im = Image.new("RGBA", im.size)
            new_im.paste(im)
            new_im.save('frame'+str(i)+'.png')

            i += 1
            im.seek(im.tell() + 1)
            numframes = i

    except EOFError:
        pass # end of sequence
        
    return numframes
        
def genFrames(file,brightness,option):
    frames = processImage(file)

    im = Image.open('frame0.png')
    bg = Image.new("RGB",im.size,(255,255,255))
    bg.paste(im)

    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(brightness)

    bg.save('frame0.jpg')

    for i in range(frames):

        im = Image.open('frame'+str(i+1)+'.png')
        
        bg = Image.new("RGB",im.size,(255,255,255))
        bg = Image.open('frame'+str(i)+'.png')
        bg.paste(im,(0,0),im)
        bg.save('frame'+str(i+1)+'.png')
    
        old = Image.open('frame'+str(i+1)+'.png')
        new = Image.new("RGB",im.size,(255,255,255))
        new.paste(old)
    
        # try to reduce brightness
        enhancer = ImageEnhance.Brightness(new)
        new = enhancer.enhance(brightness)
    
        new.save('frame'+str(i+1)+'.jpg')
    
    
    if option == "small":
        #resize the whole lot
        for i in range(frames+1):
            impng = Image.open('frame'+str(i)+'.png')
            smallpng = Image.new("RGB",impng.size,(0,0,0))
            impng = impng.resize((210,144))
            smallpng.paste(impng,(35,24))
            smallpng.save('frame'+str(i)+'.png')
    
            imjpg = Image.open('frame'+str(i)+'.jpg')
            smalljpg = Image.new("RGB",imjpg.size,(0,0,0))
            imjpg = imjpg.resize((210,144))
            smalljpg.paste(imjpg,(35,24))
            smalljpg.save('frame'+str(i)+'.jpg')

    if option == "tiny":
        #resize the whole lot
        for i in range(frames+1):
            impng = Image.open('frame'+str(i)+'.png')
            smallpng = Image.new("RGB",impng.size,(0,0,0))
            impng = impng.resize((140,96))
            smallpng.paste(impng,(70,48))
            smallpng.save('frame'+str(i)+'.png')
    
            imjpg = Image.open('frame'+str(i)+'.jpg')
            smalljpg = Image.new("RGB",imjpg.size,(0,0,0))
            imjpg = imjpg.resize((140,96))
            smalljpg.paste(imjpg,(70,48))
            smalljpg.save('frame'+str(i)+'.jpg')


    return frames

def getStupidClosestColor(colorTuple):

    global blue,orange,black


    # the 'whatever' color values (playing around)
    #blue = (0xee,0x80,0xee)
    #orange = (0xcd,0x5b

    # taken from the wikipedia page on 8-bit computer palettes (from GNOME dropper)



    hgrRGBtuple = {'blue': blue, 'orange': orange, 'black': black, 'white':white}
    #hgrRGB = {'blue': 0x14cffd, 'orange': 0xff6a3c, 'purple': 0xff44fd, 'green': 0x14f53c, 'black': 0x000000}

    # have no idea where these colors came from (saving this for backup)
    #hgrDisplayColor = {'blue': (0x19,0x8b,0xe5), 'orange': (0xcd,0x5b,0x01), 'purple': (0xcd,0x2f,0xe5), 'green': (0x19,0xb7,0x01), 'black': (0x00,0x00,0x00)}


    mindist = sqrt(255*255*3+1) # everything should be closer than this


    for color, value in hgrRGBtuple.iteritems():
        #if (color == 'green') or (color == 'orange') or (color == 'black'):
        dist = sqrt(pow((value[0]-colorTuple[0]),2)+pow((value[1]-colorTuple[1]),2)+pow((value[2]-colorTuple[2]),2))
        if color == 'orange':
            orangeDist = dist
        if color == 'blue':
            blueDist = dist
        if color == 'black':
            blackDist = dist
        if dist < mindist:
            mindist = dist
            mincolor = color
            
    return mincolor

def grabFrame(file,frame):
    imgif = Image.open(file)

    for i in range(frame):
        imgif.seek(imgif.tell()+1)
    
    imconv = Image.new("RGB",imgif.size,(255,255,255))
    
    imconv.paste(imgif,None)

    imconv.save("currframe.jpg")    
    
def stupidDither(framenum):

    global blue,orange,white,black
    
    hgrRGBtuple = {'blue': blue, 'orange': orange, 'black': black, 'white':white}
    
    im = Image.open('frame'+str(framenum)+'.jpg')
    
    pix = im.load()

    hgrDisplayColor = {'blue': blue, 'orange': orange, 'black': black, 'white':white}

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

def getClosestColor(x,colorTuple):

    # the 'whatever' color values (playing around)
    #blue = (0xee,0x80,0xee)
    #orange = (0xcd,0x5b

    global blue,orange,black

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

    hgrRGBtuple = {'blue': blue, 'orange': orange, 'black': black}
    #hgrRGB = {'blue': 0x14cffd, 'orange': 0xff6a3c, 'purple': 0xff44fd, 'green': 0x14f53c, 'black': 0x000000}

    oddColors = {'orange': orange, 'black': black}
    evenColors = {'blue': blue, 'black': black}

    # have no idea where these colors came from (saving this for backup)
    #hgrDisplayColor = {'blue': (0x19,0x8b,0xe5), 'orange': (0xcd,0x5b,0x01), 'purple': (0xcd,0x2f,0xe5), 'green': (0x19,0xb7,0x01), 'black': (0x00,0x00,0x00)}


    mindist = sqrt(255*255*3+1) # everything should be closer than this

    if ( x % 2 == 1):
        #odd pixel!

        for color, value in oddColors.iteritems():
            dist = sqrt(pow((value[0]-colorTuple[0]),2)+pow((value[1]-colorTuple[1]),2)+pow((value[2]-colorTuple[2]),2))
            if dist < mindist:
                mindist = dist
                mincolor = color

        return mincolor

    if ( x % 2 == 0):
        #even pixel!

        for color, value in evenColors.iteritems():
            dist = sqrt(pow((value[0]- colorTuple[0]),2)+pow((value[1]-colorTuple[1]),2)+pow((value[2]-colorTuple[2]),2))
            if dist < mindist:
                mindist = dist
                mincolor = color

        return mincolor
        
def apple2Dither():

    global blue,orange,black

    hgrRGBtuple = {'blue': blue, 'orange': orange, 'black': black}
    hgrDisplayColor = {'blue': blue, 'orange': orange, 'black': black}

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
                    
            bestColor = getClosestColor(x,(newColor[0],newColor[1],newColor[2]))
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

            paletteBit[currXByte][y] = 1

        currXByte = -1

    im.save("hgrphoto.png")
    os.remove("stupid_dither.png")

    return paletteBit            


def saveA2Binary(outfile,paletteBit):
    #print paletteBit
    
    byteList = []

    ## OK NOW LET'S TRY TO OUTPUT SOMETHING AN APPLE II CAN ACTUALLY READ

    im = Image.open("hgrphoto.png")

    pix = im.load()

    # loop over all the bytes in video memory -- going to take advantage of the 1:64 interleave

    #for pixels
    x = 0
    y = 0

    f = open(outfile, 'ab')

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
                    newByte = 0b10000000
                    # eight empty bytes -- these are the 'screen holes' I think
                    for i in range(8):
                        f.write(struct.pack('B',newByte))
                        byteList.append(newByte)
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
            
            if newByte == 0:
                newByte = 0b10000000
            
            f.write(struct.pack('B',newByte))
            byteList.append(newByte)

        # tack on another set of screen holes to end this pass
        newByte = 0b10000000
        for i in range(8):
            f.write(struct.pack('B',newByte))
            byteList.append(newByte)

    f.close()
    os.remove("hgrphoto.png")
    
    return byteList

def updateMask(n):
    # compare orginal frame jpegs to determine whether or not a byte is candidate for update
    # returns list of bytes
    # a '1' means that a byte is updateable, '0' otherwise
    
    # structure cribbed from the binary saver
    
    byteList = []

    imcurr = Image.open('frame'+str(n)+'.png')
    pixcurr = imcurr.load()
    
    imlast = Image.open('frame'+str(n-1)+'.png')
    pixlast = imlast.load()
    
    # loop over all the bytes in video memory -- going to take advantage of the 1:64 interleave

    #for pixels
    x = 0
    y = 0

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
                        byteList.append(newByte)
                #print "DING"
                y = y + 64
                x = 0

            #print str(x) + " " + str(xbyte) + " " + str(y) + " " + str(times_around)
            
            newByte = 0
            diff = 0
            for k in range(7):
                colorDistance = sqrt(pow(pixcurr[x+k,y][0]-pixlast[x+k,y][0],2)+pow(pixcurr[x+k,y][1]-pixlast[x+k,y][1],2)+pow(pixcurr[x+k,y][2]-pixlast[x+k,y][2],2))
                if ( colorDistance > 30 ):
                    diff = diff + 1
            
            if diff > 1:
                newByte = 1
                
            # where all the ifs went in the binary saving function
            
            x = x + 7
            
            byteList.append(newByte)

        # tack on another set of screen holes to end this pass
        newByte = 0
        for i in range(8):
            byteList.append(newByte)
    
    os.remove('frame'+str(n-1)+'.png')

    return byteList    

def cmpBytes(byte1,byte2):
    diff = 0    
    if (byte1&0b00000001) != (byte2&0b00000001):
        diff = diff + 1
    if (byte1&0b00000010) != (byte2&0b00000010):
        diff = diff + 1
    if (byte1&0b00000100) != (byte2&0b00000100):
        diff = diff + 1
    if (byte1&0b00001000) != (byte2&0b00001000):
        diff = diff + 1
    if (byte1&0b00010000) != (byte2&0b00010000):
        diff = diff + 1
    if (byte1&0b00100000) != (byte2&0b00100000):
        diff = diff + 1
    if (byte1&0b01000000) != (byte2&0b01000000):
        diff = diff + 1
    if (byte1&0b10000000) != (byte2&0b10000000):
        diff = 8
    return diff

def compress(file):
    # simple implementation of the LZ77 compression algorithm
    # input stream is 128-255 (high bits set)

    # will use 255 'window' with max length of 127

    # first 0-127 byte indicates length to copy
    # second 0-255 byte is pointer to previous uncompressed data (e.g. how many bytes back to look)

    infile = open(file,"rb").read()
    #outfile = open(compfile,'r+b')

    bytes = []

    compbytes = []

    for el in infile:
        bytes.append(struct.unpack('B',el)[0])
        
    #compbytes.append(bytes[0])

    i = 0

    while i < bytes.__len__():
        if i < 255:
            winstart = 0
        else:
            winstart = i - 255

        maxmatchlen = 0
        maxmatchpt = 0 # this is abosolute! not relative! subtract before you store!

        for pt in range(winstart,i):

            length = 0

            for j in range(127):

                if (i+j) >= bytes.__len__():
                    break

                if bytes[i+j] == bytes[pt+j]:
                    length = length + 1
                
                if length > maxmatchlen:
                    maxmatchlen = length
                    maxmatchpt = pt

                if bytes[i+j] != bytes[pt+j]:
                    break


        if maxmatchlen > 2:
            # be clever, look for runs of zeroes
            # should help improve decrunch time
            zeroes = True
            for k in range(0,maxmatchlen):
                if (bytes[maxmatchpt+k] != 0x80):
                    zeroes = False
                    break

            if zeroes:
                compbytes.append(1)
                compbytes.append(maxmatchlen)
                i = i + maxmatchlen
                #print "all zeroes!!"
            else:
                compbytes.append(maxmatchlen)
                compbytes.append(i-maxmatchpt)
                i = i + maxmatchlen
        else:
            compbytes.append(bytes[i])
            i = i + 1

    # signals end of data
    compbytes.append(0)


    #for i in range((compbytes.__len__()-10),compbytes.__len__()):
        #print compbytes[i]

    # store length as first two bytes
    #loByte = compbytes.__len__()&0x00FF
    #hiByte = compbytes.__len__()>>8
    #outfile.write(struct.pack('B',loByte))
    #outfile.write(struct.pack('B',hiByte))


    #for el in compbytes:
        #outfile.write(struct.pack('B',el))

    #outfile.close()

    return compbytes


blue = (0x00,0x80,0xff)
orange = (0xff,0x80,0x00)
black = (0x00,0x00,0x00)
white = (0xff,0xff,0xff)

currFrame = []
onebackFrame = []

# frame with the differences from one frame back
diffFrame = []

# list of frame update lengths
updateLengths = []

totalkeylength = 0 # length of all keyframes together

totalgaps = 0

#
# GENERATE FRAMES TO USE FROM GIF FILE
#

if len(sys.argv) == 1:
    print "USAGE: hgrdither.py [outputfilename] [inputgif] [brightness (float of order 1.0)] [videosize (normal,small,tiny)]"
    sys.exit()

numframes = genFrames(sys.argv[2],float(sys.argv[3]),sys.argv[4]) + 1
print "Number of frames to process: " + str(numframes) + str("\n")

#
# INITIALIZE COMPONENTS OF BINARY VIDEO FILE
#

f_lengths = open("blengths",'ab')
f_diffs = open("bdiffs",'ab')
f_keys = open("bkeys",'ab')

# create and compress first image in animation
# this is a keyframe
stupidDither(0)
palette = apple2Dither()
saveA2Binary("keyframe",palette)
keyFrame = compress("keyframe")

for keyByte in keyFrame:
    f_keys.write(struct.pack('B',keyByte))

os.remove("keyframe")

keylength = keyFrame.__len__()
totalkeylength = totalkeylength + keylength
keylength = keylength + 0x8000 # high bit on high byte being set tells it to use LZ77 decoding

updateLengths.append(keylength)

#
# LOOP THROUGH FRAMES
#

for n in range(0,numframes):
    #print n
    onebackFrame = currFrame
    diffFrame = []
    
    #print diffFrame
    
    #grabFrame(sys.argv[1],n)
    stupidDither(n)
    palette = apple2Dither()
    currFrame = saveA2Binary(sys.argv[1]+str(n),palette)

    os.remove('frame'+str(n)+'.jpg')

    bitdiff = 0
    
    if n > 0:
        gap = 0
        mask = updateMask(n)
        #if n == 1:
            #print mask
        for m in range(currFrame.__len__()):
            bitdiff = cmpBytes(currFrame[m],onebackFrame[m])
            if (currFrame[m] != onebackFrame[m]) and (gap>1) and (bitdiff>0) and mask[m]:
                #diffFrame.append(0)
                #diffFrame.append((gap)&0x00FF)
                #diffFrame.append((gap)>>8)
                if(gap>127):
                    while (gap>127):
                        diffFrame.append(127)
                        gap = gap - 127
                diffFrame.append(gap)
                diffFrame.append(currFrame[m])
                gap = 0
                totalgaps = totalgaps + 1
            elif (currFrame[m] != onebackFrame[m]) and (gap<=1) and (bitdiff>0) and mask[m]:
                if gap == 1:
                    diffFrame.append(currFrame[m-1])
                if gap == 2:
                    diffFrame.append(currFrame[m-2])
                    diffFrame.append(currFrame[m-1])
                diffFrame.append(currFrame[m])
                gap = 0
            else:
                gap = gap + 1

        # tell codec this is the end of the frame
        diffFrame.append(0)

        keyFrame = compress(sys.argv[1]+str(n))
        keyframelength = keyFrame.__len__()

        if (keyframelength < diffFrame.__len__()) and ((totalkeylength+keyframelength) < 18000): #tweak
            print "WRITING KEYFRAME"
            for keyByte in keyFrame:
                f_keys.write(struct.pack('B',keyByte))

            totalkeylength = totalkeylength + keyframelength
            updateLengths.append(keyframelength+0x8000)

        else:
            for frameByte in diffFrame:
                f_diffs.write(struct.pack('B',frameByte))

            updateLengths.append(diffFrame.__len__())

        os.remove(sys.argv[1]+str(n))
        
        print "Frame diff length:" + str(diffFrame.__len__())
        print "Keyframe length:" + str(keyframelength) + "\n"

    if n == 0:
        os.remove(sys.argv[1]+str(n))

    if n == numframes - 1:
        os.remove('frame'+str(n)+'.png')

#
# COMPOSE FINAL BINARY FILE
#

# Layout: [number of frames][lengths/encoding of compressed frames][length of all keyframes][keyframes][difference frames]

# how many frames are there? (remember to multiply by two in decoder to get length of next section)
updateLengths.insert(0,len(updateLengths)+1) #the '+1' includes the 'end of movie' mark for looping
updateLengths.append(0)
# keys must be prepended with total length of all keys -- same as appending to this part
updateLengths.append(totalkeylength)

# create list of 16-bit lengths for file
for i in range(updateLengths.__len__()):
    loByte = updateLengths[i]&0x00FF
    hiByte = updateLengths[i]>>8
    f_lengths.write(struct.pack('B',loByte))
    f_lengths.write(struct.pack('B',hiByte))

# close stuff
f_lengths.close()
f_keys.close()
f_diffs.close()

# open actual file we want to make, and then glom it all together
f_binary = open(sys.argv[1],"wb")
shutil.copyfileobj(open("blengths",'rb'), f_binary)
shutil.copyfileobj(open("bkeys",'rb'), f_binary)
shutil.copyfileobj(open("bdiffs",'rb'), f_binary)

os.remove("blengths")
os.remove("bkeys")
os.remove("bdiffs")

f_binary.close()
