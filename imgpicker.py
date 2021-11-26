import os
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from imggrabber import ImgFolder, load_image, load_tk_image

class PickerData():
    def __init__(self, label, assignment):
        self.label = label
        self.assignment = assignment

class Picker(tk.Button):
    def __init__(self, data=None, master=None, *args, **kwargs):
        if not isinstance(master, PickerFrame):
            raise TypeError("Picker buttons can only assigned to a PickerFrame !")
        if not data:
            data = PickerData("INVALID", "invalid")
        tk.Button.__init__(self, master, *args, **kwargs)
        self.assignment = data.assignment
        self["text"] = data.label
        self["command"] = self.emit

    def emit(self, assignment=None):
        if not assignment:
            assignment = self.assignment
        self.master.process(assignment)

PYIMGPICKER_DEFAULT_PICKERDATA =  {
            "left": PickerData("KEEP", "keep"),
            "right": PickerData("DISCARD", "discard"),
            "up": PickerData("NEED PROCESSING", "needprocessing"),
            "down": PickerData("INCOMPLETE", "incomplete"),
}

class PickerFrame(tk.Frame):
    def __init__(self, commands=PYIMGPICKER_DEFAULT_PICKERDATA, master=None, *args, **kwargs):
        if not isinstance(master, ImgPicker):
            raise TypeError("Picker frames can only be assigned to an ImgPicker !")
        tk.Frame.__init__(self, master, *args, **kwargs)

        ## Create the picker buttons (layout inspired by playstation controllers)
        self.left = Picker(
            data=commands["left"],
            master=self,
            bg='green',
        )
        self.right = Picker(
            data=commands["right"],
            master=self,
            bg='red',
        )
        self.up = Picker(
            data=commands["up"],
            master=self,
            bg='yellow', fg='black',
        )
        self.down = Picker(
            data=commands["down"],
            master=self,
            bg='blue',
        )
        ## Place buttons in the frame
        self.left.grid(
            row=2, column=0,
            padx=20, pady=5,
        )
        self.right.grid(
            row=2, column=1,
            padx=20, pady=5,
        )
        self.up.grid(
            row=1, column=0, columnspan=2,
        )
        self.down.grid(
            row=3, column=0, columnspan=2,
        )

    def process(self, assignment):
        self.emit(assignment)

    def emit(self, assignment):
        self.master.process(assignment)

