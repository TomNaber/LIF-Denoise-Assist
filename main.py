import LIFUnpacker
import LIFRebuilder
import wait_for_button

def master_process():
    LIFUnpacker.main()
    wait_for_button.main()
    LIFRebuilder.main()


if __name__ == "__main__":
    master_process()
