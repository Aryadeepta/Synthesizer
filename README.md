# Synthesizer
## Contributors
I, Aryadeepta De, am the sole contributor
## Potential Applications
There are many applicable applications of my project. One example is that one could design a useful sound, such as a sound effect for a button on an elevator.
Also, as demonstrated by Demo2, one could use it as a crude way to pirate music, such as my rendition of "Still D.R.E" by Dr. Dre ft. Snoop Dogg. If one had the time and patience, they could use topics taught in this very class to perfectly recreate any sound.
## Installation
My code is entirely contained in the file ECE45_Synthesizer.py. You can retrieve this file by either cloning this repository, or by directly copying the source code.
## Basic Usage
The menus are pretty simplistic, but here is a general rundown.
For any of the file management options, simply enter the id written in brackets next to the name of the file you wish to play, destroy, download, or plot.
For any of the audio inputs, follow the exact wordings of the prompts, with another note/chord on each new line.
Additionally, there are 3 supported instruments, the sine wave, sawtooth wave, and square wave. Please select which to use.
Moreover, there is implementation of an ADSR (Attack Delay Sustain and Release). I have a pretty good one in by default, but you are also welcome to use your own. There is technically implementation of a logarithmic ADSR, but it sounds terrible.
For the sample modification options, follow the above general ideas, plus make sure to follow the rules stated by the application.
For the filters, a low pass filters out any frequencies below the low, a high pass filters anything above the high, and a band pass filters out anything not between low and high. The pitch multiplier filter does not do any actual filtering, but instead shrinks the frequency domain about the x-axis by the multiplier, so that the pitch of the resulting sample is multiplied by m. For a power of 2, this is harmonic. For anything else, this sounds demonic.
At any point, if you wish to quit, check if there is an option to do so, and then select that option, or if you are feeling fancy, select 'Q' or 'q'.
For y/n questions, there is also support for 'Y/N' and 'y/n'
## Application of ECE45
The main applications of ECE45 were in the pitch filtering functions. The three filters were classics amongst those taught to us in class, and all 4 pitch functions used transforms in the frequency domain via Fourier Transform and Inverse Fourier Transform.
## Citations
I used the math, pyaudio, matplotlib, numpy, and scipy libraries. I did not use any other help.
