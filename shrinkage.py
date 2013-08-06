#!/usr/bin/python

import os
import shlex
from time import time, sleep
import sys
from sys import stdout
from subprocess import Popen, PIPE
from qtrotate import get_set_rotation

FNULL = open(os.devnull, 'w')

def is_movie_file(filename, extensions=['.avi', '.AVI', '.mov', '.MOV']):
    return any((filename.endswith(e) and filename.find('.bak') == -1 and filename.find(".out") == -1) for e in extensions)

def find_movies(directory):
    for root, dirnames, filenames in os.walk(directory):
        for filename in filter(is_movie_file, filenames):
            yield os.path.join(root, filename)

def encode(input):
    size = os.path.getsize(input)
    try:
        rotation = get_set_rotation(input)
    except:
        return
    #if(time.time() - os.path.getctime(file) < 2592000.0):
    #  return
    print 'File: ' + input
    print 'Size: %s' % size
    print 'Rotatation: %s' % rotation
    print 'Time: %s' % time()
    print 'ctime: %s' % os.path.getctime(file)
    print 'Time Diff: %s' % (time() - os.path.getctime(file))
    parts = os.path.splitext(input)
    output = input
    tmp = parts[0] + '.out' + parts[1]
    backup = parts[0] + '.bak' + parts[1]
    if(os.path.exists(backup)):
        print 'Skipping already encoded file: ' + input
        return

    #do we need to rotate?
    filters = ""
    if rotation == 90:
        filters = "transpose=1"
    elif rotation == 180:
        filters = "vflip,hflip"
    elif rotation != 0:
        print 'Skipping file with rotation: %s' % rotation
        return
    if filters != "":
        filters = "-vf " + filters

    #do the encoding
    cmd = './ffmpeg -i \'{input}\' {filters} \'{output}\''.format(input=input,filters=filters,output=tmp)
    print "Command: " + cmd
    p = Popen(shlex.split(cmd), stdout=FNULL, stderr=PIPE)
    stdout.write("Encoding " + input + " ")
    stdout.flush()
    code = None
    while True:
        stdout.write(".")
        stdout.flush()
        sleep(.1)
        code = p.poll()
        if code is not None:
            break
    print ""

    print "Result: %s" % p.returncode
    if code == 0:
        #fix the rotation
        if rotation != 0:
            print "Adusting rotation to 0"
            get_set_rotation(tmp, 0)
        os.rename(input, backup) #save a backup just in case
        os.rename(tmp, input)
    else:
        #UNDO! UNDO!
        for line in p.stderr:
            print line
        os.remove(tmp)

if __name__ == '__main__':
    directory = sys.argv[1]
    for file in find_movies(directory):
        encode(file)

