import os
import numpy as np
from PIL import Image
import tifffile
from natsort import natsorted
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
def get_input_directory():
    messagebox.showinfo("LIF Denoise Assist - input folder",
                        "Please select folder containing the individual denoised TIFF files. Press 'OK' to continue")
    input_dir = filedialog.askdirectory(title="Input folder") + "/"
    return input_dir


# Define a function to get the output directory
def get_output_directory():
    messagebox.showinfo("LIF Denoise Assist output folder",
                        "Please select folder to store rebuilt Z-stacks in. Press 'OK' to continue")
    output_dir = filedialog.askdirectory(title="Output folder") + "/"
    return output_dir


def get_tiff_list(input_dir):
    tiff_list = natsorted([os.path.join(input_dir, f) for f in os.listdir(input_dir) if 'DeNoiseAI' in f])
    return tiff_list


def get_lif_list(tiff_files):
    return list(dict.fromkeys([LIF.split(" LifID_C")[0] for LIF in tiff_files]))


def get_current_stack(tiff_files, LIF):
    return [tiff for tiff in tiff_files if LIF in tiff]


def get_tiff_files(current_tiffs, substring):
    return [tiff for tiff in current_tiffs if substring in tiff]


def update_progress_label(value):
    return f"{round(value, 1)}%"


def file_name(LIF, channel_number, input_dir):
    return "Compiling " + LIF.split(input_dir)[1] + " channel " + str(channel_number) + " into " + LIF.split(input_dir)[
        1] + ".ims"


def increment_progressbar(progressbar, progress_label, file_label, value, channel_number, LIF, input_dir):
    progressbar["value"] += value
    progress_label["text"] = update_progress_label(progressbar["value"])
    file_label['text'] = file_name(LIF, channel_number, input_dir)
    progressbar.update()


def create_gui(LIF, channel_number, input_dir):
    root = tk.Tk()
    root.geometry('900x100')
    root.title('Unpacking LIF files...')

    progressbar = ttk.Progressbar(root, length=800, cursor='spider', mode="determinate", orient=tk.HORIZONTAL)
    progressbar.grid(row=0, column=0)

    progress_label = ttk.Label(root, text=update_progress_label(0))
    progress_label.grid(column=0, row=1, columnspan=2)

    file_label = ttk.Label(root, text=file_name(LIF, channel_number, input_dir))
    file_label.grid(column=0, row=2, columnspan=2)
    increment_progressbar(progressbar, progress_label, file_label, 0, 1, LIF, input_dir)
    return root, progressbar, progress_label, file_label


def initialize_variables(LIF_files):
    channel_colors = ["Red", "Blue", "Green"]
    LIF = LIF_files[0]
    channel_number = 1
    return channel_colors, LIF, channel_number


def lif_rebuilder(LIF_files, tiff_files, channel_colors, progressbar, progress_label, file_label, output_dir,
                  input_dir):
    for LIF in LIF_files:
        channel_number = 0
        current_stack = get_current_stack(tiff_files, LIF)
        tiff_c0, tiff_c1, tiff_c2 = [get_tiff_files(current_stack, x) for x in ['LifID_C0',
                                                                                'LifID_C1',
                                                                                'LifID_C2',
                                                                                ]]
        active_channels = []
        active_colors = []
        for channel in [tiff_c0, tiff_c1, tiff_c2]:
            if len(channel) >= 1:
                active_channels.append(channel)
        c = 0
        for color in channel_colors:
            if c < len(active_channels):
                active_colors.append(color)
            c = + 1
        stacks = []
        for tiff_channel in reversed(active_channels):
            stack = [np.expand_dims(np.array(Image.open(f)), axis=2) for f in tiff_channel]
            stack = np.concatenate(stack, axis=2)
            stack = np.transpose(stack, (2, 0, 1, 3))
            stacks.append(stack)
            channel_number += 1
            increment_progressbar(progressbar, progress_label, file_label, 100 / len(LIF_files * len(active_channels)),
                                  channel_number, LIF, input_dir)
        stacked = np.stack(stacks, axis=0)
        stacked = np.transpose(stacked, (4, 1, 0, 2, 3))
        filename = output_dir + LIF.split(input_dir)[1] + " Denoised.ims"
        tifffile.imwrite(filename, stacked, metadata={}, ome=True)

def main():
    input_dir = get_input_directory()
    output_dir = get_output_directory()
    tiff_files = get_tiff_list(input_dir)
    LIF_files = get_lif_list(tiff_files)
    channel_colors, LIF, channel_number = initialize_variables(LIF_files)
    root, progressbar, progress_label, file_label = create_gui(LIF, channel_number, input_dir)
    lif_rebuilder(LIF_files, tiff_files, channel_colors, progressbar, progress_label, file_label, output_dir, input_dir)
    root.destroy()
    return

if __name__ == "__main__":
    main()
