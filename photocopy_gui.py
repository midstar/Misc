from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from photocopy import PhotoCopy

import threading

###############################################################################
# Create root

root = Tk()

###############################################################################
# Globals

str_src = StringVar()
str_dst = StringVar()
progress = IntVar()
running = False
pc = None
thread = None

###############################################################################
# Helpers

def update_stats():
    if pc == None:
        return
    
    lbl_total_val.config(text=str(len(pc.src_paths)))
    lbl_left_val.config(text=str(pc.files_left()))
    lbl_copied_val.config(text=str(len(pc.success)))
    lbl_existed_val.config(text=str(len(pc.already_existed)))
    lbl_failed_val.config(text=str(len(pc.failed)))

    progress.set(pc.get_progress())
    root.update()

###############################################################################
# Call backs

def cb_select_src():
    src_path = filedialog.askdirectory(title = 'Source directory')
    if src_path != '' : str_src.set(src_path)

def cb_select_dst():
    dst_path = filedialog.askdirectory(title = 'Destination directory')
    if dst_path != '' :  str_dst.set(dst_path)

def cb_run_stop():
    global pc
    global running
    global thread
    if running:
        running = False # Thread will die
        return

    if str_src.get() == '' or str_dst.get() == '':
        messagebox.showerror(title='Error', message='Invalid source or dest')
        return

    btn_run_stop.config(text="Stop")
    pc = PhotoCopy(str_src.get(), str_dst.get())
    update_stats()
    running = True
    thread = threading.Thread(target=thrd_copy)
    thread.start()

###############################################################################
# Threads

def thrd_copy():
    global pc
    global running

    while running:
        src_path, dst_path = pc.get_next_file()
        scr_text.insert(INSERT, f'{src_path} > {dst_path}\n')
        status = pc.copy_next()
        if status == PhotoCopy.STAT_FINISHED:
            break # We are done
        update_stats()

    btn_run_stop.config(text="Run")
    running = False
    

###############################################################################
# UI Setup

root.geometry("1400x700")
root.title("Photo Copy")

# Source
lbl_src = Label(root, text ="Source") 
lbl_src.place(x=5,y=6)
entry_src = Entry(root,textvariable = str_src, font=('calibre',10,'normal'), width = 90)
entry_src.place(x=65,y=6)
btn_select_src = Button(root, text ="Select", command = cb_select_src)
btn_select_src.place(x=975,y=2)

# Destination
lbl_dst = Label(root, text ="Dest") 
lbl_dst.place(x=5,y=46)
entry_dst = Entry(root,textvariable = str_dst, font=('calibre',10,'normal'), width = 90)
entry_dst.place(x=65,y=46)
btn_select_dst = Button(root, text ="Select", command = cb_select_dst)
btn_select_dst.place(x=975,y=42)

# Run / stop button
fnt_large = font.Font(family='Helvetica', size=26, weight=font.BOLD)
btn_run_stop = Button(root, text ="Run", command = cb_run_stop, font=fnt_large, width=5)
btn_run_stop.place(x=1070,y=10)

# Stats
fnt_small = font.Font(family='Helvetica', size=8)

lbl_total = Label(root, text ="Total:", font=fnt_small) 
lbl_total.place(x=1260,y=2)
lbl_total_val = Label(root, text ="0", font=fnt_small) 
lbl_total_val.place(x=1310,y=2)

lbl_left = Label(root, text ="Left:", font=fnt_small) 
lbl_left.place(x=1260,y=18)
lbl_left_val = Label(root, text ="0", font=fnt_small) 
lbl_left_val.place(x=1310,y=18)

lbl_copied = Label(root, text ="Copied:", font=fnt_small) 
lbl_copied.place(x=1260,y=34)
lbl_copied_val = Label(root, text ="0", font=fnt_small) 
lbl_copied_val.place(x=1310,y=34)

lbl_existed = Label(root, text ="Existed:", font=fnt_small) 
lbl_existed.place(x=1260,y=50)
lbl_existed_val = Label(root, text ="0", font=fnt_small) 
lbl_existed_val.place(x=1310,y=50)

lbl_failed = Label(root, text ="Failed:", font=fnt_small) 
lbl_failed.place(x=1260,y=66)
lbl_failed_val = Label(root, text ="0", font=fnt_small) 
lbl_failed_val.place(x=1310,y=66)

# Progress bar
progressbar = ttk.Progressbar(variable = progress)
progressbar.place(x=5, y=90, width=1390)

# Status text entry
scr_text = ScrolledText(root, width=137, height=25)
scr_text.place(x=5, y=110)

root.mainloop()     