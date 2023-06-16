import LIFUnpacker
import LIFRebuilder
import wait_for_button

def master_process():
    metadata_dir = LIFUnpacker.main()
    wait_for_button.main()
    LIFRebuilder.main(metadata_dir)


if __name__ == "__main__":
    master_process()
