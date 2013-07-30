Hello!

This directory contains the nearly-mature version of my animated GIF converter and player for 8-bit Apple II computers.

Nategri's Apple II Vidplayer was designed to work on virtually every Apple II ever produced, and to play completely arbitrary video
clips, given that they fit in the available memory.


FILES:


a2vid.do:

140kB Apple II disk image that contains ProDOS, player sources (Merlin format), the player, and two sample videos


hgranimate.py:

Python script to convert appropriately resized GIF files into something useable by the player


a2vidplayer.txt:

6502 assembler sources for the video player (same as on disk image, but ASCII readable for convenience)



USAGE:


A2VID.sYSTEM (the player):

Works on any Apple II system with a 16kB'language card' equivalent (almost all), and access to 64kB or greater RAM disk.
Before first playback hit enter at prompt to set the name of this disk on your system (set to '/RAM' by default). This
is then saved to the disk and should only need to be done again if you change systems or hardware. Type the name of the file
you wish to play. Hit a key to stop playback and return to the selection screen.


hgranimate.py:

Run as 'python hgranimate.py' from a command prompt. If run with no arguments it will generate this 'help' output:
'USAGE: hgrdither.py [outputfilename] [inputgif] [brightness (float of order 1.0)] [videosize (normal,small,tiny)]'

NOTE: There is now a final (mandatory) option that sets a threshhold for what bytes are updated (range: 0-255). Start this at 30 and lower it if you get animations that are too 'lossy.' Increasing improves compression at the cost of clarity.

'videosize' adjusts the size of black borders around the animation. This helps with file size. Example files were created with 'small'.

IMPORTANT: Images must first be manually converted to a size of 280x192.
ALSO IMPORTANT: Program depends on 'PIL,' the Python Image Library.

FIDDLY NOT-MATURE SOFTWARE THING: The '30' in 'colorDistance > 30' on line 568 is a good thing to tweak for file size/visuals. It has to
do with which parts of an image are candidates for a refresh in each frame. '15' I think was my standard for a while.

In its current state it throws a bunch of debug stuff at the screen when run. And yes, I'm too lazy to remove it right now.
(Also: it makes a TON of files and deletes them as it goes.)

Output from this script can be then be loaded onto a disk image (don't forget the '.V' suffix!) with Ciderpress or Whatever.



BUGS:


None that I know of! But: Currently the software is limited to playing files with less than 224 frames.



TO DO:


Add that 'colorDistance > 30' nonsense as a command line argument. (DONE)

^Put this in the 'help' message output soon D:

Kill all the 'debug' type stuff it pipes to screen when running.

Make it so funtions are passed relevant objects, instead of pulling in ephemeral garbage files.

Increase max number of frames (with some fancy procedurally generated portions of the binary to free up space?)

Add the other two colors (This would be HARD, so don't hold yer breath.)



AUTHOR:


Me: Nathan Griffith. My email is 'nategri' at the email service run by everyone's favorite Mountain View, California company.



LICENSE:


I give everyone permission to use and and modify this software, provided they at least give me a shoutout somewhere.

PIL (PYTHON IMAGING LIBRARY) STUFF

The Python Imaging Library (PIL) is

    Copyright © 1997-2011 by Secret Labs AB
    Copyright © 1995-2011 by Fredrik Lundh