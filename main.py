import os
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from PIL import ImageTk, Image

class imgloader():
    def __init__(self, path, ext):
        self.image_paths = []
        for (root, _, files) in os.walk(path):
            self.image_paths += [os.path.join(root, file) for file in files if file.split('.')[1] in ext]

        self.image = (ImageTk.PhotoImage(Image.open(img)) for img in self.image_paths)
        self.cur_id = 0

    def next(self):
        self.cur_id += 1
        try:
            img = next(self.image)
            return img
        except StopIteration:
            if self.cur_id == 1:
                return None
            else:
                return ImageTk.PhotoImage(Image.open(os.path.join(os.getcwd(), 'done.jpg')))

    def completed(self):
        return self.cur_id == len(self.image_paths) + 1

    def cur_img_path(self):
        return self.image_paths[self.cur_id - 1]

class imgpicker():
    def __init__(self):
        self.loader = None
        self.clean_records()
        ## Init root window
        self.win_root = tk.Tk()
        self.win_root.title("pyimgpick")
        ## Placing the window on the top left makes for a better experience
        self.win_root.geometry("+0+0")
        ## Init and place folder selectors frame
        self.init_folder_frame()
        self.frm_folders.pack(
            side=tk.TOP,
            pady=5,
        )
        ## Init image canvas with a dummy
        self.cnv_image = tk.Canvas(
            master=self.win_root,
        )
        ## Place the canvas in the window
        self.cnv_image.pack(
            padx=5, pady=5,
        )
        ## Init and place button frame
        self.init_button_frame()
        self.update_labels()
        self.frm_buttons.pack(
            side=tk.BOTTOM, 
            pady=5,
        )

        def dumprecords():
            for mode, images in self.imgrecord.items():
                print(mode + ":", len(images))
                for img in images:
                    print('\t'+img)
            self.win_root.destroy()

        self.win_root.bind("<Left>", lambda event: self.cmd_count_image("keep"))
        self.win_root.bind("<Right>", lambda event: self.cmd_count_image("discard"))
        self.win_root.bind("<Up>", lambda event: self.cmd_count_image("needprocessing"))
        self.win_root.bind("<Down>", lambda event: self.cmd_count_image("incomplete"))

        self.win_root.protocol("WM_DELETE_WINDOW", dumprecords) ## debug
        self.reset()
        self.win_root.mainloop()

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
            os.makedirs(mode_dir)
            ## Then move the images in the proper batch mode dirs
            for file in self.imgrecord[mode]:
                filepath = os.path.join(mode_dir, file.split("/")[-1])
                os.replace(file, filepath)
        messagebox.showinfo(message=f"Images successfully sorted to {self.cur_dst_folder}.")
        self.reset()

    def clean_records(self):
        self.imgrecord = {
            "keep": [],
            "discard": [],
            "incomplete": [],
            "needprocessing": [],
        }
    
    def reset_canvas(self, img=None):
        if img:
            self.cur_img = img
        self.img_on_cnv_image = self.cnv_image.create_image(0, 0, image=self.cur_img, anchor='nw')
        self.cnv_image.configure(height=self.cur_img.height(), width=self.cur_img.width())

    def reset(self, src_dir=None):
        if not src_dir:
            start_img = ImageTk.PhotoImage(Image.open(os.path.join(os.getcwd(), 'letsgo.jpg')))
            self.reset_canvas(start_img)
            return
        self.loader = None
        self.clean_records()
        self.cur_src_folder = src_dir
        ## Recreate an image loader, retrieve the first image and setup the canvas
        self.loader = imgloader(src_dir, ['png', 'bmp', 'jpg', 'jpeg'])
        self.cur_img = self.loader.next()

        if not self.cur_img:
            messagebox.showerror(message="Directory does not exist or does not contain any images !")
            self.loader = None
            return

        self.reset_canvas()
        self.update_labels()

    def nextimage(self):
        self.cur_img = self.loader.next()
        self.cnv_image.itemconfig(self.img_on_cnv_image, image=self.cur_img)
        self.cnv_image.configure(height=self.cur_img.height(), width=self.cur_img.width())
        self.update_labels(self.loader.completed())

    def init_folder_frame(self):
        if not self.win_root:
            raise ValueError("Root window not initialized.")
        self.frm_folders = tk.Frame(master=self.win_root)
        ## Init buttons
        self.btn_src_folder = tk.Button(
            master=self.frm_folders,
            text="Choose source folder...",
            command=lambda: self.cmd_set_folder("source"),
        )
        self.btn_dst_folder = tk.Button(
            master=self.frm_folders,
            text="Choose destination folder...",
            command=lambda: self.cmd_set_folder("destination"),
        )
        self.btn_save = tk.Button(
            master=self.frm_folders,
            text="Commit",
            command=self.cmd_commit,
        )
        self.btn_reset = tk.Button(
            master=self.frm_folders,
            text="Reset",
            command=lambda: self.reset(self.cur_src_folder),
        )
        ## Init labels and folder names
        self.cur_src_folder = None
        self.cur_dst_folder = None
        self.lbl_src_folder = tk.Label(
            master=self.frm_folders,
        )
        self.lbl_dst_folder = tk.Label(
            master=self.frm_folders,
        )
        ## Place buttons and labels in frame
        self.btn_src_folder.grid(
            row=0, column=0,
            padx=5, pady=(0, 5),
            sticky='we',
        )
        self.lbl_src_folder.grid(
            row=0, column=1,
            padx=5, pady=(0, 5),
        )
        self.btn_dst_folder.grid(
            row=1, column=0,
            padx=5, pady=(5, 0),
            sticky='we',
        )
        self.lbl_dst_folder.grid(
            row=1, column=1,
            padx=5, pady=(5, 0),
        )
        self.btn_save.grid(
            row=0, column=2,
            padx=(20, 5), pady=5,
            sticky='we',
        )
        self.btn_reset.grid(
            row=1, column=2,
            padx=(20, 5), pady=(0, 5),
            sticky='we',
        )

    def update_labels(self, jobdone=False):
        self.lbl_src_folder['text'] = f"Current : {self.cur_src_folder}"
        self.lbl_dst_folder['text'] = f"Current : {self.cur_dst_folder}"
        if self.loader:
            self.lbl_imgcounter['text'] = f"Image ({self.loader.cur_id} of {len(self.loader.image_paths)})" \
                if not jobdone else "Done ! Press commit to save your picks."
        else:
            self.lbl_imgcounter['text'] = "No images loaded."

    def cmd_count_image(self, command):
        if not self.loader:
            messagebox.showerror(message="Please select a source folder first !")
            return
        if self.loader.completed():
            messagebox.showinfo(message="No more images to pick, please commit your sorting !")
            return
        self.imgrecord[command].append(self.loader.cur_img_path())
        self.nextimage()

    def init_button_frame(self):
        self.frm_buttons = tk.Frame(master=self.win_root)
        ## Init buttons and image counter
        self.lbl_imgcounter = tk.Label(
            master=self.frm_buttons,
        )
        self.btn_keep = tk.Button(
            master=self.frm_buttons,
            text="KEEP",
            bg='green',
            command=lambda: self.cmd_count_image("keep"),
        )
        self.btn_discard = tk.Button(
            master=self.frm_buttons,
            text="DISCARD",
            bg='red',
            command=lambda: self.cmd_count_image("discard"),
        )
        self.btn_needprocessing = tk.Button(
            master=self.frm_buttons,
            text="NEED PROCESSING",
            bg='yellow', fg='black',
            command=lambda: self.cmd_count_image("needprocessing"),
        )
        self.btn_incomplete = tk.Button(
            master=self.frm_buttons,
            text="INCOMPLETE",
            bg='blue',
            command=lambda: self.cmd_count_image("incomplete"),
        )
        ## Place buttons in the frame
        self.lbl_imgcounter.grid(
            row=0, column=0, columnspan=2,
            pady=(0, 5),
        )
        self.btn_needprocessing.grid(
            row=1, column=0, columnspan=2,
        )
        self.btn_keep.grid(
            row=2, column=0,
            padx=20, pady=5,
        )
        self.btn_discard.grid(
            row=2, column=1,
            padx=20, pady=5,
        )
        self.btn_incomplete.grid(
            row=3, column=0, columnspan=2,
        )

if __name__ == "__main__":
    app = imgpicker()
