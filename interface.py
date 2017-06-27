import tkinter as tk
import tkinter.ttk as ttk
import time
import math
import ephem
import datetime

# Establish the telescope's location for ephem
# This is an approximate location, to be altered when the telescope has a permanent location
mylocation = ephem.Observer()
mylocation.long, mylocation.lat = '-4.35', '55.92'  # placeholder


# Converter between angles in fractional degrees and dms; produces output string for the interface coordinates
def todms(inputangle):

    # These should correct for angles > 360 or < 0 being returned, bringing them back within range
    while inputangle > 360:
        inputangle -= 360

    while inputangle < 0:
        inputangle += 360

    # Separate out degrees, minutes and seconds, initially as ints or floats
    degree = math.floor(inputangle)
    firstremainder = inputangle-degree
    minute = math.floor(firstremainder*60)
    secondremainder = (firstremainder*60)-minute
    second = round(secondremainder*60, 1)

    # Ideally this would produce an output string in one line
    # However, there's a problem where attempting to do so just repeatedly prints the degree value in different formats
    # If possible, fix this later
    # Meanwhile, this will provide the correct format for the full string
    degformat = "{0:0=3d}°".format(degree)
    minformat = "{0:0=2d}m".format(minute)
    secformat = "{0:04.1f}s".format(second)
    coord = "{} {} {}".format(degformat, minformat, secformat)
    return coord


# Clock in UTC; updates every 500ms
# Note: this isn't the clock used in ephem calculations, so it's not intended to be especially precise
def tick(timenow=""):
    timenow = time.strftime("%H:%M:%S", time.gmtime())
    clock.config(text=timenow)
    clock.after(500, tick)


def getlocation(aznow="", elnow=""):
    # Get current az-el from driver
    # Convert to ra-dec
    # Produce four labels for az-el and ra-dec coordinates
    # Update this periodically - 200ms
    aznow = 0  # placeholder
    elnow = 0  # placeholder
    mylocation.date = datetime.datetime.now()
    [rarad, decrad] = mylocation.radec_of(math.radians(aznow), math.radians(elnow))
    # Problem - clock stops for mylocation when the program's running; won't update
    ranow = math.degrees(rarad)
    decnow = math.degrees(decrad)
    azcoord = todms(aznow)
    elcoord = todms(elnow)
    racoord = todms(ranow)
    deccoord = todms(decnow)
    azval.config(text=azcoord)
    elval.config(text=elcoord)
    raval.config(text=racoord)
    decval.config(text=deccoord)
    decval.after(50, getlocation)


def gohome():
    print("gohome is unfinished")
    # This should drive to fixed coordinates
    homeaz = 0  # placeholder
    homeel = 0  # placeholder


def gostow():
    print("gotstow is unfinished")
    # This should drive to fixed coordinates
    stowaz = 0  # placeholder
    stowel = 0  # placeholder


def quit():
    maininterface.quit()


