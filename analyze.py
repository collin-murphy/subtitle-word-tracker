import os
import subprocess
from linecache import getline
from datetime import datetime
from source import SHOWS_DIR, SUBS_DIR

OUTPUT_DIR = "output"
TEMP_OUTPUT = "temp"
WORD = 'fart'
OUTPUT_FORMAT = 'mp4'
FINAL_OUTPUT_FNAME = f'output_{WORD}.{OUTPUT_FORMAT}'

class Instance:
    def __init__(self, sub_filepath: str, start: str, end: str, video_fname: str = ""):
        self.sub_filepath = sub_filepath
        self.start = start
        self.end = end
        self.video_fname = video_fname

# find the word in each file and put each instance in a list
def search_word_in_files(word, directory, instances):
    for subdir, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(subdir, file)
            with open(filepath, 'r') as f:
                count = 0
                for line in f:
                    count += 1
                    if word in line.lower():
                        instance = find_instance(count, filepath)
                        instances.append(instance)


def find_instance(count, filepath):
    temp_c = count - 1
    temp_l = getline(filepath, temp_c)
    time_stamp = getline(filepath, 1)

    while temp_c > 0:
        if temp_l == '\n':
            time_stamp = getline(filepath, temp_c + 2)
            break
        temp_c -= 1
        temp_l = getline(filepath, temp_c)
    timestamps = format_time(time_stamp)
    return Instance(filepath, timestamps[0], timestamps[1])


def format_time(time_stamp):
    if time_stamp.find(' --> ') == -1:
        print(f"Incorrect time stamp format: {time_stamp}")
        return
    start = time_stamp.split(' --> ')[0].replace(',', '.')
    end = time_stamp.split(
        ' --> ')[1].split('\n')[0].replace(',', '.')

    return [start, end]

#make sure output directory is ready for use
def create_output_dir():
    directory = f"{OUTPUT_DIR}/{TEMP_OUTPUT}"
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created successfully.")
    else:
        #delete files from temp directory
        cmd = f"rm -rf {directory}/*"
        subprocess.call(cmd, shell=True)
        print(f"Directory '{directory}' already exists.")

def find_episode(instance):
    sub_fname = instance.sub_filepath.rsplit('/')[-2]
    # Iterate over all files in the directory
    for filename in os.listdir(SHOWS_DIR):
        # Check if the filename contains the substring
        if sub_fname in filename:
            instance.video_fname = filename


def generate_clip(instance):
    input_video = SHOWS_DIR + instance.video_fname
    directory = f"{OUTPUT_DIR}/{TEMP_OUTPUT}"

    output_video = f"{directory}/{SHOWS_DIR.rsplit('/')[-2]}_{instance.start}_{instance.end}.{OUTPUT_FORMAT}"
    cmd = f'ffmpeg -y -i {input_video} -ss {instance.start} -to {instance.end} -c:v libx264 -c:a copy -movflags +faststart {output_video}'

    subprocess.call(cmd, shell=True)


def generate_clips(instances):
    for i in instances:
        generate_clip(i)


def combine_clips():
    # Set the directory containing the video files
    directory = f'{OUTPUT_DIR}/{TEMP_OUTPUT}'

    # Get a list of all video files in the directory
    videos = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(f'.{OUTPUT_FORMAT}')]

    # Set the output file name and path
    output_file = f"{OUTPUT_DIR}/{FINAL_OUTPUT_FNAME}"

    # Build the ffmpeg command to concatenate all the video files
    ffmpeg_command = ['ffmpeg']
    for video in videos:
        ffmpeg_command.extend(['-i', video])
    ffmpeg_command.extend(['-filter_complex', 'concat=n={}:v=1:a=1'.format(len(videos)), output_file])

    # Run the ffmpeg command using subprocess
    subprocess.run(ffmpeg_command, check=True)

    cmd = f"rm -rf {directory}"
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    instances = []
    print("Searching for instances of {WORD}...")
    search_word_in_files(WORD, SUBS_DIR, instances)
    print(f"Found {len(instances)} instances of {WORD}")

    create_output_dir()
    print("Generating video clips...")
    for i in instances:
        find_episode(i)

    generate_clips(instances)

    print("Combining video clips...")
    combine_clips() 
    print(f"Final output available at {OUTPUT_DIR}/{FINAL_OUTPUT_FNAME}")