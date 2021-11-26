# pyimgpick

## Manual image sorter

pyimgpick is a TKinter app for manually sorting images, intended for the creation of machine learning datasets from raw image dumps.

![pyimgpick](https://user-images.githubusercontent.com/9503374/143513847-aaf58c3f-18e3-4738-a516-17f2d0eb6513.png)

### Requirements

* python 3
* `pillow` (with `python3-pil.imagetk`)

### Usage

Use the top-left buttons to choose a source and a destination directory. The app will then allow you to go through all images
present in that directory and its subdirectories.

For each image, you can assign them to a different action : Keep, Discard, Need Processing or Incomplete.
You may use the directional arrows to speed things up.

If you messed up, just press the Backspace key to cancel your picks until you're satisfied.

At any time during the process, you can press the "Commit" button to have the app sort the images in corresponding folders
inside the destination directory.

Press "Reset" to restart the source directory scan as well as the sorting process.

### TODO
* Allow the user to specify the labels and corresponding folder names of the actions (hopefully with a nice dialog window)
