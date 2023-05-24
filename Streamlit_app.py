import os
import tkinter as tk
from dicttoxml import dicttoxml
from readlif.reader import LifFile
import streamlit as st


# Define a function to get the input directory
def get_input_directory():
    st.info("LIF Denoise Assist - input folder\nPlease select a folder containing the raw Leica image files (LIF files).")
    input_dir = st.sidebar.selectbox("Input folder", os.listdir())
    return input_dir


# Define a function to get the output directory
def get_output_directory():
    st.info("LIF Denoise Assist - output folder\nPlease select a folder in which to store the image slices.")
    output_dir = st.sidebar.selectbox("Output folder", os.listdir())
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
    st.title('Unpacking LIF files...')
    st.progress(0)

    st.subheader(update_progress_label(0))

    st.text(file_name(metadata, series_index, total_stacks))


def file_name(metadata, series_index, total_stacks):
    return str(series_index + 1) + "/" + str(total_stacks) + " " + metadata['name']


def update_progress_label(value):
    return f"{round(value, 1)}%"


def increment_progressbar(progress_label, file_label, metadata, total_stacks, value, current_stack):
    st.progress(value)
    progress_label.subheader(update_progress_label(value))
    file_label.text(file_name(metadata, current_stack, total_stacks))


# Define function to unpack LIF files
def process_lif_files(liffiles, input_dir, output_dir, total_slices, total_stacks, progress_label, file_label):
    """
    Parameters:
    liffiles (list): List of LIF file names to process
    input_dir(str): Path to input directory
    output_dir (str): Path to output directory
    total_slices (int): Total number of slices to process
    total_stacks (int): Total number of Z-stacks to process
    progress_label (Streamlit component): Percentage widget to update
    file_label (Streamlit component): File name widget to update
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
                    increment_progressbar(progress_label, file_label, metadata, total_stacks,
                                          100 / total_slices, current_stack)

                c += 1

            # Read and save metadata to an XML
            xml_metadata = dicttoxml(metadata)
            xml_decode = xml_metadata.decode()

            with open(os.path.join(output_dir, metadata['name'] + " metadata" + ".xml"), "w") as xmlfile:
                xmlfile.write(xml_decode)

            series_index += 1
            current_stack += 1


# Define function to unpack LIF files without progressbar, to be incorporated into new scripts

def main():
    st.sidebar.title("LIF Denoise Assist")
    input_dir = get_input_directory()
    output_dir = get_output_directory()
    liffiles = get_lif_files(input_dir)
    total_slices, total_stacks, total_channels, series_index, metadata = variable_initialization(input_dir, liffiles)
    total_slices, total_stacks = slice_counter(liffiles, input_dir, total_stacks, total_slices)

    create_gui(metadata, series_index, total_stacks)
    process_lif_files(liffiles, input_dir, output_dir, total_slices, total_stacks, st, st)


if __name__ == "__main__":
    main()