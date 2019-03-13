#!/usr/bin/python
import os
import subprocess
from datetime import datetime

# Make a temp/ directory for files we will create
if not os.path.exists('temp'):
    os.makedirs('temp')

##############################################################################
# Change these values ########################################################

# Names of videos in order
video_names = ['risen.mp4', 'our_king_has_come.mp4']
# Name of output file
output_name = 'April.mp4'

##############################################################################
##############################################################################

# List input files for the concat step later
with open(os.path.join('temp','input.txt'), 'w+') as g:
    for n in video_names:
        g.write('file \''+n+'\'\n')

rates = []
for n in video_names:
    # Get the audio sample rate (e.g. 44100 Hz, 48000 Hz)
    # If they are not the same, we need to change one
    # Otherwise the concat will mess up
    n_rate = subprocess.check_output(['ffprobe', '-v', 'error',
        '-select_streams', 'a:0', '-show_entries', 'stream=sample_rate', '-of',
        'default=noprint_wrappers=1:nokey=1', n])

    # Append the rate to the list
    rates.append(int(n_rate[:-1]))

# The sample rate of file0 is less than that of file1
if rates[0] < rates[1]:
    # Copy file0 without changing it
    subprocess.call(['ffmpeg', '-i', video_names[0], '-c', 'copy',
        os.path.join('temp', video_names[0])])
    
    # Reducce the audio sample rate of file1 and copy it
    subprocess.call(['ffmpeg', '-i', video_names[1], '-ar', str(rates[0]),
        '-c:v', 'copy', os.path.join('temp', video_names[1])])

# The sample rate of file0 is greater than that of file1
elif rates[0] > rates[1]:
    # Copy file1 without changing it
    subprocess.call(['ffmpeg', '-i', video_names[1], '-c', 'copy',
        os.path.join('temp', video_names[1])])
    
    # Reduce the audio sample rate of file0 and copy it
    subprocess.call(['ffmpeg', '-i', video_names[0], '-ar', str(rates[1]), '-c:v',
    'copy', os.path.join('temp', video_names[0])])

# The audio sample rates are equal, so no changes are needed
# You are Blessed!
else:
    for i,n in enumerate(video_names):
        subprocess.call(['ffmpeg', '-i', n, '-c', 'copy', os.path.join('temp',
            n)])

# Concatenate the videos together
subprocess.call(['ffmpeg', '-f', 'concat', '-i', os.path.join('temp',
    'input.txt'), '-c', 'copy', output_name])

