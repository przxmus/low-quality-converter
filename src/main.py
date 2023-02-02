import os
import subprocess
import shutil
import threading
import time

import colorama
from colorama import Fore

# get global time in milliseconds
global_start_time = int(round(time.time() * 1000))

# def prompt(str):
#     valid_input = False
#     while not valid_input:
#         try:
#             number = int(input(str))
#             valid_input = True
#         except ValueError:
#             print(Fore.RED + "Incorrect input. Enter only numbers." + Fore.RESET)
#     return number
#
#
# quality = prompt("Enter quality (1-51) (BEST-WORST): ")
# if quality < 1:
#     quality = 1
# elif quality > 51:
#     quality = 51
#
# fps = prompt("Enter FPS: ")
# if fps < 1:
#     fps = 1

total_threads = 0
completed_threads = 0
threads_lock = threading.Lock()
threads_event = threading.Event()

src_folder = os.path.dirname(os.path.abspath(__file__))
root_folder = os.path.dirname(os.path.abspath(src_folder))
input_folder = os.path.join(root_folder, "inputs")
output_folder = os.path.join(root_folder, "outputs")
used_input_folder = os.path.join(input_folder, "used")
old_output_folder = os.path.join(output_folder, "old")

colorama.init()

# get number of files in output folder that are video files
num_files = len(
    [f for f in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, f)) and f.endswith(".mp4")])
print(Fore.GREEN + "Found " + str(num_files) + " converted videos.")
# get number of files in input folder that are video files
num_files = len([file for file in os.listdir(input_folder) if file.endswith(".mp4")])
print(Fore.GREEN + "Found " + str(num_files) + " video to convert." + Fore.RESET)
print("")
# for every file in output folder
for file in os.listdir(output_folder):
    # if file is video
    if file.endswith(".mp4"):
        # move it to old output folder
        shutil.move(os.path.join(output_folder, file), os.path.join(old_output_folder, file))
        print(Fore.YELLOW + "Moved " + file + " to old output folder." + Fore.RESET)

print("")


def convert(file):
    # get current time in milliseconds
    start_time = int(round(time.time() * 1000))
    # create the command
    input_file = os.path.join(input_folder, file)
    output_file = os.path.join(output_folder, file)

    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-b:a", "1k",
        "-vcodec", "libx264",
        "-crf", "35",
        "-s", "256x144",
        "-vf", "scale=1920:1080:flags=bicubic",
        "-r", "15",
        output_file

    ]

    print(Fore.YELLOW + "Converting " + file + "..." + Fore.RESET)

    try:
        result = subprocess.run(ffmpeg_command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        if result.returncode == 0:
            end_time = int(round(time.time() * 1000))
            # get time difference and format it
            time_diff = time.strftime('%H:%M:%S', time.gmtime((end_time - start_time) / 1000))

            print(Fore.GREEN + "Successfully converted " + file + " in " + time_diff + "." + Fore.RESET)
            # move input file to inputs/used folder
            shutil.move(input_file, os.path.join(used_input_folder, file))
        else:
            print(Fore.RED + "Failed to convert " + file + "." + Fore.RESET)
    except:
        print(Fore.RED + "Failed to convert " + file + "." + Fore.RESET)

    # Increment number of completed threads
    with threads_lock:
        global completed_threads
        completed_threads += 1

    # Check if all threads have finished
    if completed_threads == total_threads:
        threads_event.set()


# for every file in inputs folder
for file in os.listdir(input_folder):
    # if file is a video file
    if file.endswith(".mp4"):
        total_threads += 1
        # convert file in new thread
        threading.Thread(target=convert, args=(file,)).start()
    if total_threads == 0:
        threads_event.set()

threads_event.wait()
print("")
# get global end time
global_end_time = int(round(time.time() * 1000))
# get time difference and format it
global_time_diff = time.strftime('%H:%M:%S', time.gmtime((global_end_time - global_start_time) / 1000))
print(Fore.GREEN + "Everything done in " + global_time_diff + "." + Fore.RESET)
