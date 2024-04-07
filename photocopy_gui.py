from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter.scrolledtext import ScrolledText

###############################################################################
# Create root

root = Tk()

###############################################################################
# Globals
str_src = StringVar()
str_dst = StringVar()

###############################################################################
# Call backs
def cb_select_src():
    src_path = filedialog.askdirectory(title = 'Source directory')
    if src_path != '' : str_src.set(src_path)

def cb_select_dst():
    dst_path = filedialog.askdirectory(title = 'Destination directory')
    if dst_path != '' :  str_dst.set(dst_path)

def cb_run_stop():
    btn_run_stop.config(text="Stop")
    pass


###############################################################################
# Main program

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
btn_run_stop.place(x=1100,y=10)

# Status text entry
scr_text = ScrolledText(root, width=137, height=25)
scr_text.place(x=5, y=110)
scr_text.insert(INSERT, 'First row\n')
scr_text.insert(INSERT, 'Second row\n')

root.mainloop()     