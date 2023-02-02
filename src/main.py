import os
import subprocess
import shutil

import colorama
from colorama import Fore

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


# for every file in inputs folder
for file in os.listdir(input_folder):
    # if file is a video file
    if file.endswith(".mp4"):
        # create the command
        input_file = os.path.join(input_folder, file)
        output_file = os.path.join(output_folder, file)

        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-b:a", "1k",
            "-vcodec", "libx264",
            "-crf", "40",
            "-s", "256x144",
            "-vf", "scale=1920:1080:flags=bicubic",
            output_file

        ]

        print(Fore.YELLOW + "Converting " + file + "..." + Fore.RESET)

        try:
            result = subprocess.run(ffmpeg_command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

            if result.returncode == 0:
                print(Fore.GREEN + "Successfully converted " + file + "." + Fore.RESET)
                # move input file to inputs/used folder
                shutil.move(input_file, os.path.join(used_input_folder, file))
            else:
                print(Fore.RED + "Failed to convert " + file + "." + Fore.RESET)
        except:
            print(Fore.RED + "Failed to convert " + file + "." + Fore.RESET)

print("")
print(Fore.GREEN + "Everything done." + Fore.RESET)
