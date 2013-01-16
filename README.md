IQ2GIF
======
This script allow to generate GIF animations from captured IQ signals. The signals must be stored as 16 bits for real and other 16 bits for imaginary IQ samples. 

#Usage

	usage: iq2gif.py [-h] [--seek OFFSET] [--frames N] [--loops N]
	                 [--duration TIME] [--impulse {RAW,DVB-T,DVB-T2,DAB}]
	                 [--bandwidth <signal_bw>@<capture_bw>]
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
	  --impulse {RAW,DVB-T,DVB-T2,DAB}
	                        Draw impulse response plot, if not set spectrum is
	                        drawn
	  --bandwidth <signal_bw>@<capture_bw>
	                        Define signal bandwidth and capture filter bandwigth	                        
#Example
![Spectrum Animation](https://raw.github.com/ikeralbeniz/IQ2GIF/master/images/default2013010216231g.gif)
![Impulse Response Animation](https://raw.github.com/ikeralbeniz/IQ2GIF/master/images/default2013010216231g_1.gif)