Hi!

DESCRIPTION:
This repository currently holds my EXTREMELY POORLY DOCUMENTED proof-of-concept python scripts 
(and 6502 video codec) for Apple II image conversion and animation. For now you're going to have 
to read the code to see how they work. Though I do plan on cleaning them up and giving them nicer 
command line interfaces.

USE:
As far as using this stuff for your own projects goes, just giving me a shoutout and a link to the
repo is fine. Bonus points if you'd like to email me about what you're up to, since I'll obviously
think it's cool. 'nategri' on everyone's favorite Mountain View, California based email service.

WHAT'S HERE:

hgrdither_alltogether.py:
Catchy name! Coverts an image that's already HiRes-sized to a binary an Apple II can push to the screen.
(i.e. you can BLOAD it in from a BASIC prompt)

outputframes.py:
Scrapes images out of an animated gif.

resizeoutputframes.py:
Resizes the output of outputframes.py

hgranimate.py:
Runs through what outputframes made, compresses and makes a binary that the codec can read.

videonewbuff.txt:
This is the assembly language codec that reads the file hgranimate makes. Can be assembled in MERLIN.
Oh, the blood sweat & tears that went into THIS thing. That said it is still *extrememly* rudimentary.