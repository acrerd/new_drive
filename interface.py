import tkinter as tk
import tkinter.ttk as ttk
import time
import math
import ephem
import datetime
import serial

# To allow retrying after errors, the whole code is wrapped in a function
def runinterface():

    # This function allows the program to rerun from the start, destroying all active tkinter windows
    # Used for errors where the driver isn't connected - F
    def rerunandquit():
        nodriverwindow.destroy()
        maininterface.destroy()
        runinterface()


    # Driver code and comments c/o Kingsley Baxter

    # Predefining a bunch of variables that are used later on to prevent error and speed up allocation
    dataAZ = [0, 0, 0, 0]
    dataEL = [0, 0, 0, 0]
    NULL = chr(0)
    Azimuth = 0.0
    Elevation = 0.0
    # Setting up all the Tkinter Variables, these act as global variables but I think they're a bit safer, also python is
    # terrible at functions
    maininterface = tk.Tk()
    Az = tk.StringVar(maininterface)
    Az.set("0.0")
    El = tk.StringVar(maininterface)
    El.set("0.0")
    TarAZ = tk.StringVar(maininterface)
    TarAZ.set("0.0")
    TarEL = tk.StringVar(maininterface)
    TarEL.set("0.0")
    Already = tk.BooleanVar(maininterface)
    Already.set(True)
    # Defining and Opening the port used in the program. Only exiting the program through the GUI will close the Port.
    # That needs to change a bit.
    Server = serial.Serial()
    Server.port = 'COM3'
    Server.baudrate = 460800
    try:
        Server.open()
    except serial.serialutil.SerialException:
        # Popup error if the driver isn't plugged in - F
        nodriverwindow = tk.Toplevel()
        nodriverwindow.title("Error")
        nodriverframe = tk.Frame(nodriverwindow, background="white")
        nodriverframe.columnconfigure(0, minsize=150)
        nodriverframe.columnconfigure(1, minsize=150)
        nodriverframe.rowconfigure(0, minsize=50)
        nodriverframe.rowconfigure(1, minsize=50)
        warning = tk.Label(nodriverframe, text="Error: driver not detected.\nPlease ensure the driver is connected to the "
                                               "computer and turned on.", justify=tk.CENTER, background="white",
                           wraplength=150)
        okbutton = tk.Button(nodriverframe, text="Retry", width=12, height=1, wraplength=70,
                             background="light sky blue", activebackground="deep sky blue",
                             command=lambda: rerunandquit())
        exitbutton = tk.Button(nodriverframe, text="Quit", width=12, height=1, wraplength=70,
                               background="light sky blue", activebackground="deep sky blue", command=lambda: quit())
        nodriverframe.grid(row=0, column=0, columnspan=2, rowspan=2)
        warning.grid(row=0, column=0, columnspan=2)
        okbutton.grid(row=1, column=0)
        exitbutton.grid(row=1, column=1)
        maininterface.withdraw()
        nodriverwindow.mainloop()


    # The Rot2Prog protocol has three commands: Goto, Status, and Stop. Status and Stop don't require coordinate input
    # So they can be defined now to improve efficiency in the program. See above for an explanation of the protocol.
    Stop_String = "W" + NULL * 10 + chr(15) + chr(32)
    Stop_Command = Stop_String.encode('utf-8')
    Read_String = "W" + NULL * 10 + chr(31) + chr(32)
    Read_Command = Read_String.encode('utf-8')


    # The Stop function is the first one to be defined so that it can be inserted into future functions.
    def Stop_Drive():
        "Stops the Drive"
        Server.write(Stop_Command)


    # The read function, it sends the command and then reads the response. See above for a detailed breakdown of the
    # response. Due to wanting the Drive to always move in a certain direction another function BetaSet_Drive() is called
    # That function might need to be tidied up.
    def ReadFunction():
        "Reads the current position of the drive and passes it back into tkinter."
        Server.write(Read_Command)
        Data = Server.read(11).decode('utf-8')
        Bin = Server.read()
        DataAZ = Data[1:5]  # The Azimuth is the 2nd through 5th character sent in the response
        DataEL = Data[6:10]  # The Elevation is the 6th through 10th character sent in ther response
        for e in range(0, 4):
            dataAZ[e] = ord(DataAZ[e])  # converts the ascii character into a number since it uses ascii index 0-10 the
            # number doesn't need to be manipulated further.
            dataEL[e] = ord(DataEL[e])
        Azimuth = ((dataAZ[0] * 1000 + dataAZ[1] * 100 + dataAZ[2] * 10 + dataAZ[3]) / 10) - 360
        Elevation = ((dataEL[0] * 1000 + dataEL[1] * 100 + dataEL[2] * 10 + dataEL[3]) / 10) - 360
        Azimuth = "{0:.1f}".format(Azimuth)
        Elevation = "{0:.1f}".format(Elevation)
        Az.set(Azimuth)
        El.set(Elevation)
        if Already.get() == False:
            BetaSet_Drive()

        maininterface.after(50, ReadFunction)  # Returns the two numbers so they can be displayed.


    # Important function. Can't predefine the command since it changes with the coordinates. Will set an Azimuth and
    # Elevation for the Drive to point at.
    def BetaSet_Drive():
        # "This function is used when the Drive needs to move more than 180 degrees to make sure the drive goes the long
        # way round."
        Target = float(TarAZ.get())
        Current = float(Az.get())
        Comparison = Target - Current
        if abs(Comparison) > 180:
            return

        AZ = Target
        AZ = AZ + 360
        AZ = str(AZ)  # Its easier to split up a string then a number, at least to my knowledge.
        if len(AZ) < 5:
            AZ = (5 - len(AZ)) * "0" + AZ
        AZhundreds = AZ[0]  # Seperates the Digits out so that they can be read into their own byte.
        AZtens = AZ[1]
        AZdigits = AZ[2]
        AZtenths = AZ[4]

        EL = float(TarEL.get()) + 360
        EL = str(EL)  # Its easier to split up a string then a number, at least to my knowledge.
        if len(EL) < 5:
            EL = (5 - len(EL)) * "0" + AZ
        ELhundreds = AZ[0]  # Seperates the Digits out so that they can be read into their own byte.
        ELtens = AZ[1]
        ELdigits = AZ[2]
        ELtenths = AZ[4]

        ACC = chr(10)  # The Accuracy of this driver is 0.1 Degrees Therefore to change the numbers from integers to floats
        # a quotient of 10 is required.
        COMMAND = chr(47)  # Command 47 is the Set command, there are two others Read (31) and Stop (15).
        END = chr(32)  # The End of the transmission is marked by a space bar or ascii character 32.

        Set_String = "W" + AZhundreds + AZtens + AZdigits + AZtenths + ACC + ELhundreds + ELtens + ELdigits + ELtenths + \
                     ACC + COMMAND + END  # The culmination of the processes above are fed into this string.
        Set_Command = Set_String.encode('utf-8')  # Which is then encoded into byte information to be sent.
        Server.write(Stop_Command)
        time.sleep(0.1)
        Server.write(Set_Command)
        Already.set(True)


    # Most important function will take in an Az El and make the drive turn to that location. Its pretty robust with the
    # error messages above. Needs BetaSet_Drive to function due to the BREAK part of the code. Important thing about this
    # code is that the Tkinter variables are the key. They are used as checks and balances. Make sure they are all there or
    # that all reference to them is gone otherwise problems will occur.
    def Set_Drive(AZInput, ELInput):
        "Drives the Drive to a set Azimuth and Elevation"
        BREAK = float(Az.get()) + 179
        BREAK2 = float(Az.get()) - 179
        try:
            AZ = float(AZInput)  # Converts the string to a Float for numerical manipulation
            EL = float(ELInput)
        except ValueError:
            return

        if (EL < -0) or (EL > 90):
            return

        if (AZ < 0) or (AZ > 360):
            return
        TarAZ.set(str(AZ))
        TarEL.set(str(EL))

        if AZ > BREAK:
            AZ = BREAK
            Already.set(False)
        elif AZ < BREAK2:
            AZ = BREAK2
            Already.set(False)
            # The controller can't take negative number so all number are increased by 360 degrees

        EL = EL + 360
        AZ = AZ + 360
        AZ = str(AZ)  # Its easier to split up a string then a number, at least to my knowledge.
        if len(AZ) < 5:
            AZ = (5 - len(AZ)) * "0" + AZ
        EL = str(EL)
        if len(EL) < 5:
            EL = (5 - len(EL)) * "0" + AZ

        AZhundreds = AZ[0]  # Seperates the Digits out so that they can be read into their own byte.
        AZtens = AZ[1]
        AZdigits = AZ[2]
        AZtenths = AZ[4]

        ELhundreds = EL[0]  # Same for Elevation as Azimuth
        ELtens = EL[1]
        ELdigits = EL[2]
        ELtenths = EL[4]

        ACC = chr(10)  # The Accuracy of this driver is 0.1 Degrees Therefore to change the numbers from integers to floats
        # a quotient of 10 is required.
        COMMAND = chr(47)  # Command 47 is the Set command, there are two others Read (31) and Stop (15).
        END = chr(32)  # The End of the transmission is marked by a space bar or ascii character 32.

        Set_String = "W" + AZhundreds + AZtens + AZdigits + AZtenths + ACC + ELhundreds + ELtens + ELdigits + ELtenths + \
                     ACC + COMMAND + END  # The culmination of the processes above are fed into this string.
        Set_Command = Set_String.encode('utf-8')  # Which is then encoded into byte information to be sent.

        Server.write(Set_Command)


        # Used to exit the program, has the benefit of closing the port as well so other programs can use it. Now attached
        # to the protocol of closing the window itself.


    # From hereon, code and comments c/o Fiona Porter

    # Establish the telescope's location for ephem
    # Coordinates here are those for the telescope site as given by Google Maps
    mylocation = ephem.Observer()
    mylocation.long, mylocation.lat = '-4.307105', '55.902528'


    # Converter between angles in fractional degrees and dms; produces output string for the interface coordinates
    def todms(inputangle):

        # Separate out degrees, minutes and seconds, initially as ints or floats
        degree = math.floor(inputangle)
        firstremainder = inputangle-degree
        minute = math.floor(firstremainder*60)
        secondremainder = (firstremainder*60)-minute
        second = round(secondremainder*60, 1)

        # The rounding sometimes causes the seconds value to appear as 60; this corrects it
        if second == 60:
            second = 0
            minute = minute + 1

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
    def tick():
        timenow = time.strftime("%H:%M:%S", time.gmtime())
        clock.config(text=timenow)
        clock.after(500, tick)


    def getlocation():
        # Get current az-el from driver
        # Convert to ra-dec
        # Produce four labels for az-el and ra-dec coordinates
        # Update this periodically - 50ms is enough to make the change of numbers look smooth
        aznow = float(Az.get())  # placeholder
        elnow = float(El.get())  # placeholder
        # While the program is running, the clock won't automatically update
        # This updates it manually each loop
        mylocation.date = datetime.datetime.utcnow()
        [rarad, decrad] = mylocation.radec_of(math.radians(aznow), math.radians(elnow))
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
        # This should drive to fixed coordinates
        homeaz = 0  # placeholder
        homeel = 0  # placeholder
        Set_Drive(homeaz, homeel)

    def gostow():
        # This should drive to fixed coordinates
        stowaz = 0  # placeholder
        stowel = 90  # placeholder
        Set_Drive(stowaz, stowel)

    def mainquit():
        # Quit function for later use
        maininterface.quit()

    def stowandquit():
        # Special case of the stow command that also quits the interface afterwards
        stowaz = 0  # placeholder
        stowel = 90  # placeholder
        Set_Drive(stowaz, stowel)
        maininterface.quit()

    def stowcheck():
        # Offers a prompt to drive the telescope to the stow position before shutting the interface
        stowwindow = tk.Toplevel()
        stowwindow.title("Stow?")
        stowframe = ttk.Frame(stowwindow, style="Lower.TFrame")
        stowframe.columnconfigure(0, minsize=150)
        stowframe.columnconfigure(1, minsize=150)
        stowframe.rowconfigure(0, minsize=50)
        stowframe.rowconfigure(1, minsize=50)
        warning = ttk.Label(stowframe, text="Stow the telescope before quitting?", justify=tk.CENTER,
                            style="ErrorLower.TLabel", wraplength=150)
        okbutton = tk.Button(stowframe, text="Yes", width=12, height=1, wraplength=70,
                             background="light sky blue", activebackground="deep sky blue", command=lambda: stowandquit())
        exitbutton = tk.Button(stowframe, text="No", width=12, height=1, wraplength=70,
                               background="light sky blue", activebackground="deep sky blue", command=lambda: mainquit())
        stowframe.grid(row=0, column=0, columnspan=2, rowspan=2)
        warning.grid(row=0, column=0, columnspan=2)
        okbutton.grid(row=1, column=0)
        exitbutton.grid(row=1, column=1)

    def missinginputerror(problemphrase):
        # This error message appears when information is missing
        # The "problemphrase" input allows for a custom message to be displayed for each different error
        errorwindow = tk.Toplevel()
        errorwindow.title("Error")
        errorframe = ttk.Frame(errorwindow, style="Lower.TFrame")
        errorframe.columnconfigure(0, minsize=200)
        errorframe.rowconfigure(0, minsize=50)
        errorframe.rowconfigure(1, minsize=50)
        warning = ttk.Label(errorframe, text="Error: missing input.\nPlease select " + problemphrase, justify=tk.CENTER,
                            style="ErrorLower.TLabel", wraplength=150)
        okbutton = tk.Button(errorframe, text="OK", width=12, height=1, wraplength=70,
                             background="light sky blue", activebackground="deep sky blue", command=errorwindow.destroy)
        errorframe.grid(row=0, column=0)
        warning.grid(row=0, column=0)
        okbutton.grid(row=1, column=0)

    def invalidinputerror(problemphrase):
        # This error message appears when input isn't valid - for example, text in a field that expects numbers
        # The "problemphrase" input allows for a custom message to be displayed for each different error
        errorwindow = tk.Toplevel()
        errorwindow.title("Error")
        errorframe = ttk.Frame(errorwindow, style="Lower.TFrame")
        errorframe.columnconfigure(0, minsize=200)
        errorframe.rowconfigure(0, minsize=50)
        errorframe.rowconfigure(1, minsize=50)
        warning = ttk.Label(errorframe, text="Error: invalid input.\nPlease input " + problemphrase, justify=tk.CENTER,
                            style="ErrorLower.TLabel", wraplength=150)
        okbutton = tk.Button(errorframe, text="OK", width=12, height=1, wraplength=70,
                             background="light sky blue", activebackground="deep sky blue", command=errorwindow.destroy)
        errorframe.grid(row=0, column=0)
        warning.grid(row=0, column=0)
        okbutton.grid(row=1, column=0)

    def coordunavailableerror():
        # This accounts for coordinates being below the horizon and prevents attempts to drive there
        errorwindow = tk.Toplevel()
        errorwindow.title("Error")
        errorframe = ttk.Frame(errorwindow, style="Lower.TFrame")
        errorframe.columnconfigure(0, minsize=200)
        errorframe.rowconfigure(0, minsize=50)
        errorframe.rowconfigure(1, minsize=50)
        warning = ttk.Label(errorframe, text="Error: coordinates unavailable.\nThis point is currently below the "
                                             "horizon.", justify=tk.CENTER, style="ErrorLower.TLabel", wraplength=150)
        okbutton = tk.Button(errorframe, text="OK", width=12, height=1, wraplength=70,
                             background="light sky blue", activebackground="deep sky blue", command=errorwindow.destroy)
        errorframe.grid(row=0, column=0)
        warning.grid(row=0, column=0)
        okbutton.grid(row=1, column=0)

    def coorddrive():
        # This sets up the driver to drive to the requested coordinates
        # First, check which coordinate system was selected
        if coordsyschoice.get() == "":
            missinginputerror("a coordinate system.")
            return
            # The above should display a popup with that error message and break out of this function
            # Can't run at all without a coordinate system
            # Want to keep the interface's input so it can be easily fixed
        else:
            # This value will be used later when coordinate conversions need done
            choice = coordsyschoice.get()
        # Next, get horizontal coordinates
        # The below code is the series of checks to make sure the input provided is sensible
        # Details for the formatting it demands are available for display on the wiki
        if len(horizdeg.get()) > 0:
            try:
                horizdegval = int(horizdeg.get())
                horizdecimaldeg = horizdegval
                if horizdecimaldeg < 0 or horizdecimaldeg > 360:
                    invalidinputerror("a horizontal degree value between 0 and 360.")
                    return
                else:
                    pass
                if len(horizmin.get()) > 0:
                    try:
                        horizminval = int(horizmin.get())
                        if horizminval < 0 or horizminval >= 60:
                            invalidinputerror("a horizontal minute value between 0 and 60.")
                            return
                        else:
                            pass
                        horizdecimalmin = horizminval/60
                        if len(horizsec.get()) > 0:
                            try:
                                horizsecval = int(horizsec.get())
                                if horizsecval < 0 or horizsecval >= 60:
                                    invalidinputerror("a horizontal second value between 0 and 60.")
                                    return
                                else:
                                    pass
                                horizdecimalsec = horizsecval/3600
                                horizdecimaltotal = horizdecimaldeg + horizdecimalmin + horizdecimalsec
                            except ValueError:
                                try:
                                    horizsecval = float(horizsec.get())
                                    if horizminval < 0 or horizminval >= 60:
                                        invalidinputerror("a horizontal minute value between 0 and 60.")
                                        return
                                    else:
                                        pass
                                    horizdecimalsec = horizsecval/3600
                                    horizdecimaltotal = horizdecimaldeg + horizdecimalmin + horizdecimalsec
                                except ValueError:
                                    invalidinputerror("coordinates as numbers only.")
                                    return
                        else:
                            horizdecimaltotal = horizdecimaldeg + horizdecimalmin
                    except ValueError:
                        try:
                            horizminval = float(horizmin.get())
                            if horizminval < 0 or horizminval >= 60:
                                invalidinputerror("a horizontal minute value between 0 and 60.")
                                return
                            else:
                                pass
                            horizdecimalmin = horizminval/60
                            horizdecimaltotal = horizdecimaldeg + horizdecimalmin
                            if len(horizsec.get()) > 0:
                                invalidinputerror("coordinates using the style provided by the wiki.")
                                return
                            else:
                                pass
                        except ValueError:
                            invalidinputerror("coordinates as numbers only.")
                            return
                elif len(horizsec.get()) > 0:
                    try:
                        horizsecval = int(horizsec.get())
                        if horizsecval < 0 or horizsecval >= 60:
                            invalidinputerror("a horizontal second value between 0 and 60.")
                            return
                        else:
                            pass
                        horizdecimalsec = horizsecval / 3600
                        horizdecimaltotal = horizdecimaldeg + horizdecimalsec
                    except ValueError:
                        try:
                            horizsecval = float(horizsec.get())
                            if horizsecval < 0 or horizsecval >= 60:
                                invalidinputerror("a horizontal minute value between 0 and 60.")
                                return
                            else:
                                pass
                            horizdecimalsec = horizsecval / 3600
                            horizdecimaltotal = horizdecimaldeg + horizdecimalsec
                        except ValueError:
                            invalidinputerror("coordinates as numbers only.")
                            return
                else:
                    horizdecimaltotal = horizdecimaldeg
            except ValueError:
                try:
                    horizdegval = float(horizdeg.get())
                    if horizdegval < 0 or horizdegval >= 60:
                        invalidinputerror("a horizontal degree value between 0 and 360.")
                        return
                    else:
                        pass
                    horizdecimaldeg = horizdegval
                    horizdecimaltotal = horizdecimaldeg
                    if len(horizmin.get()) > 0:
                        invalidinputerror("coordinates using the style provided by the wiki.")
                        return
                    elif len(horizsec.get()) > 0:
                        invalidinputerror("coordinates using the style provided by the wiki.")
                        return
                    else:
                        pass
                except ValueError:
                    invalidinputerror("coordinates as numbers only.")
                    return
        elif len(horizmin.get()) > 0:
            try:
                horizminval = int(horizmin.get())
                if horizminval < 0 or horizminval >= 60:
                    invalidinputerror("a horizontal minute value between 0 and 60.")
                    return
                else:
                    pass
                horizdecimalmin = horizminval/60
                if len(horizsec.get()) > 0:
                    try:
                        horizsecval = int(horizsec.get())
                        if horizsecval < 0 or horizsecval >= 60:
                            invalidinputerror("a horizontal second value between 0 and 60.")
                            return
                        else:
                            pass
                        horizdecimalsec = horizsecval/3600
                        horizdecimaltotal = horizdecimalmin + horizdecimalsec
                    except ValueError:
                        try:
                            horizsecval = float(horizsec.get())
                            if horizsecval < 0 or horizsecval >= 60:
                                invalidinputerror("a horizontal second value between 0 and 60.")
                                return
                            else:
                                pass
                            horizdecimalsec = horizsecval/3600
                            horizdecimaltotal = horizdecimalmin + horizdecimalsec
                        except ValueError:
                            invalidinputerror("coordinates as numbers only.")
                            return
                else:
                    horizdecimaltotal = horizdecimalmin
            except ValueError:
                try:
                    horizminval = float(horizmin.get())
                    if horizminval < 0 or horizminval >= 60:
                        invalidinputerror("a horizontal minute value between 0 and 60.")
                        return
                    else:
                        pass
                    horizdecimalmin = horizminval/60
                    horizdecimaltotal = horizdecimalmin
                    if len(horizsec.get()) > 0:
                        invalidinputerror("coordinates using the style provided by the wiki.")
                        return
                    else:
                        pass
                except ValueError:
                    invalidinputerror("coordinates as numbers only.")
                    return
        elif len(horizsec.get()) > 0:
            try:
                horizsecval = int(horizsec.get())
                if horizsecval < 0 or horizsecval >= 60:
                    invalidinputerror("a horizontal second value between 0 and 60.")
                    return
                else:
                    pass
                horizdecimalsec = horizsecval/3600
                horizdecimaltotal = horizdecimalsec
            except ValueError:
                try:
                    horizsecval = float(horizsec.get())
                    if horizsecval < 0 or horizsecval >= 60:
                        invalidinputerror("a horizontal second value between 0 and 60.")
                        return
                    else:
                        pass
                    horizdecimalsec = horizsecval/3600
                    horizdecimaltotal = horizdecimalsec
                except ValueError:
                    invalidinputerror("coordinates as numbers only.")
                    return
        else:
            missinginputerror("a horizontal coordinate.")
            return
        # Next, get vertical coordinates
        # Same set of checks as above
        if len(vertdeg.get()) > 0:
            isnegative = tk.BooleanVar(maininterface)
            isnegative.set(False)
            try:
                vertdegval = int(vertdeg.get())
                if vertdegval < -90 or vertdegval > 90:
                    missinginputerror("a vertical degree value between -90 and 90.")
                    return
                else:
                    pass
                if vertdegval < 0:
                    isnegative.set(True)
                    vertdegval = abs(vertdegval)
                else:
                    pass
                vertdecimaldeg = vertdegval
                if len(vertmin.get()) > 0:
                    try:
                        vertminval = int(vertmin.get())
                        if vertminval < 0 or vertminval >= 60:
                            invalidinputerror("a vertical minute value between 0 and 60.")
                            return
                        else:
                            pass
                        vertdecimalmin = vertminval / 60
                        if len(vertsec.get()) > 0:
                            try:
                                vertsecval = int(vertsec.get())
                                if vertsecval < 0 or vertsecval >= 60:
                                    invalidinputerror("a vertical second value between 0 and 60.")
                                    return
                                else:
                                    pass
                                vertdecimalsec = vertsecval / 3600
                                vertdecimaltotal = vertdecimaldeg + vertdecimalmin + vertdecimalsec
                            except ValueError:
                                try:
                                    vertsecval = float(vertsec.get())
                                    if vertsecval < 0 or vertsecval >= 60:
                                        invalidinputerror("a vertical second value between 0 and 60.")
                                        return
                                    else:
                                        pass
                                    vertdecimalsec = vertsecval / 3600
                                    vertdecimaltotal = vertdecimaldeg + vertdecimalmin + vertdecimalsec
                                except ValueError:
                                    invalidinputerror("coordinates as numbers only.")
                                    return
                        else:
                            vertdecimaltotal = vertdecimaldeg + vertdecimalmin
                    except ValueError:
                        try:
                            vertminval = float(vertmin.get())
                            if vertminval < 0 or vertminval >= 60:
                                invalidinputerror("a vertical minute value between 0 and 60.")
                                return
                            else:
                                pass
                            vertdecimalmin = vertminval / 60
                            vertdecimaltotal = vertdecimaldeg + vertdecimalmin
                            if len(vertsec.get()) > 0:
                                invalidinputerror("coordinates using the style provided by the wiki.")
                                return
                            else:
                                pass
                        except ValueError:
                            invalidinputerror("coordinates as numbers only.")
                            return
                elif len(vertsec.get()) > 0:
                    try:
                        vertsecval = int(vertsec.get())
                        if vertsecval < 0 or vertsecval >= 60:
                            invalidinputerror("a vertical second value between 0 and 60.")
                            return
                        else:
                            pass
                        vertdecimalsec = vertsecval / 3600
                        vertdecimaltotal = vertdecimaldeg + vertdecimalsec
                    except ValueError:
                        try:
                            vertsecval = float(vertsec.get())
                            if vertsecval < 0 or vertsecval >= 60:
                                invalidinputerror("a vertical second value between 0 and 60.")
                                return
                            else:
                                pass
                            vertdecimalsec = vertsecval / 3600
                            vertdecimaltotal = vertdecimaldeg + vertdecimalsec
                        except ValueError:
                            invalidinputerror("coordinates as numbers only.")
                            return
                else:
                    vertdecimaltotal = vertdecimaldeg
            except ValueError:
                try:
                    vertdegval = float(vertdeg.get())
                    if vertdegval < -90 or vertdegval > 90:
                        invalidinputerror("a vertical degree value between -90 and 90.")
                        return
                    else:
                        pass
                    vertdecimaldeg = vertdegval
                    vertdecimaltotal = vertdecimaldeg
                    if len(vertmin.get()) > 0:
                        invalidinputerror("coordinates using the style provided by the wiki.")
                        return
                    else:
                        pass
                    if len(vertsec.get()) > 0:
                        invalidinputerror("coordinates using the style provided by the wiki.")
                        return
                    else:
                        pass
                except ValueError:
                    invalidinputerror("coordinates as numbers only.")
                    return
        elif len(vertmin.get()) > 0:
            try:
                vertminval = int(vertmin.get())
                if vertminval < 0 or vertminval >= 60:
                    invalidinputerror("a vertical minute value between 0 and 60.")
                    return
                else:
                    pass
                vertdecimalmin = vertminval / 60
                if len(vertsec.get()) > 0:
                    try:
                        vertsecval = int(vertsec.get())
                        if vertsecval < 0 or vertsecval >= 60:
                            invalidinputerror("a vertical second value between 0 and 60.")
                            return
                        else:
                            pass
                        vertdecimalsec = vertsecval / 3600
                        vertdecimaltotal = vertdecimalmin + vertdecimalsec
                    except ValueError:
                        try:
                            vertsecval = float(vertsec.get())
                            if vertsecval < 0 or vertsecval >= 60:
                                invalidinputerror("a vertical second value between 0 and 60.")
                                return
                            else:
                                pass
                            vertdecimalsec = vertsecval / 3600
                            vertdecimaltotal = vertdecimalmin + vertdecimalsec
                        except ValueError:
                            invalidinputerror("coordinates as numbers only.")
                            return
                else:
                    vertdecimaltotal = vertdecimalmin
            except ValueError:
                try:
                    vertminval = float(vertmin.get())
                    if vertminval < 0 or vertminval >= 60:
                        invalidinputerror("a vertical minute value between 0 and 60.")
                        return
                    else:
                        pass
                    vertdecimalmin = vertminval / 60
                    vertdecimaltotal = vertdecimalmin
                    if len(vertsec.get()) > 0:
                        invalidinputerror("coordinates using the style provided by the wiki.")
                        return
                    else:
                        pass
                except ValueError:
                    invalidinputerror("coordinates as numbers only.")
                    return
        elif len(vertsec.get()) > 0:
            try:
                vertsecval = int(vertsec.get())
                if vertsecval < 0 or vertsecval >= 60:
                    invalidinputerror("a vertical second value between 0 and 60.")
                    return
                else:
                    pass
                vertdecimalsec = vertsecval / 3600
                vertdecimaltotal = vertdecimalsec
            except ValueError:
                try:
                    vertsecval = float(vertsec.get())
                    if vertsecval < 0 or vertsecval >= 60:
                        invalidinputerror("a vertical second value between 0 and 60.")
                        return
                    else:
                        pass
                    vertdecimalsec = vertsecval / 3600
                    vertdecimaltotal = vertdecimalsec
                except ValueError:
                    invalidinputerror("coordinates as numbers only.")
                    return
        else:
            missinginputerror("a vertical coordinate.")
            return
        # Handling negative inputs separately, else the addition is -d + m + s rather than -d - m - s as should be
        if isnegative is True:
            vertdecimaltotal = -vertdecimaltotal
        else:
            pass

        horizradiantotal = math.radians(horizdecimaltotal)
        vertradiantotal = math.radians(vertdecimaltotal)

        # Convert the coordinates into az-el if they're not already
        # No error-handling included here, as the coordinate choice was already validated earlier
        if choice == "Ecliptic":
            skylocation = ephem.Equatorial(ephem.Ecliptic(horizradiantotal, vertradiantotal))
            referencestar = ephem.FixedBody()
            referencestar._ra = skylocation.ra
            referencestar._dec = skylocation.dec
            referencestar.compute(mylocation)
            gotoaz = math.degrees(referencestar.az)
            gotoel = math.degrees(referencestar.alt)
        elif choice == "Equatorial":
            skylocation = ephem.Equatorial(horizradiantotal, vertradiantotal)
            referencestar = ephem.FixedBody()
            referencestar._ra = skylocation.ra
            referencestar._dec = skylocation.dec
            referencestar.compute(mylocation)
            gotoaz = math.degrees(referencestar.az)
            gotoel = math.degrees(referencestar.alt)
        elif choice == "Galactic":
            skylocation = ephem.Equatorial(ephem.Galactic(horizradiantotal, vertradiantotal))
            referencestar = ephem.FixedBody()
            referencestar._ra = skylocation.ra
            referencestar._dec = skylocation.dec
            referencestar.compute(mylocation)
            gotoaz = math.degrees(referencestar.az)
            gotoel = math.degrees(referencestar.alt)
        else:
            gotoaz = horizdecimaltotal
            gotoel = vertdecimaltotal
           
        # If the resulting coordinates are below the horizon, prevents attempts to drive to them
        if gotoel < 0:
            coordunavailableerror()
            Stop_Drive()
            return
        else:
            pass
        # The driver has limited precision (0.1 degree/6 minutes) so this rounds the result
        # In practical terms, the seconds in any coordinate system won't make much difference to where the telescope
        # goes; however, the functionality's been left in so if the code is ever reused for another drive, it's
        # available if needed
        gotoaz = round(gotoaz*10)/10
        gotoel = round(gotoel*10)/10

        Set_Drive(gotoaz, gotoel)

        # Tracking updates the position every 24 seconds (equivalent to 0.1 degree)
        if coordtrackchoice.get() == 1 and choice is not "Horizontal":
            coordframe.after(24000, coorddrive)

    def objdrive():
        # This directs the driver to any desired object on the list
        # Objects may be added by appending this list
        if objchoice.get() == "":
            missinginputerror("an object.")
            return
        elif objchoice.get() == "Sun":
            drivetoobj = ephem.Sun(mylocation)
            gotoaz = math.degrees(drivetoobj.az)
            gotoel = math.degrees(drivetoobj.alt)
        elif objchoice.get() == "Moon":
            drivetoobj = ephem.Moon(mylocation)
            gotoaz = drivetoobj.az
            gotoel = drivetoobj.alt
        elif objchoice.get() == "Cassiopeia A":
            drivetoobj = ephem.readdb("Casseopeia A,f,23:23:24.01,58:48:54.0,6,2000")
            drivetoobj.compute(mylocation)
            gotoaz = drivetoobj.az
            gotoel = drivetoobj.alt
        elif objchoice.get() == "Sagittarius A":
            drivetoobj = ephem.readdb("Sagittarius A*,f,17:45:40.04,-29:0:28.2,25,2000")
            drivetoobj.compute(mylocation)
            gotoaz = drivetoobj.az
            gotoel = drivetoobj.alt
        elif objchoice.get() == "Cygnus A":
            drivetoobj = ephem.readdb("Cygnus A,f,19:59:28.36,40:44:02.1,16,2000")
            drivetoobj.compute(mylocation)
            gotoaz = drivetoobj.az
            gotoel = drivetoobj.alt
        elif objchoice.get() == "Crab Nebula":
            drivetoobj = ephem.readdb("Crab Nebula,f,5:34:31.94,22:00:52.2,8.5,2000")
            drivetoobj.compute(mylocation)
            gotoaz = drivetoobj.az
            gotoel = drivetoobj.alt
        # A check to ensure the object is visible before attempting to drive to it
        # If tracking is currently on, figure out when the object is next up and drive to it then
        # The time till next rising is given in milliseconds
        if gotoel < 0:
            if objtrackchoice.get == 1:
                prevset = mylocation.previous_setting(drivetoobj)
                nextrise = mylocation.next_rising(drivetoobj)
                timetillrise = round((nextrise-prevset)*24*60*60*1000)
                objframe.after(timetillrise, objdrive)
            else:
                coordunavailableerror()
                Stop_Drive()
                return
        else:
            Set_Drive(gotoaz, gotoel)

        # Tracking updates the position every 24 seconds (equivalent to 0.1 degree)
        if objtrackchoice.get() == 1:
            objframe.after(24000, objdrive)


    def getriseset():
        # Generating the rising and setting times for each body
        if objchoice.get() == "":
            missinginputerror("an object.")
            return
        elif objchoice.get() == "Sun":
            findriseset = ephem.Sun(mylocation)
        elif objchoice.get() == "Moon":
            findriseset = ephem.Moon(mylocation)
        elif objchoice.get() == "Cassiopeia A":
            findriseset = ephem.readdb("Casseopeia A,f,23:23:24.01,58:48:54.0,6,2000")
            findriseset.compute(mylocation)
        elif objchoice.get() == "Sagittarius A":
            findriseset = ephem.readdb("Sagittarius A*,f,17:45:40.04,-29:0:28.2,25,2000")
            findriseset.compute(mylocation)
        elif objchoice.get() == "Cygnus A":
            findriseset = ephem.readdb("Cygnus A,f,19:59:28.36,40:44:02.1,16,2000")
            findriseset.compute(mylocation)
        elif objchoice.get() == "Crab Nebula":
            findriseset = ephem.readdb("Crab Nebula,f,5:34:31.94,22:00:52.2,8.5,2000")
            findriseset.compute(mylocation)
        try:
            prevrise = mylocation.previous_rising(findriseset)
            prevset = mylocation.previous_setting(findriseset)
            nextrise = mylocation.next_rising(findriseset)
            nextset = mylocation.next_setting(findriseset)
            # If prevrise > prevset, the object is currently up; if vice versa, the object is currently down
            # There's a slightly different display depending on which is the case
            if prevrise > prevset:
                risesettext.set("Rose at:\n" + str(prevrise) + "\nSetting at:\n" + str(nextset))
            else:
                risesettext.set("Set at:\n" + str(prevset) + "\nRising at:\n" + str(nextrise))
        # Some objects never set; this accounts for them
        except ephem.AlwaysUpError:
            risesettext.set("Always risen")

    # The different interface windows are actually just different frames stacked in the same place and raised as needed
    # This function performs the raising
    def raise_frame(frame):
        frame.tkraise()

    # Setting up main interface window
    # Note: styles won't work unless placed after the maininterface declaration
    maininterface.deiconify()
    maininterface.title("Telescope Interface")
    maininterface.resizable(0, 0)  # Disabled window resizing - if annoying later, remove

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
    style.configure("ErrorLower.TLabel", foreground="black", background="white")
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
    coordtracklabel = ttk.Label(coordframe, text="Track?", style="WiderLower.TLabel")
    coordtracklabel.grid(row=1, column=0)
    coordtrackchoice = tk.IntVar()
    coordtrackcheck = ttk.Checkbutton(coordframe, style="Lower.TCheckbutton", variable=coordtrackchoice)
    coordtrackcheck.grid(row=1, column=2)

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
                           background="light sky blue", activebackground="deep sky blue", command=lambda: Stop_Drive())
    stopbutton.grid(row=1, column=4)
    backbutton = tk.Button(coordframe, text="Back", width=12, height=1, wraplength=70,
                           background="light sky blue", activebackground="deep sky blue",
                           command=lambda: raise_frame(mainframe))
    backbutton.grid(row=4, column=4)
    quitbutton = tk.Button(coordframe, text="Quit", width=12, height=1, wraplength=70,
                           background="light sky blue", activebackground="deep sky blue", command=lambda: stowcheck())
    quitbutton.grid(row=5, column=4)

    # Widgets for objframe
    objchoicelabel = ttk.Label(objframe, text="Object:", style="WiderLower.TLabel")
    objchoicelabel.grid(row=0, column=0)
    objchoice = tk.StringVar()
    objchoicemenu = ttk.Combobox(objframe, values=["Sun", "Moon", "Cassiopeia A", "Sagittarius A", "Cygnus A",
                                                   "Crab Nebula"], textvariable=objchoice, state="readonly", width=13)
    objchoicemenu.grid(row=0, column=1)
    objtracklabel = ttk.Label(objframe, text="Track?", style="WiderLower.TLabel")
    objtracklabel.grid(row=1, column=0)
    objtrackchoice = tk.IntVar()
    objtrackcheck = ttk.Checkbutton(objframe, style="Lower.TCheckbutton", variable=objtrackchoice)
    objtrackcheck.grid(row=1, column=1)
    risesetbutton = tk.Button(objframe, text="Generate rise/set times", width=12, height=5, wraplength=50,
                              background="light sky blue", activebackground="deep sky blue",
                              command=lambda: getriseset())
    risesetbutton.grid(row=3, column=0, rowspan=2)
    risesettext = tk.StringVar()
    risesetlabel = ttk.Label(objframe, textvariable=risesettext, style="WiderLower.TLabel")
    risesetlabel.grid(row=3, column=1, rowspan=2)

    drivebutton = tk.Button(objframe, text="Drive", width=12, height=1, wraplength=70,
                            background="light sky blue", activebackground="deep sky blue", command=objdrive)
    drivebutton.grid(row=0, column=2)
    stopbutton = tk.Button(objframe, text="Stop", width=12, height=1, wraplength=70,
                           background="light sky blue", activebackground="deep sky blue", command=lambda: Stop_Drive())
    stopbutton.grid(row=1, column=2)
    backbutton = tk.Button(objframe, text="Back", width=12, height=1, wraplength=70,
                           background="light sky blue", activebackground="deep sky blue",
                           command=lambda: raise_frame(mainframe))
    backbutton.grid(row=3, column=2)
    quitbutton = tk.Button(objframe, text="Quit", width=12, height=1, wraplength=70,
                           background="light sky blue", activebackground="deep sky blue", command=lambda: stowcheck())
    quitbutton.grid(row=4, column=2)

    getlocation()
    tick()
    ReadFunction()

    raise_frame(mainframe)
    maininterface.protocol("WM_DELETE_WINDOW", lambda: stowcheck())
    maininterface.mainloop()

runinterface()
