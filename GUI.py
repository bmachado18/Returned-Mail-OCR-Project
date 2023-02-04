import tkinter as tk
from tkinter import HORIZONTAL, filedialog, ttk, messagebox, PhotoImage
import threading

import os
import shutil, sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import GetAppeal 
import main

appeal_path = ""
APPEAL_DATAFRAME = pd.DataFrame(columns=['Name', 'Address Line 1', 'Address Line 2', 'Address Line 3', "Appeal_ID", "Consituent_ID"])

"""delete_tmp
deletes the temporary folders with the appeals and the envelopes

params: nothing

returns: nothing
"""
def delete_tmp():
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')
    return

"""browseFiles
opens the file explorer to select a pdf file, and updates the appeal path accordingly

params: the appeal path label

returns: nothing
"""
def browseFiles(app_path_lbl):
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("pdf files","*.pdf*"),
                                                       ("all files","*.*")))
    if bool(filename):
        app_path_lbl['text'] = ' Selected ' + filename
        global appeal_path
        appeal_path = filename

# exclusively for a responsive gui
def on_enter(e):
    e.widget['background'] = 'green'

def on_leave(e):
    e.widget['background'] = 'SystemButtonFace'

# resets the appeal path so nothing is selected
def reset_app(app_path_lbl):
    global appeal_path
    appeal_path = ""
    app_path_lbl["text"]="No file selected"

class MainApplication(tk.Frame):
    
    def __init__(self, master, *args, **kwargs):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.create_widgets()
    
    def configure_gui(self):
        self.master.title("Returned Mail Automation System")
        self.master.resizable(False, False)

    def create_widgets(self):

        def read():
            try:
                statusLabel['text'] = "Status: In Progress"
                run_btn['state'] = 'disable'
                progress_bar.start()
                global APPEAL_DATAFRAME
                APPEAL_DATAFRAME = main.start(appeal_path, APPEAL_DATAFRAME)
                progress_bar.stop()
                table_status['text'] = str(len(APPEAL_DATAFRAME.index)) + " rows"
                run_btn['state'] = 'normal'
                statusLabel['text'] = "Status: Complete"
            except NameError as e2:
                print(e2)
                progress_bar.stop()
                run_btn['state'] = 'normal'
                statusLabel['text'] = "Status: Not Running"
                messagebox.showinfo("NameError", "No Appeal Path Selected")
            except Exception as e:
                progress_bar.stop()
                run_btn['state'] = 'normal'
                statusLabel['text'] = "Status: Not Running"
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(e)
                messagebox.showinfo("error", "Something happened. Please check your pdf's and try again")

        main_window = tk.Frame(self.master, padx = 20, pady = 20)
        tk.Label(main_window)

        welcome_lbl = tk.Label(main_window,text="Welcome! To get started, find the appeals PDF", font = "Verdana 10")
        welcome_lbl.grid(row=0, column=0, columnspan=2, pady=(0,10))

        appeal_nav_btn = tk.Button(main_window, text="Please select the PDF for the Appeal", command=lambda: browseFiles(appeal_path_lbl), width = 40, height=2,relief = "groove",font = "Verdana 10", bd = 2)
        appeal_nav_btn.grid(row=1, column=0, columnspan=2, pady=(20,0))

        appeal_path_lbl = tk.Label(main_window, text="No file selected",font = "Verdana 10", width=40)
        appeal_path_lbl.grid(row=3, column=0, columnspan=2, pady=(10, 15))

        add_xlxs_btn = tk.Button(main_window, text="Create excel file",command=lambda: (APPEAL_DATAFRAME.to_excel("returned_mail_output.xlsx")), width=30, height=2, relief = "groove",font = "Verdana 10", bd = 2)
        add_xlxs_btn.grid(row=6, column=0, columnspan=2, pady=(0, 10), padx = (0, 5))

        status_box = tk.Frame(main_window, bd=5, borderwidth=10,bg='gray')
        status_box.grid(row=7, column=0, columnspan=2, rowspan=2,pady=(0,10))

        reset_appPath_btn = tk.Button(main_window,text="Cancel",command = lambda: reset_app(appeal_path_lbl),width = 10, height=2,relief = "groove",font = "Verdana 10", bd = 2)
        reset_appPath_btn.grid(row=4, column=0, columnspan=2)

        exit_button = tk.Button(main_window, text="Exit", command=root.destroy, width=30, height=2,relief = "groove",font = "Verdana 10", bd = 2)
        exit_button.grid(row=9, column=1, pady=(0,10), padx = (5, 0))

        delete_button = tk.Button(main_window, text="Delete Images", command=lambda:delete_tmp(), width=30, height=2,relief = "groove",font = "Verdana 10", bd = 2)
        delete_button.grid(row=9, column=0, pady=(0,10))


        appeal_nav_btn.bind("<Enter>", on_enter)
        appeal_nav_btn.bind("<Leave>", on_leave)
        exit_button.bind("<Enter>", on_enter)
        exit_button.bind("<Leave>", on_leave)
        reset_appPath_btn.bind("<Enter>", on_enter)
        reset_appPath_btn.bind("<Leave>", on_leave)
        add_xlxs_btn.bind("<Enter>", on_enter)
        add_xlxs_btn.bind("<Leave>", on_leave)
        delete_button.bind("<Enter>", on_enter)
        delete_button.bind("<Leave>", on_leave)


        run_btn = tk.Button(main_window, text="Scan Files", command=lambda: threading.Thread(target=read).start(), width=30, height=2,relief = "groove",font = "Verdana 10", bd = 2)
        run_btn.grid(row=5, column=0, pady=15, columnspan=2)

        run_btn.bind("<Enter>", on_enter)
        run_btn.bind("<Leave>", on_leave)

        progress_bar = ttk.Progressbar(status_box, orient=HORIZONTAL, length=300, mode='indeterminate')
        progress_bar.grid(row=0, column=0, columnspan=2)
        statusLabel = tk.Label(status_box, text="Status: Not Running",font = "Verdana 10")
        statusLabel.grid(row=1, column=0, columnspan=2, pady=(10,0))
        table_status = tk.Label(status_box, font="Verdana 10", text="0 rows")
        table_status.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        main_window.pack()
        

if __name__ == '__main__':
   root = tk.Tk()
   main_app =  MainApplication(root)
   root.mainloop()