def coorddrive():
    # This sets up the driver to drive to the requested coordinates
    print("coorddrive is unfinished")

    # First, check which coordinate system was selected
    if coordsyschoice.get() == "":
        print("Error: missing input. Please select a coordinate system.")
        # The above should display a popup with that error message and break out of this function
        # Can't run at all without a coordinate system
        # Want to keep the interface's input so it can be easily fixed
    else:
        # This value will be used later when coordinate conversions need done
        choice = coordsyschoice.get()

    # Next, get horizontal coordinates
    # To do: all error messages as popups
    if len(horizdeg.get()) > 0:
        try:
            horizdegval = int(horizdeg.get())
            horizdecimaldeg = horizdegval
            try:
                horizminval = int(horizmin.get())
                horizdecimalmin = horizminval/60
                if len(horizsec.get()) > 0:
                    try:
                        horizsecval = int(horizsec.get())
                        horizdecimalsec = horizsecval/3600
                        horizdecimaltotal = horizdecimaldeg + horizdecimalmin + horizdecimalsec
                    except ValueError:
                        try:
                            horizsecval = float(horizsec.get())
                            horizdecimalsec = horizsecval/3600
                            horizdecimaltotal = horizdecimaldeg + horizdecimalmin + horizdecimalsec
                        except ValueError:
                            print("Error: invalid input. Please input coordinates as numbers only.")
                else:
                    horizdecimaltotal = horizdecimaldeg + horizdecimalmin
            except ValueError:
                try:
                    horizminval = float(horizmin.get())
                    horizdecimalmin = horizminval/60
                    horizdecimaltotal = horizdecimaldeg + horizdecimalmin
                    if len(horizsec.get()) > 0:
                        print("Error: invalid input. Please see the wiki for correct formatting.")
                    else:
                        pass
                except ValueError:
                    print("Error: invalid input. Please input coordinates as numbers only.")
        except ValueError:
            try:
                horizdegval = float(horizdeg.get())
                horizdecimaldeg = horizdegval
                horizdecimaltotal = horizdecimaldeg
                if len(horizmin.get()) > 0:
                    print("Error: invalid input. Please see the wiki for correct formatting.")
                else:
                    pass
                if len(horizsec.get()) > 0:
                    print("Error: invalid input. Please see the wiki for correct formatting.")
                else:
                    pass
            except ValueError:
                print("Error: invalid input. Please input coordinates as numbers only.")
    elif len(horizmin.get()) > 0:
        try:
            horizminval = int(horizmin.get())
            horizdecimalmin = horizminval/60
            if len(horizsec.get()) > 0:
                try:
                    horizsecval = int(horizsec.get())
                    horizdecimalsec = horizsecval/3600
                    horizdecimaltotal = horizdecimalmin + horizdecimalsec
                except ValueError:
                    try:
                        horizsecval = float(horizsec.get())
                        horizdecimalsec = horizsecval/3600
                        horizdecimaltotal = horizdecimalmin + horizdecimalsec
                    except ValueError:
                        print("Error: invalid input. Please input coordinates as numbers only.")
            else:
                horizdecimaltotal = horizdecimalmin
        except ValueError:
            try:
                horizminval = float(horizmin.get())
                horizdecimalmin = horizminval/60
                horizdecimaltotal = horizdecimalmin
                if len(horizsec.get()) > 0:
                    print("Error: invalid input. Please see the wiki for correct formatting.")
                else:
                    pass
            except ValueError:
                print("Error: invalid input. Please input coordinates as numbers only.")
    elif len(horizsec.get()) > 0:
        try:
            horizsecval = int(horizsec.get())
            horizdecimalsec = horizsecval/3600
            horizdecimaltotal = horizdecimalsec
        except ValueError:
            try:
                horizsecval = float(horizsec.get())
                horizdecimalsec = horizsecval/3600
                horizdecimaltotal = horizdecimalsec
            except ValueError:
                print("Error: invalid input. Please input coordinates as numbers only.")
    else:
        print("Error: missing input. Please input a horizontal coordinate.")

    # Next, get vertical coordinates
    # To do: all error messages as popups
    if len(vertdeg.get()) > 0:
        try:
            vertdegval = int(vertdeg.get())
            vertdecimaldeg = vertdegval
            try:
                vertminval = int(vertmin.get())
                vertdecimalmin = vertminval / 60
                if len(vertsec.get()) > 0:
                    try:
                        vertsecval = int(vertsec.get())
                        vertdecimalsec = vertsecval / 3600
                        vertdecimaltotal = vertdecimaldeg + vertdecimalmin + vertdecimalsec
                    except ValueError:
                        try:
                            vertsecval = float(vertsec.get())
                            vertdecimalsec = vertsecval / 3600
                            vertdecimaltotal = vertdecimaldeg + vertdecimalmin + vertdecimalsec
                        except ValueError:
                            print("Error: invalid input. Please input coordinates as numbers only.")
                else:
                    vertdecimaltotal = vertdecimaldeg + vertdecimalmin
            except ValueError:
                try:
                    vertminval = float(vertmin.get())
                    vertdecimalmin = vertminval / 60
                    vertdecimaltotal = vertdecimaldeg + vertdecimalmin
                    if len(vertsec.get()) > 0:
                        print("Error: invalid input. Please see the wiki for correct formatting.")
                    else:
                        pass
                except ValueError:
                    print("Error: invalid input. Please input coordinates as numbers only.")
        except ValueError:
            try:
                vertdegval = float(vertdeg.get())
                vertdecimaldeg = vertdegval
                vertdecimaltotal = vertdecimaldeg
                if len(vertmin.get()) > 0:
                    print("Error: invalid input. Please see the wiki for correct formatting.")
                else:
                    pass
                if len(vertsec.get()) > 0:
                    print("Error: invalid input. Please see the wiki for correct formatting.")
                else:
                    pass
            except ValueError:
                print("Error: invalid input. Please input coordinates as numbers only.")
    elif len(vertmin.get()) > 0:
        try:
            vertminval = int(vertmin.get())
            vertdecimalmin = vertminval / 60
            if len(vertsec.get()) > 0:
                try:
                    vertsecval = int(vertsec.get())
                    vertdecimalsec = vertsecval / 3600
                    vertdecimaltotal = vertdecimalmin + vertdecimalsec
                except ValueError:
                    try:
                        vertsecval = float(vertsec.get())
                        vertdecimalsec = vertsecval / 3600
                        vertdecimaltotal = vertdecimalmin + vertdecimalsec
                    except ValueError:
                        print("Error: invalid input. Please input coordinates as numbers only.")
            else:
                vertdecimaltotal = vertdecimalmin
        except ValueError:
            try:
                vertminval = float(vertmin.get())
                vertdecimalmin = vertminval / 60
                vertdecimaltotal = vertdecimalmin
                if len(vertsec.get()) > 0:
                    print("Error: invalid input. Please see the wiki for correct formatting.")
                else:
                    pass
            except ValueError:
                print("Error: invalid input. Please input coordinates as numbers only.")
    elif len(vertsec.get()) > 0:
        try:
            vertsecval = int(vertsec.get())
            vertdecimalsec = vertsecval / 3600
            vertdecimaltotal = vertdecimalsec
        except ValueError:
            try:
                vertsecval = float(vertsec.get())
                vertdecimalsec = vertsecval / 3600
                vertdecimaltotal = vertdecimalsec
            except ValueError:
                print("Error: invalid input. Please input coordinates as numbers only.")
    else:
        print("Error: missing input. Please input a vertical coordinate.")

    # Convert the coordinates into az-el if they're not already
    # No error-handling included here, as the coordinate choice was already validated earlier
    if choice == "Ecliptic":
        print("Convert ecliptic to horizontal")
        skylocation = ephem.Equatorial(ephem.Ecliptic(horizdecimaltotal, vertdecimaltotal))
        referencestar = ephem.FixedBody()
        referencestar._ra = skylocation.ra
        referencestar._dec = skylocation.dec
        referencestar._epoch = skylocation.epoch
        referencestar.compute(mylocation)
        gotoaz = referencestar.az
        gotoel = referencestar.alt
    elif choice == "Equatorial":
        print("Convert equatorial to horizontal")
        skylocation = ephem.Equatorial(horizdecimaltotal, vertdecimaltotal)
        referencestar = ephem.FixedBody()
        referencestar._ra = skylocation.ra
        referencestar._dec = skylocation.dec
        referencestar._epoch = skylocation.epoch
        referencestar.compute(mylocation)
        gotoaz = referencestar.az
        gotoel = referencestar.alt
    elif choice == "Galactic":
        print("Convert galactic to horizontal")
        skylocation = ephem.Equatorial(ephem.Galactic(horizdecimaltotal, vertdecimaltotal))
        referencestar = ephem.FixedBody()
        referencestar._ra = skylocation.ra
        referencestar._dec = skylocation.dec
        referencestar._epoch = skylocation.epoch
        referencestar.compute(mylocation)
        gotoaz = referencestar.az
        gotoel = referencestar.alt
    else:
        print("Already horizontal!")
        gotoaz=horizdecimaltotal
        gotoel=vertdecimaltotal


