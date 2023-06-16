# *************************************************************************** #
# *   Developed by Tom Naber                https://github.com/TomNaber     * #
# *   Pyott Lab                             https://www.thepyottlab.com/    * #
# *   Department of Otorhinolaryngology                                     * #
# *   University of Groningen                                               * #
# *   Current version: 1.0                                                  * #
# *   Last updated: 03-05-2023                                              * #
# *************************************************************************** #

"""
Python module to be used for processing Leica image files.

This python module can unpack LIF files, saving each slice as a TIFF file. The channel and slice number are retained in
the name of the resulting TIFF files. The metadata from each Z-stack contained in the LIF files is saved as an XML.
To execute this module, press run, select the folder containing LIF files and the folder to store the TIFF and XML files
in.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
from readlif.reader import LifFile


# Define a function to get the input directory
def get_input_directory():
    messagebox.showinfo("LIF Denoise Assist - input folder",
                        "Please select folder containing the raw Leica image files (LIF files). Press 'OK' to continue")
    input_dir = filedialog.askdirectory(title="Input folder") + "/"
    return input_dir


# Define a function to get the output directory
def get_output_directory():
    messagebox.showinfo("LIF Denoise Assist - output folder", "Please select folder in which to store the image "
                                                              "slices. Press 'OK' to continue")
    output_dir = filedialog.askdirectory(title="Output folder") + "/"
    return output_dir


# Get list of lif files in input directory
def get_lif_files(input_dir):
    liffiles = [file for file in os.listdir(input_dir) if file.endswith('.lif')]
    return liffiles


# Initialize variables to store metadata and progress information
def variable_initialization(input_dir, liffiles):
    total_slices = []
    total_stacks = []
    total_channels = []
    series_index = 0
    metadata = LifFile(os.path.join(input_dir, liffiles[0])).get_image(0).info
    return total_slices, total_stacks, total_channels, series_index, metadata


# Count the number of individual slices contained in the LIF files to accurately track progress
def slice_counter(liffiles, input_dir, total_stacks, total_slices):
    for file in liffiles:
        liffile = LifFile(os.path.join(input_dir, file))
        imagelist = liffile.image_list
        total_stacks.append(len(imagelist))
        sections = [z_slice['dims'][2] for z_slice in imagelist]
        channels = [z_slice['channels'] for z_slice in imagelist]
        for section, channel in zip(sections, channels):
            total_slices.append(section * channel)

    total_slices = sum(total_slices)
    total_stacks = sum(total_stacks)
    return total_slices, total_stacks


# Create GUI to show progress. Show progress in percentage, current stack name and current stack number
def create_gui(metadata, series_index, total_stacks):
    root = tk.Tk()
    root.geometry('900x100')
    root.title('Unpacking LIF files...')

    progressbar = ttk.Progressbar(root, length=800, cursor='spider', mode="determinate", orient=tk.HORIZONTAL)
    progressbar.grid(row=0, column=0)

    progress_label = ttk.Label(root, text=update_progress_label(0))
    progress_label.grid(column=0, row=1, columnspan=2)

    file_label = ttk.Label(root, text=file_name(metadata, series_index, total_stacks))
    file_label.grid(column=0, row=2, columnspan=2)

    return root, progressbar, progress_label, file_label


def file_name(metadata, series_index, total_stacks):
    return str(series_index + 1) + "/" + str(total_stacks) + " " + metadata['name']


def update_progress_label(value):
    return f"{round(value, 1)}%"


def increment_progressbar(progressbar, progress_label, file_label, metadata, total_stacks, value, current_stack):
    progressbar["value"] += value
    progress_label["text"] = update_progress_label(progressbar["value"])
    file_label['text'] = file_name(metadata, current_stack, total_stacks)
    progressbar.update()


# Define function to unpack LIF files
def process_lif_files_with_pb(liffiles, input_dir, output_dir, total_slices, total_stacks, progressbar, progress_label,
                              file_label):
    """
    Parameters:
    liffiles (list): List of LIF file names to process
    input_dir(str): Path to input directory
    output_dir (str): Path to output directory
    total_slices (int): Total number of slices to process
    total_stacks (int): Total number of Z-stacks to process
    progressbar (tkinter.ttk.Progressbar): Progress bar widget to update
    progress_label (tkinter.Label): Percentage widget to update
    File_label (tkinter.Label): File name widget to update
    """
    current_stack = 0

    # Loop over each LIF file
    for file in liffiles:
        liffile = LifFile(os.path.join(input_dir, file))
        series_length = len(liffile.image_list)
        series_index = 0

        # Loop over each stack in a LIF file
        while series_index < series_length:
            series = liffile.get_image(series_index)
            channel_list = [i for i in series.get_iter_c(z=0)]
            metadata = series.info
            c = 0

            # Loop over each channel in a stack
            while c < len(channel_list):
                z_stack = [i for i in series.get_iter_z(c=c)]
                i = 0

                # Loop over each slice in each channel in a stack
                for item in z_stack:
                    item.save(os.path.join(output_dir, metadata['name'] + f' LifID_C{c}-{i}.tiff'))
                    i += 1
                    increment_progressbar(progressbar, progress_label, file_label, metadata, total_stacks,
                                          100 / total_slices, current_stack)

                c += 1

            # Write metadata
            metadata_json = json.dumps(metadata, indent=4)
            with open(output_dir+"/"+metadata["name"]+".json", "w") as file:
                file.write(metadata_json)

            series_index += 1
            current_stack += 1


# Define function to unpack LIF files without progressbar, to be incorporated into new scripts

def main():
    input_dir = get_input_directory()
    output_dir = get_output_directory()
    liffiles = get_lif_files(input_dir)
    total_slices, total_stacks, total_channels, series_index, metadata = variable_initialization(input_dir, liffiles)
    total_slices, total_stacks = slice_counter(liffiles, input_dir, total_stacks, total_slices)

    root, progressbar, progress_label, file_label = create_gui(metadata, series_index, total_stacks)
    process_lif_files_with_pb(liffiles, input_dir, output_dir, total_slices, total_stacks, progressbar, progress_label,
                              file_label)
    root.destroy()
    return output_dir


if __name__ == "__main__":
    main()
