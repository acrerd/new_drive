# from tkinter import *
#
# ralabel = Label(text="Right ascension")
# raentry = Label(text="###d ##m ##.#s")
# declabel = Label(text="Declination")
# decentry = Label(text="###d ##m ##.#s")
# azlabel = Label(text="Azimuth")
# azentry = Label(text="###d ##m ##.#s")
# ellabel = Label(text="Elevation")
# elentry = Label(text="###d ##m ##.#s")
# timelabel = Label(text="Time (UTC)")
# timeentry = Label(text="##:##:##")
#
# coorddrivebutton = Button(text="Drive to coordinates")
# objdrivebutton = Button(text="Drive to object")
# homedrivebutton = Button(text="Home")
# stowdrivebutton = Button(text="Stow")
#
# ralabel.grid(row=0, column=0, sticky=W, padx=5, pady=2)
# raentry.grid(row=0, column=1, padx=5, pady=2)
# declabel.grid(row=0, column=2, sticky=W, padx=5, pady=2)
# decentry.grid(row=0, column=3, padx=5, pady=2)
# azlabel.grid(row=1, column=0, sticky=W, padx=5, pady=2)
# azentry.grid(row=1, column=1, padx=5, pady=2)
# ellabel.grid(row=1, column=2, sticky=W, padx=5, pady=2)
# elentry.grid(row=1, column=3, padx=5, pady=2)
# timelabel.grid(row=0, column=4, sticky=W, padx=5, pady=5)
# timeentry.grid(row=1, column=4, padx=5, pady=5)
#
# coorddrivebutton.grid(row=3, column=1, padx=5, pady=20)
# objdrivebutton.grid(row=3, column=3, padx=5, pady=20)
# homedrivebutton.grid(row=4, column=1, padx=5, pady=5)
# stowdrivebutton.grid(row=4, column=3, padx=5, pady=5)
#
# mainloop()

# Things to have:

# Text that reads "Azimuth"
# Text that reads "Elevation"
# Text that reads "Right ascension"
# Text that reads "Declination"
# Text that reads "Time (UTC)"

# Text that gives current telescope azimuth - when window opens, calculate telescope position
# Text that gives current telescope altitude - when window opens, calculate telescope position
# Text that gives current telescope right ascension - when window opens, calculate telescope position
# Text that gives current telescope declination - when window opens, calculate telescope position
# Text that gives current time (and updates each second)

# Button that says "Drive to coordinates" - launches second window
# Button that says "Drive to object" - launches second window
# Button that says "Home" - drives to fixed position
# Button that says "Stow" - drives to fixed position

from tkinter import *
import time

# Clock adapted from clock by vegaseat on Daniweb
def tick(timenow=''):
    timenow = time.strftime('%H:%M:%S', time.gmtime())
    clock.config(text=timenow)
    clock.after(500, tick)

root = Tk()

timelabel = Label(text="Time (UTC)")
clock = Label(root)
tick()

# For later - use this to set the telescope to home position
def gohome():
    print("The telescope is going home.")
    # This drives the telescope to the home position
    # Home position coordinates can be set below
    homealt = 0
    homeel = 0
    # Pass these coordinates to the driver and get it to drive there
    # After this, make sure it's ready to do something else

# For later - use this to set the telescope to stow position
def gostow():
    print("The telescope is stowing.")
    # This drives the telescope to the home position
    # Home position coordinates can be set below
    stowaz = 0
    stowel = 0
    # Pass these coordinates to the driver and get it to drive there
    # After this, make sure it's ready to do something else

ralabel = Label(text="Right ascension")
raentry = Label(text="")
declabel = Label(text="Declination")
decentry = Label(text="")
azlabel = Label(text="Azimuth")
azentry = Label(text="")
ellabel = Label(text="Elevation")
elentry = Label(text="")

coorddrivebutton = Button(text="Drive to coordinates")
objdrivebutton = Button(text="Drive to object")
homedrivebutton = Button(text="Home", command=gohome)
stowdrivebutton = Button(text="Stow", command=gostow)

ralabel.grid(row=0, column=0, sticky=W, padx=5, pady=2)
raentry.grid(row=0, column=1, padx=5, pady=2)
declabel.grid(row=0, column=2, sticky=W, padx=5, pady=2)
decentry.grid(row=0, column=3, padx=5, pady=2)
azlabel.grid(row=1, column=0, sticky=W, padx=5, pady=2)
azentry.grid(row=1, column=1, padx=5, pady=2)
ellabel.grid(row=1, column=2, sticky=W, padx=5, pady=2)
elentry.grid(row=1, column=3, padx=5, pady=2)

coorddrivebutton.grid(row=3, column=1, padx=5, pady=20)
objdrivebutton.grid(row=3, column=3, padx=5, pady=20)
homedrivebutton.grid(row=4, column=1, padx=5, pady=5)
stowdrivebutton.grid(row=4, column=3, padx=5, pady=5)

timelabel.grid(row=0, column=4, sticky=W, padx=5, pady=5)
clock.grid(row=1, column=4, padx=5, pady=5)

mainloop()

# Idea for coords
# Write an app called whereami
# whereami should ask driver for current az/el
# Add whatever offset exists because of its location
# Convert into RA/dec
# Then print each value into the box
# Then be ready to take more instructions
# Run this every time the main GUI is open

# Idea for home
# Write an app called gohome
# Tell driver to move to the home position
# Then be ready to take more instructions
# Run this when the home button is clicked

# Idea for stow
# Write an app called gostow
# Tell driver to move to the stow position
# Then be ready to take more instructions
# Run this when the stow button is clicked