def raise_frame(frame):
    frame.tkraise()


# Setting up main interface window
# Note: styles won't work unless placed after the maininterface declaration
maininterface = tk.Tk()
maininterface.title("Telescope Interface")
maininterface.resizable(0, 0)  # Disabled window resizing - if annoying later, removed

# Setting up styles
style = ttk.Style()

style.configure("Upper.TFrame", background="gray20")
style.configure("Lower.TFrame", background="white")
style.configure("Upper.TLabel", foreground="white", background="gray20", width=15, anchor=tk.CENTER)
style.configure("Lower.TLabel", foreground="black", background="white", width=15, anchor=tk.CENTER)
style.configure("WiderUpper.TLabel", foreground="white", background="gray20", width=18, anchor=tk.CENTER)
style.configure("WiderLower.TLabel", foreground="black", background="white", width=18, anchor=tk.CENTER)
style.configure("MiniUpper.TLabel", foreground="white", background="gray20", width=2, anchor=tk.W)
style.configure("MiniLower.TLabel", foreground="black", background="white", width=2, anchor=tk.W)
style.configure("Lower.TCheckbutton", background="white")

# Frame declarations
upperframe = ttk.Frame(maininterface, width=500, height=50, style="Upper.TFrame")
upperframe.grid(row=0, rowspan=2, columnspan=5)
mainframe = ttk.Frame(maininterface, width=500, height=250, style="Lower.TFrame")
mainframe.grid(row=2, columnspan=5)
coordframe = ttk.Frame(maininterface, width=500, height=250, style="Lower.TFrame")
coordframe.grid(row=2, columnspan=3)
objframe = ttk.Frame(maininterface, width=500, height=250, style="Lower.TFrame")
objframe.grid(row=2)

