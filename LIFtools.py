import os
from PIL import Image
from dicttoxml import dicttoxml
from readlif.reader import LifFile
from timeit import default_timer as timer
import numpy as np
import tifffile

def lif_unpacker(liffiles, input_dir, output_dir):
    """
    This function is to be called when importing this script as a module rather than a standalone application
    """
    start = timer()
    current_stack = 1

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
            print("Processing " + metadata['name'])
            # Loop over each channel in a stack
            while c < len(channel_list):
                z_stack = [i for i in series.get_iter_z(c=c)]
                i = 0

                # Loop over each slice in each channel in a stack
                for item in z_stack:
                    item.save(os.path.join(output_dir, metadata['name'] + f' LifID_C{c}-{i}.tiff'))
                    i += 1

                c += 1

            # Read and save metadata to an XML
            xml_metadata = dicttoxml(metadata)
            xml_decode = xml_metadata.decode()

            with open(os.path.join(output_dir, metadata['name'] + " metadata" + ".xml"), "w") as xmlfile:
                xmlfile.write(xml_decode)

            series_index += 1
            current_stack += 1
    end = timer()
    print("Finished unpacking " + str(current_stack-1) + " Z-stacks from " + str(len(liffiles)) + " LIF files in " +
          str(round(end - start, 2)) + " seconds")

def lif_rebuilder(tiff_files,input_dir,output_dir):
    LIF_files = list(dict.fromkeys([LIF.split(" LifID_C")[0] for LIF in tiff_files]))
    channel_colors = ["Red", "Blue", "Green"]
    start = timer()

    for LIF in LIF_files:
        print("Rebuilding " + str(LIF))
        current_stack = [tiff for tiff in tiff_files if LIF in tiff]
        tiff_c0, tiff_c1, tiff_c2 = [[tiff for tiff in current_stack if x in tiff]for x in ['LifID_C0',
                                                                                'LifID_C1',
                                                                                'LifID_C2',
                                                                                ]]
        active_channels = []
        active_colors = []
        for channel in [tiff_c0, tiff_c1, tiff_c2]:
            if len(channel) >= 1:
                active_channels.append(channel)
        c=0
        for color in channel_colors:
            if c < len(active_channels):
                active_colors.append(color)
            c =+ 1
        stacks = []
        for tifff_channel in reversed(active_channels):
            stack = [np.expand_dims(np.array(Image.open(input_dir+f)), axis=2) for f in tifff_channel]
            stack = np.concatenate(stack, axis=2)
            stack = np.transpose(stack, (2, 0, 1))
            stacks.append(stack)
        stacked = np.stack(stacks, axis=0)
        stacked = np.transpose(stacked, (1, 0, 2, 3))
        filename = output_dir + LIF + ".tiff"
        tifffile.imwrite(filename, stacked, metadata={},ome=True)
    end = timer()
    print("Finished rebuilding " + str(len(LIF_files)) + " TIFF files from " + str(len(tiff_files)) + " tiff files in " +
          str(round(end - start, 2)) + " seconds")