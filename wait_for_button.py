import tkinter as tk

def main():
    window=tk.Tk()
    var = tk.IntVar()
    btn=tk.Button(window, text="Press after denoising...", command=lambda: var.set(1))
    btn.place(x=400, y=125)
    lbl=tk.Label(window, text="Now denoise the unpacked TIFF files using Topaz. Make sure the files are saved with 'DeNoiseAI' in the name, which Topaz does by default", font=("Helvetica", 9))
    lbl.place(x=60, y=50)
    lbl2=tk.Label(window, text="Press the button below to recompile the denoised TIFF files into IMS files", font=("Helvetica", 9))
    lbl2.place(x=60, y=75)

    window.title('Waiting for denoising')
    window.geometry("900x200+10+10")
    window.tkraise()

    # Wait for OK button to be pressed
    # btnOK.wait_variable(okVar) - this didn't work
    window.wait_variable(var)

    # Close frame
    window.destroy()
    # Show frame