# Setting up frame sizes to allow for correct spacing
upperframe.columnconfigure(0, minsize=100)
upperframe.columnconfigure(1, minsize=100)
upperframe.columnconfigure(2, minsize=100)
upperframe.columnconfigure(3, minsize=100)
upperframe.columnconfigure(4, minsize=100)

mainframe.columnconfigure(0, minsize=100)
mainframe.columnconfigure(1, minsize=100)
mainframe.columnconfigure(2, minsize=100)
mainframe.columnconfigure(3, minsize=100)
mainframe.columnconfigure(4, minsize=100)

mainframe.rowconfigure(0, minsize=50)
mainframe.rowconfigure(1, minsize=50)
mainframe.rowconfigure(2, minsize=50)
mainframe.rowconfigure(3, minsize=25)
mainframe.rowconfigure(4, minsize=25)

coordframe.columnconfigure(0, minsize=150)
coordframe.columnconfigure(1, minsize=20)
coordframe.columnconfigure(2, minsize=150)
coordframe.columnconfigure(3, minsize=20)
coordframe.columnconfigure(4, minsize=150)

coordframe.rowconfigure(0, minsize=40)
coordframe.rowconfigure(1, minsize=40)
coordframe.rowconfigure(2, minsize=20)
coordframe.rowconfigure(3, minsize=40)
coordframe.rowconfigure(4, minsize=40)
coordframe.rowconfigure(5, minsize=40)

objframe.columnconfigure(0, minsize=160)
objframe.columnconfigure(1, minsize=160)
objframe.columnconfigure(2, minsize=160)

objframe.rowconfigure(0, minsize=50)
objframe.rowconfigure(1, minsize=50)
objframe.rowconfigure(2, minsize=20)
objframe.rowconfigure(3, minsize=50)
objframe.rowconfigure(4, minsize=50)

