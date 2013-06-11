import Image
import ImageEnhance
import sys
import os
import shutil

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
        
frames = processImage(sys.argv[1])

im = Image.open('frame0.png')
bg = Image.new("RGB",im.size,(255,255,255))
bg.paste(im)

enhancer = ImageEnhance.Brightness(bg)
bg = enhancer.enhance(float(sys.argv[2]))

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
    new = enhancer.enhance(float(sys.argv[2]))
    
    new.save('frame'+str(i+1)+'.jpg')
    
#for i in range(frames+1):
    #os.unlink('frame'+str(i)+'.png')
    
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

# make last frame equal first, so we can loop
shutil.copy2('frame0.png','frame'+str(frames+1)+'.png')
shutil.copy2('frame0.jpg','frame'+str(frames+1)+'.jpg')
