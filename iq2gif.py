import struct  
from numpy.fft import fft,fftshift
import matplotlib.pyplot as plt
from pylab import *
import time
import os
import argparse

try:
    import PIL
    from PIL import Image, ImageChops
    from PIL.GifImagePlugin import getheader, getdata
except ImportError:
    PIL = None

try:
    import numpy as np
except ImportError:
    np = None    


def intToBin(i):
    """ Integer to two bytes """
    # devide in two parts (bytes)
    i1 = i % 256
    i2 = int( i/256)
    # make string (little endian)
    return chr(i1) + chr(i2)


def getheaderAnim(im):
    """ Animation header. To replace the getheader()[0] """
    bb = "GIF89a"
    bb += intToBin(im.size[0])
    bb += intToBin(im.size[1])
    bb += "\x87\x00\x00"
    return bb


def getAppExt(loops=0):
    """ Application extention. Part that secifies amount of loops. 
    if loops is 0, if goes on infinitely.
    """
    bb = "\x21\xFF\x0B"  # application extension
    bb += "NETSCAPE2.0"
    bb += "\x03\x01"
    if loops == 0:
        loops = 2**16-1
    bb += intToBin(loops)
    bb += '\x00'  # end
    return bb


def getGraphicsControlExt(duration=0.1):
    """ Graphics Control Extension. A sort of header at the start of
    each image. Specifies transparancy and duration. """
    bb = '\x21\xF9\x04'
    bb += '\x01'  # no transparancy
    bb += intToBin( int(duration*100) ) # in 100th of seconds
    bb += '\x11'  # no transparant color
    bb += '\x00'  # end
    return bb


def _writeGifToFile(fp, images, durations, loops):
    """ Given a set of images writes the bytes to the specified stream.
    """
    
    # init
    frames = 0
    previous = None
    
    for im in images:
        
        if not previous:
            # first image
            
            # gather data
            palette = getheader(im)[1]
            data = getdata(im)
            imdes, data = data[0], data[1:]            
            header = getheaderAnim(im)
            appext = getAppExt(loops)
            graphext = getGraphicsControlExt(durations[0])
            
            # write global header
            fp.write(header)
            fp.write(palette)
            fp.write(appext)
            
            # write image
            fp.write(graphext)
            fp.write(imdes)
            for d in data:
                fp.write(d)
            
        else:
#            # gather info (compress difference)              
#            data = getdata(im) 
#            imdes, data = data[0], data[1:]       
#            graphext = getGraphicsControlExt(durations[frames])
#            
#            # write image
#            fp.write(graphext)
#            fp.write(imdes)
#            for d in data:
#                fp.write(d)

             # delta frame - does not seem to work
             delta = ImageChops.subtract_modulo(im, previous)            
             bbox = delta.getbbox()
             
             if bbox:
                 
                 # gather info (compress difference)              
                 data = getdata(im.crop(bbox), offset = bbox[:2]) 
                 imdes, data = data[0], data[1:]       
                 graphext = getGraphicsControlExt(durations[frames])
                 
                 # write image
                 fp.write(graphext)
                 fp.write(imdes)
                 for d in data:
                     fp.write(d)
                 
             else:
                 # FIXME: what should we do in this case?
                 pass
        
        # prepare for next round
        previous = im.copy()        
        frames = frames + 1

    fp.write(";")  # end gif
    return frames

def zoomImpulse(arrayvalues,reflevel=1.0):
    total = 0
    for i in arrayvalues:
        total = total + i

    partial = 0
    lateral = 0
    for i in arrayvalues:
        partial = partial + i
        percent = (partial * 100.0) / total
        if percent >= reflevel:
            return lateral
        lateral = lateral + 1
    return 0