class TopFrame(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        if not isinstance(master, ImgPicker):
            raise TypeError("Top frame can only be asigned to an ImgPicker !")
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.columnconfigure((0,2), weight=1)
        self.columnconfigure(1, weight=5000)

        self.frame_l = tk.Frame(self)
        self.btn_src = tk.Button(self.frame_l,
            text="Source Folder",
            command=lambda: master.cmd_set_folder("source"),
        )
        self.btn_src.pack(pady=5, fill="both")
        self.btn_dst = tk.Button(self.frame_l,
            text="Destination Folder",
            command=lambda: master.cmd_set_folder("destination"),
        )
        self.btn_dst.pack(pady=5, fill="both")

        self.frame_m = tk.Frame(self)
        self.lbl_src = tk.Label(self.frame_m)
        self.lbl_src.grid(pady=(0, 10), sticky="w")
        self.lbl_dst = tk.Label(self.frame_m)
        self.lbl_dst.grid(pady=(10, 0), sticky="w")

        self.frame_r = tk.Frame(self)
        self.btn_commit = tk.Button(self.frame_r,
            text="Commit",
            command=master.cmd_commit,
        )
        self.btn_commit.pack(pady=5, fill="both")
        self.btn_reset = tk.Button(self.frame_r,
            text="Reset",
            command=lambda: master.reset(master.cur_src_folder)
        )
        self.btn_reset.pack(pady=5, fill="both")

        self.frame_l.grid(row=0, column=0, padx=(10, 0), sticky="w")
        self.frame_m.grid(row=0, column=1, sticky="w")
        self.frame_r.grid(row=0, column=2, padx=(0, 10), sticky="e")
    
    def update(self):
        self.lbl_src['text'] = f": {self.master.cur_src_folder}"
        self.lbl_dst['text'] = f": {self.master.cur_dst_folder}"

class ImgDisplay(tk.Canvas):
    def __init__(self, master=None, *args, **kwargs):
        tk.Canvas.__init__(self, master, *args, **kwargs)
        self.reset()

    def set_content(self, content):
        self.delete("all")
        self.img = content
        self.configure(width=self.img.width(), height=self.img.height())
        self.content = self.create_image(0, 0, image=self.img, anchor='nw')

    def reset(self):
        self.set_content(load_tk_image("letsgo.jpg"))

class ImgPicker(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("pyimgpick")
        ## Placing the window on the top left makes for a better experience
        self.geometry("+0+0")

        self.loader = None
        ## Init and place folder selectors frame
        self.topframe = TopFrame(master=self)
        self.topframe.pack(
            side=tk.TOP,
            pady=5,
            expand=True,
            fill="both",
        )
        self.cur_dst_folder = None
        self.cur_src_folder = None
        ## Init image frame with canvas and counter
        self.img_frame = tk.Frame(master=self)
        self.display = ImgDisplay(master=self.img_frame)
        self.display.grid(
            row=0, column=0,
            padx=5, pady=(5, 0),
        )
        self.imgcounter = tk.Label(master=self.img_frame)
        self.imgcounter.grid(
            row=1, column=0,
            padx=5, pady=(0, 5),
        )
        self.img_frame.pack(
            padx=5, pady=5,
        )
        ## Init and place button frame
        self.pickers = PickerFrame(master=self)
        self.pickers.pack(
            side=tk.BOTTOM, 
            pady=5,
        )

        self.bind("<Left>", lambda event: self.pickers.left.emit())
        self.bind("<Right>", lambda event: self.pickers.right.emit())
        self.bind("<Up>", lambda event: self.pickers.up.emit())
        self.bind("<Down>", lambda event: self.pickers.down.emit())
        self.bind("<BackSpace>", lambda event: self.back())

        self.protocol("WM_DELETE_WINDOW", self.exit) ## debug
        self.clean_records()
        self.reset()

    def exit(self, dump=True):
        if dump:
            print("Dumping records...")
            for mode, images in self.imgrecord.items():
                print(mode + ":", len(images))
                for img in images:
                    print('\t'+img)
        self.destroy()

    def clean_records(self):
        self.history = []
        self.imgrecord = {
            self.pickers.left.assignment: [],
            self.pickers.right.assignment: [],
            self.pickers.up.assignment: [],
            self.pickers.down.assignment: [],
        }

    def cmd_set_folder(self, target):
        if self.loader and target == "source":
            if not messagebox.askokcancel(message="Choosing another source folder will forfeit all current choices, proceed ?"):
                return
        folder = askdirectory(mustexist=False)
        if not folder:
            messagebox.showwarning(title="Warning !", message=f"No {target} folder selected !")
            return
        ## Did we change the source directory ?
        if target == "source":
            self.cur_src_folder = folder
            self.reset(folder)
        elif target == "destination":
            self.cur_dst_folder = folder
        self.update_labels()

    def cmd_commit(self):
        if not self.cur_dst_folder:
            messagebox.showerror(message="Please choose a destination folder.")
            return
        ## Create the different batch mode dirs in/and the destination directory if needed
        for mode in self.imgrecord:
            mode_dir = os.path.join(self.cur_dst_folder, mode)
            os.makedirs(mode_dir, exist_ok=True)
            ## Then move the images in the proper batch mode dirs
            for file in self.imgrecord[mode]:
                filepath = os.path.join(mode_dir, file.split("/")[-1])
                os.replace(file, filepath)
        messagebox.showinfo(message=f"Images successfully sorted to {self.cur_dst_folder}.")
        self.reset()

    def reset(self, src_dir=None):
        if not self.cur_src_folder:
            self.display.reset()
            self.update_labels()
            return
        self.clean_records()
        if not src_dir:
            src_dir = self.cur_src_folder
        self.loader = ImgFolder(src_dir)
        if not self.loader.paths:
            messagebox.showerror(message="Source folder is empty or does not contain suitable images !")
            self.loader = None
            return
        self.getimage()
        self.update_labels()

    def getimage(self, dir="next"):
        if not self.loader:
            if dir == "prev":
                return
            raise ValueError("Cannot get the next image without an image loader !")
        ## Get next image
        try:
            if dir == "next":
                img = self.loader.next()
            if dir == "prev":
                img = self.loader.prev()
        except StopIteration:
            if self.loader.completed():
                img = load_image("done.jpg")
            else:
                return
        if img:
            self.cur_img = load_tk_image(img)
            self.display.set_content(self.cur_img)
            self.update_labels(self.loader.completed())

    def update_labels(self, jobdone=False):
        self.topframe.update()
        if self.loader:
            self.imgcounter['text'] = f"Image ({self.loader.head + 1} of {len(self.loader.paths)})" \
                if not jobdone else "Done ! Press commit to save your picks."
        else:
            self.imgcounter['text'] = "No images loaded."

    def process(self, assignment):
        if not self.loader:
            messagebox.showerror(message="Please select a source folder first !")
            return
        if self.loader.completed():
            messagebox.showinfo(message="No more images to pick, please commit your sorting !")
            return
        self.imgrecord[assignment].append(self.loader.curpath())
        self.history.append(assignment)
        self.getimage()

    def back(self):
        if not self.loader:
            return
        self.getimage("prev")
        if self.history:
            self.imgrecord[self.history.pop()].pop()