# Labels for upper section; coordinates and time
ralabel = ttk.Label(upperframe, text="RA:", style="Upper.TLabel")
declabel = ttk.Label(upperframe, text="Dec:", style="Upper.TLabel")
raval = ttk.Label(upperframe, style="Upper.TLabel")
decval = ttk.Label(upperframe, style="Upper.TLabel")
ralabel.grid(row=0, column=0)
declabel.grid(row=1, column=0)
raval.grid(row=0, column=1)
decval.grid(row=1, column=1)

azlabel = ttk.Label(upperframe, text="Az:", style="Upper.TLabel")
ellabel = ttk.Label(upperframe, text="El:", style="Upper.TLabel")
azval = ttk.Label(upperframe, style="Upper.TLabel")
elval = ttk.Label(upperframe, style="Upper.TLabel")
azlabel.grid(row=0, column=2)
ellabel.grid(row=1, column=2)
azval.grid(row=0, column=3)
elval.grid(row=1, column=3)

timelabel = ttk.Label(upperframe, text="Time (UTC):", style="Upper.TLabel")
timelabel.grid(row=0, column=4)
clock = ttk.Label(upperframe, style="Upper.TLabel")
clock.grid(row=1, column=4)

# Buttons for mainframe
coordbutton = tk.Button(mainframe, text="Drive to coordinates", width=12, height=5, wraplength=70,
                        background="light sky blue", activebackground="deep sky blue",
                        command=lambda: raise_frame(coordframe))
objbutton = tk.Button(mainframe, text="Drive to object", width=12, height=5, wraplength=70,
                      background="light sky blue", activebackground="deep sky blue",
                      command=lambda: raise_frame(objframe))
homebutton = tk.Button(mainframe, text="Home", width=12,
                       background="light sky blue", activebackground="deep sky blue", command=gohome)
stowbutton = tk.Button(mainframe, text="Stow", width=12,
                       background="light sky blue", activebackground="deep sky blue", command=gostow)
coordbutton.grid(row=1, column=1)
objbutton.grid(row=1, column=3)
homebutton.grid(row=3, column=1)
stowbutton.grid(row=3, column=3)

# Widgets for coordframe
coordsyslabel = ttk.Label(coordframe, text="Coordinate system:", style="WiderLower.TLabel")
coordsyslabel.grid(row=0, column=0)
coordsyschoice = tk.StringVar()
coordsysmenu = ttk.Combobox(coordframe, values=["Ecliptic", "Equatorial", "Galactic", "Horizontal"],
                            textvariable=coordsyschoice, state="readonly", width=15)
coordsysmenu.grid(row=0, column=2)

horizlabel = ttk.Label(coordframe, text="Horizontal", style="Lower.TLabel")
horizlabel.grid(row=2, column=0)
horizdeg = tk.StringVar()
horizdegentry = ttk.Entry(coordframe, textvariable=horizdeg, width=15)
horizdegentry.grid(row=3, column=0)
horizdegsymbol = ttk.Label(coordframe, text="d", style="MiniLower.TLabel")
horizdegsymbol.grid(row=3, column=1, sticky="W")
horizmin = tk.StringVar()
horizminentry = ttk.Entry(coordframe, textvariable=horizmin, width=15)
horizminentry.grid(row=4, column=0)
horizminsymbol = ttk.Label(coordframe, text="m", style="MiniLower.TLabel")
horizminsymbol.grid(row=4, column=1, sticky="W")
horizsec = tk.StringVar()
horizsecentry = ttk.Entry(coordframe, textvariable=horizsec, width=15)
horizsecentry.grid(row=5, column=0)
horizsecsymbol = ttk.Label(coordframe, text="s", style="MiniLower.TLabel")
horizsecsymbol.grid(row=5, column=1, sticky="W")

