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
    scr_text.delete('1.0', END)
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
        if src_path != '':
            scr_text.insert(INSERT, f'{src_path} > {dst_path}\n', src_path)
        scr_text.see(END)
        status = pc.copy_next()
        if status == PhotoCopy.STAT_FINISHED:
            break # We are done
        color = 'green'
        if status == PhotoCopy.STAT_EXISTED:
            color = 'yellow'
        elif status == PhotoCopy.STAT_FAILED:
            scr_text.insert(INSERT, f'  {pc.last_error}\n', src_path)
            color = 'red'
        scr_text.tag_config(src_path, foreground=color)
        update_stats()

    btn_run_stop.config(text="Run")
    running = False
    

###############################################################################
# UI Setup

root.geometry("1400x700")
root.title("Photo Copy")

# Top bar
frm_top = Frame(root)
frm_top.pack(fill=X)

# Source and Dest
frm_src_dst = Frame(frm_top)
frm_src_dst.pack(side=LEFT, fill=X, expand=True)

# Source
frm_src = Frame(frm_src_dst)
frm_src.pack(fill=X)

lbl_src = Label(frm_src, text ="Source", width = 6) 
lbl_src.pack(side=LEFT)
entry_src = Entry(frm_src,textvariable = str_src, font=('calibre',10,'normal'))
entry_src.pack(side=LEFT, fill=X, expand=True)
btn_select_src = Button(frm_src, text ="Select", command = cb_select_src)
btn_select_src.pack(side=RIGHT, padx=2)

# Destination
frm_dst = Frame(frm_src_dst)
frm_dst.pack(fill=X)

lbl_dst = Label(frm_dst, text ="Dest", width = 6) 
lbl_dst.pack(side=LEFT)
entry_dst = Entry(frm_dst,textvariable = str_dst, font=('calibre',10,'normal'))
entry_dst.pack(side=LEFT, fill=X, expand=True)
btn_select_dst = Button(frm_dst, text ="Select", command = cb_select_dst)
btn_select_dst.pack(side=LEFT, padx=2)

# Run / stop button
fnt_large = font.Font(family='Helvetica', size=20, weight=font.BOLD)
btn_run_stop = Button(frm_top, text ="Run", command = cb_run_stop, font=fnt_large, width=5)
btn_run_stop.pack(side=LEFT, padx=5)


# Stats
frm_stats = Frame(frm_top)
frm_stats.pack(side=RIGHT)

frm_stats1 = Frame(frm_stats)
frm_stats1.pack(fill=X)

frm_stats2 = Frame(frm_stats)
frm_stats2.pack(fill=X)

frm_stats3 = Frame(frm_stats)
frm_stats3.pack(fill=X)

fnt_small = font.Font(family='Helvetica', size=7)

frm_total = Frame(frm_stats1)
frm_total.pack(side=LEFT)
lbl_total = Label(frm_total, text ="Total:", font=fnt_small, width = 7) 
lbl_total.pack(side=LEFT)
lbl_total_val = Label(frm_total, text ="0", font=fnt_small, width = 5) 
lbl_total_val.pack(side=RIGHT)

frm_left = Frame(frm_stats1)
frm_left.pack(side=RIGHT)
lbl_left = Label(frm_left, text ="Left:", font=fnt_small, width = 7) 
lbl_left.pack(side=LEFT)
lbl_left_val = Label(frm_left, text ="0", font=fnt_small, width = 5) 
lbl_left_val.pack(side=RIGHT)

frm_copied = Frame(frm_stats2)
frm_copied.pack(side=LEFT)
lbl_copied = Label(frm_copied, text ="Copied:", font=fnt_small, width = 7)  
lbl_copied.pack(side=LEFT)
lbl_copied_val = Label(frm_copied, text ="0", font=fnt_small, width = 5)  
lbl_copied_val.pack(side=RIGHT)

frm_existed = Frame(frm_stats2)
frm_existed.pack(side=RIGHT)
lbl_existed = Label(frm_existed, text ="Existed:", font=fnt_small, width = 7)
lbl_existed.pack(side=LEFT)
lbl_existed_val = Label(frm_existed, text ="0", font=fnt_small, width = 5)
lbl_existed_val.pack(side=RIGHT)

frm_failed = Frame(frm_stats3)
frm_failed.pack(side=LEFT)
lbl_failed = Label(frm_failed, text ="Failed:", font=fnt_small, width = 7)
lbl_failed.pack(side=LEFT)
lbl_failed_val = Label(frm_failed, text ="0", font=fnt_small, width = 5)
lbl_failed_val.pack(side=RIGHT)

# Progress bar
progressbar = ttk.Progressbar(variable = progress)
progressbar.pack(fill=X, padx = 5, pady = 5)

# Status text entry
scr_text = ScrolledText(root)
scr_text.pack(fill=BOTH, expand = True)

root.mainloop()     