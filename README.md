IQ2GIF
======

#Explanation
This script allow to generate GIF animations from captured IQ signals. The signals must be stored as 16 bits for real and other 16 bits for imaginary IQ samples. 

#Usage
usage: iq2gif.py [-h] [--seek OFFSET] [--frames N] [--loops N]
                 [--duration TIME] [--impulse {DVB-T,DVB-T2,DAB}]
                 FILE

Convert IQ capture Spectrum or Impulse Response to GIF animation

positional arguments:
  FILE                  IQ file to read from

optional arguments:
  -h, --help            show this help message and exit
  --seek OFFSET         Startpoint of the IQ file to start from
  --frames N            Number of frames to be generated, if not set frames
                        will be genarated till end of file
  --loops N             Set number of loops of the animation, defaul is 0 that
                        means infinte loops
  --duration TIME       Time between frames
  --impulse {DVB-T,DVB-T2,DAB}
                        Draw impulse response plot, if not set spectrum is
                        drawn