vertlabel = ttk.Label(coordframe, text="Vertical", style="Lower.TLabel")
vertlabel.grid(row=2, column=2)
vertdeg = tk.StringVar()
vertdegentry = ttk.Entry(coordframe, textvariable=vertdeg, width=15)
vertdegentry.grid(row=3, column=2)
vertdegsymbol = ttk.Label(coordframe, text="d", style="MiniLower.TLabel")
vertdegsymbol.grid(row=3, column=3, sticky="W")
vertmin = tk.StringVar()
vertminentry = ttk.Entry(coordframe, textvariable=vertmin, width=15)
vertminentry.grid(row=4, column=2)
vertminsymbol = ttk.Label(coordframe, text="m", style="MiniLower.TLabel")
vertminsymbol.grid(row=4, column=3, sticky="W")
vertsec = tk.StringVar()
vertsecentry = ttk.Entry(coordframe, textvariable=vertsec, width=15)
vertsecentry.grid(row=5, column=2)
vertsecsymbol = ttk.Label(coordframe, text="s", style="MiniLower.TLabel")
vertsecsymbol.grid(row=5, column=3, sticky="W")

drivebutton = tk.Button(coordframe, text="Drive", width=12, height=1, wraplength=70,
                        background="light sky blue", activebackground="deep sky blue", command=coorddrive)
drivebutton.grid(row=0, column=4)
stopbutton = tk.Button(coordframe, text="Stop", width=12, height=1, wraplength=70,
                       background="light sky blue", activebackground="deep sky blue")
stopbutton.grid(row=1, column=4)
backbutton = tk.Button(coordframe, text="Back", width=12, height=1, wraplength=70,
                       background="light sky blue", activebackground="deep sky blue",
                       command=lambda: raise_frame(mainframe))
backbutton.grid(row=4, column=4)
quitbutton = tk.Button(coordframe, text="Quit", width=12, height=1, wraplength=70,
                       background="light sky blue", activebackground="deep sky blue", command=quit)
quitbutton.grid(row=5, column=4)

# Widgets for objframe
objchoicelabel = ttk.Label(objframe, text="Object:", style="WiderLower.TLabel")
objchoicelabel.grid(row=0, column=0)
objchoicemenu = ttk.Combobox(objframe, values=["Sun", "Moon", "Galactic Centre", "Crab Pulsar"], state="readonly",
                             width=13)
objchoicemenu.grid(row=0, column=1)
tracklabel = ttk.Label(objframe, text="Track?", style="WiderLower.TLabel")
tracklabel.grid(row=1, column=0)
trackcheck = ttk.Checkbutton(objframe, style="Lower.TCheckbutton")
trackcheck.grid(row=1, column=1)
risesetbutton = tk.Button(objframe, text="Generate rise/set times", width=12, height=5, wraplength=50,
                          background="light sky blue", activebackground="deep sky blue")
risesetbutton.grid(row=3, column=0, rowspan=2)
risinglabel = ttk.Label(objframe, text="Rising:\nPlaceholder", style="WiderLower.TLabel")
risinglabel.grid(row=3, column=1)
settinglabel = ttk.Label(objframe, text="Setting:\nPlaceholder", style="WiderLower.TLabel")
settinglabel.grid(row=4, column=1)

drivebutton = tk.Button(objframe, text="Drive", width=12, height=1, wraplength=70,
                        background="light sky blue", activebackground="deep sky blue")
drivebutton.grid(row=0, column=2)
stopbutton = tk.Button(objframe, text="Stop", width=12, height=1, wraplength=70,
                       background="light sky blue", activebackground="deep sky blue")
stopbutton.grid(row=1, column=2)
backbutton = tk.Button(objframe, text="Back", width=12, height=1, wraplength=70,
                       background="light sky blue", activebackground="deep sky blue",
                       command=lambda: raise_frame(mainframe))
backbutton.grid(row=3, column=2)
quitbutton = tk.Button(objframe, text="Quit", width=12, height=1, wraplength=70,
                       background="light sky blue", activebackground="deep sky blue", command=quit)
quitbutton.grid(row=4, column=2)


getlocation()
tick()

raise_frame(mainframe)
maininterface.mainloop()