def IQFile2Gif(filename, startpoint=0,frames=0,duration=0.1,loops=0,impulse=False,bandwidth=[1.0,1.0]):#,hiddeplot=False):

    images2 = []
    f = open(filename, 'rb')  

    f.seek(startpoint) 
    try:
        samples = []
        plt.ion()
        fig = plt.figure()
        if frames == 0:
            frames = f.size/(32768/4);
        for test in range(0,frames):
            samples = []
            for i in range(0,32768):
                short = f.read(2)
                i = struct.unpack('h', short)[0]
                short = f.read(2)
                q = struct.unpack('h', short)[0] 
                iq = complex(i * 0.05,q * 0.05)
                samples.append(iq)

            # FFT of the signal
            start = int((32768/bandwidth[1])*((bandwidth[1]-bandwidth[0])/2))
            end = int((32768/bandwidth[1])*(((bandwidth[1]-bandwidth[0])/2)+(bandwidth[0])))
            fftresult = fftshift(abs(fft(samples)))[start:end]

            #if impulse response is selected - TO BE DONE
            if impulse != None:
                if impulse == "RAW":
                    fftresult = fftshift(abs(fft(fftresult)))
                    lateral = zoomImpulse(fftresult,47.0)
                    fftresult = fftresult[lateral:len(fftresult)-lateral]
            #    if impulse == "DVB-T"
            #        fftresult = dvbt_impulse(fftresult)
            #    elif impulse == "DVB-T2"
            #        fftresult = dvbt2_impulse(fftresult)
            #    elif impulse == "DAB"
            #        fftresult = dab_impulse(fftresult)

            #clear plot and draw again
            plt.clf()
            ax = fig.add_subplot(1,1,1)
            line, = ax.plot(fftresult,'r-')
            ax.set_yscale('log')
            plt.draw()

            #save temfile to generate gif
            temmfile = str(time.time())+".jpg"
            plt.savefig(temmfile)
            im = Image.open(temmfile)
            im.convert('L')
            images2.append( im.convert('P', dither=1))
            os.remove(temmfile)

    finally:
        f.close()

    #generate GIF from image array
    durations = [duration for im in images2]
    nfileName, nfileExtension = os.path.splitext(filename)
    
    gif_file_name = nfileName+".gif"
    counter = 1
    while os.path.exists(gif_file_name):
        gif_file_name = nfileName+"_"+str(counter)+".gif"
        counter = counter +1

    fp = open(gif_file_name, 'wb')
        
    # write GIF
    try:
        n = _writeGifToFile(fp, images2, durations, loops)
    finally:
        fp.close()
   

if __name__ == '__main__':

    class bandwidth_parse(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            try:
                if values.find('@')>= 0:
                    params = values.split('@')
                    if len(params) != 2:
                        raise argparse.ArgumentError(self, "Invalid argument format: <signal_bw>@<capture_bw>")
                    result = [float(params[0]),float(params[1])]
                    setattr(namespace, self.dest, result)
                else:
                    raise argparse.ArgumentError(self, "Invalid argument format: <signal_bw>@<capture_bw>")
            except:
                raise argparse.ArgumentError(self, "Invalid argument format: <signal_bw>@<capture_bw>")
            
    parser = argparse.ArgumentParser(description='Convert IQ capture Spectrum or Impulse Response to GIF animation')

    parser.add_argument('filename', metavar='FILE', type=str,
                       help='IQ file to read from')
    parser.add_argument('--seek', dest='startpoint', metavar='OFFSET', type=int, default=0,
                       help='Startpoint of the IQ file to start from')
    parser.add_argument('--frames', dest='frames', metavar='N', type=int, default=0,
                       help='Number of frames to be generated, if not set frames will be genarated till end of file')
    parser.add_argument('--loops', dest='loops', metavar='N', default=0,
                       help='Set number of loops of the animation, defaul is 0 that means infinte loops')
    parser.add_argument('--duration', dest='duration', metavar='TIME', type=float, default=0.1,
                       help='Time between frames')
    parser.add_argument('--impulse', dest='impulse', choices=['RAW','DVB-T','DVB-T2','DAB'], default=None,
                   help='Draw impulse response plot, if not set spectrum is drawn')
    #parser.add_argument('--hiddeplot', dest='hiddeplot', action='store_true', default=False,
    #               help='Avoid showing ploting window')
    parser.add_argument('--bandwidth', metavar='<signal_bw>@<capture_bw>', dest='bandwidth', action=bandwidth_parse, default=[1.0,1.0],
                   help='Define signal bandwidth and capture filter bandwigth')
    args = parser.parse_args()

    IQFile2Gif(args.filename, args.startpoint, args.frames, args.duration, args.loops, args.impulse, args.bandwidth)#, args.hiddeplot)