#!/usr/bin/python
import os
import subprocess
from datetime import datetime

if not os.path.exists('temp'):
    os.makedirs('temp')

##############################################################################
# Change these values ########################################################

# Name of lyric file
lyric_name = 'risen.txt'
# Name of audio file
song_name = 'risen.mp3'
# Name of background video
background_video = 'background.mp4'

##############################################################################
##############################################################################

# Read the lyric file
with open(lyric_name, 'r') as f:
    text = f.read()

break_string = '\n\n<'
i = 0
start = 0
dt = []
while i < 100:
    # Find where the slide starts
    stop = text.find(break_string,start)
    # Get timestamp from slide
    time = text[start+1:start+11]
    # Extract time in a useful format
    dt.append(datetime.strptime(time, '<%M:%S.%f>'))
    # Generate filename for lyric text
    name = '{:02d}.txt'.format(i)
    # Get lyrics
    out = text[start+12:stop].replace(break_string,'')
    # Save individual slide of lyrics
    with open(os.path.join('temp',name), 'w+') as ff:
        ff.write(out)
        # Add empty lines to force text higher on screen
        ff.write('\n\n\n')

    start = stop+1
    i += 1
    # Stop iterating after we reach the end of the file
    if stop is -1:
        break

diff_time = []
# Find the difference between timestamps to get duration
for i, t in enumerate(dt):
    if i is 0:
        diff_time.append(t - datetime(1900, 1, 1, 0, 0, 0))
    else:
        diff_time.append(t - dt[i-1])

# Write ffmpeg input file with lyric_names and durations
with open(os.path.join('temp','times.txt'), 'w+') as g:
    for j, item in enumerate(diff_time[1:]):
        g.write('file {:02d}.png\nduration '.format(j))
        g.write(str(item.total_seconds()))
        g.write('\n')
    g.write('file {:02d}.png'.format(j+1))

# Make images from all text files
for f in range(i+1):
    subprocess.call(['convert', '-size', '1920x1080', '-background',
    'transparent', '-fill', 'white', '-stroke', 'black', '-strokewidth', '3',
    '-font', 'roboto-black', '-gravity', 'Center',
    'caption:@'+os.path.join('temp', '{:02d}.txt'.format(f)),
    os.path.join('temp','{:02d}.png'.format(f))])

# Join images together as a video
subprocess.call(['ffmpeg', '-hide_banner', '-f', 'concat', '-i', os.path.join('temp',
    'times.txt'), '-r', '24',
    '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-metadata:s:v:0',
    'alpha_mode="1"', '-b:v', '2M', os.path.join('temp','lyrics.webm')])


# Find duration of video to know how long to loop background
duration = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
    'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
    '-sexagesimal', song_name])

# Make proper background video loop
subprocess.call(['ffmpeg', '-hide_banner', '-stream_loop', '-1', '-i',
    background_video, '-c',
    'copy', '-t', duration[:-1], os.path.join('temp', 'background_looped.mp4')])

# Add sound to background 
subprocess.call(['ffmpeg', '-hide_banner', '-i',
    os.path.join('temp','background_looped.mp4'), '-i', song_name, '-c:v', 'copy',
    os.path.join('temp', 'background_looped_sound.mp4')])

# Overlay video on background
subprocess.call(['ffmpeg','-hide_banner', '-i', os.path.join('temp',
    'background_looped_sound.mp4'), '-c:v',
    'libvpx-vp9', '-i', os.path.join('temp', 'lyrics.webm'), '-filter_complex', 'overlay',
    lyric_name[:-4]+'.mp4'])

