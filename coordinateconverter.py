# Converter between equatorial, horizontal and galactic coordinates to azimuth-elevation
# Allows input of the original coordinate system and a horizontal and vertical coordinate

def coordinate_convert(convertfrom='noinput', horizontal='noinput', vertical='noinput'):

    # Import regex and ephem for later use
    import re
    import ephem

    # Coordinates given are approximate and temporary: update when telescope has fixed position
    mylocation = ephem.Observer()
    mylocation.long, mylocation.lat = '-4.35', '55.92'

    # Initially, checking for missing inputs; if any input is missing, the function can't create an output
    # There may be a neater way to do this, but for now this is functional
    # Also import regex and ephem for later use
    if convertfrom == 'noinput':
        print('Error: missing input. Please input the coordinate system to convert from.')
    elif horizontal == 'noinput':
        print('Error: missing input. Please input a horizontal coordinate.')
    elif vertical == 'noinput':
        print('Error: missing input. Please input a vertical coordinate.')
    else:

        # Check input coordinate formats
        # Coordinates should be input either as a float/int or as a string of hours/degrees, minutes and seconds
        # Should recognise the letter format regardless of spacing
        # Two cases for strings: input as degrees or input as hours
        # Final values for horizontal and vertical coordinates will be given as floats

        if type(horizontal) == str:

            if re.search("(\d*(\.\d*)?)(\s*)?h(\s*)?((\d*(\.\d*)?)(\s*)?m)?(\s*)?((\d*(\.\d*)?)(\s*)?s)?", horizontal) is not None:
                horizcoords = re.findall("(\d+(\.\d+)?)", horizontal)
                hourtodeg = float(horizcoords[0][0])*15
                mintodeg = float(horizcoords[1][0])/60
                sectodeg = float(horizcoords[2][0])/3600
                horizontaldeg = str(hourtodeg+mintodeg+sectodeg)
            elif re.search("(\d*(\.\d*)?)(\s*)?d(\s*)?((\d*(\.\d*)?)(\s*)?m)?(\s*)?((\d*(\.\d*)?)(\s*)?s)?", horizontal) is not None:
                horizcoords = re.findall("(\d+(\.\d+)?)", horizontal)
                degtodeg = float(horizcoords[0][0])
                mintodeg = float(horizcoords[1][0]) / 60
                sectodeg = float(horizcoords[2][0]) / 3600
                horizontaldeg = str(degtodeg + mintodeg + sectodeg)
            else:
                print('Error: invalid coordinate. Please give horizontal coordinate in degrees (float) or hms/dms (string).')

        elif type(horizontal) == float or int:
            horizontaldeg = str(horizontal)

        else:
            print('Error: invalid coordinate. Please give horizontal coordinate in degrees (float) or hms/dms (string).')

        if type(vertical) == str:

            if re.search("(\d*(\.\d*)?)(\s*)?h(\s*)?((\d*(\.\d*)?)(\s*)?m)?(\s*)?((\d*(\.\d*)?)(\s*)?s)?", vertical) is not None:
                vertcoords = re.findall("(\d+(\.\d+)?)", vertical)
                hourtodeg = float(vertcoords[0][0])*15
                mintodeg = float(vertcoords[1][0])/60
                sectodeg = float(vertcoords[2][0])/3600
                verticaldeg = str(hourtodeg+mintodeg+sectodeg)
            elif re.search("(\d*(\.\d*)?)(\s*)?d(\s*)?((\d*(\.\d*)?)(\s*)?m)?(\s*)?((\d*(\.\d*)?)(\s*)?s)?", vertical) is not None:
                vertcoords = re.findall("(\d+(\.\d+)?)", vertical)
                degtodeg = float(vertcoords[0][0])
                mintodeg = float(vertcoords[1][0]) / 60
                sectodeg = float(vertcoords[2][0]) / 3600
                verticaldeg = str(degtodeg + mintodeg + sectodeg)
            else:
                print('Error: invalid coordinate. Please give horizontal coordinate in degrees (float) or hms/dms (string).')

        elif type(vertical) == float or int:
            verticaldeg = str(vertical)

        else:
            print('Error: invalid coordinate. Please give vertical coordinate in degrees (float) or hms/dms (string).')

        # Check if the coordinate system to convert from is valid
        if convertfrom == "horizontal":

               # Horizontal to az-el
                skylocation = ephem.Equatorial(horizontaldeg,verticaldeg)
                referencestar = ephem.FixedBody()
                referencestar._ra = skylocation.ra
                referencestar._dec = skylocation.dec
                referencestar._epoch = skylocation.epoch
                referencestar.compute(mylocation)

                gotoaz = referencestar.az
                gotoel = referencestar.alt

                return (gotoaz, gotoel)

        elif convertfrom == "equatorial":

                # Equatorial to az-el
                skylocation = ephem.Equatorial(horizontaldeg, verticaldeg)
                referencestar = ephem.FixedBody()
                referencestar._ra = skylocation.ra
                referencestar._dec = skylocation.dec
                referencestar._epoch = skylocation.epoch
                referencestar.compute(mylocation)

                gotoaz = referencestar.az
                gotoel = referencestar.alt

                return (gotoaz, gotoel)

        elif convertfrom == "galactic":

               # Galactic to az-el
               # As equatorial is the base system for ephem, need to convert to this
                skylocation = ephem.Equatorial(ephem.Galactic(horizontaldeg, verticaldeg))
                referencestar = ephem.FixedBody()
                referencestar._ra = skylocation.ra
                referencestar._dec = skylocation.dec
                referencestar._epoch = skylocation.epoch
                referencestar.compute(mylocation)

                gotoaz = referencestar.az
                gotoel = referencestar.alt

                return (gotoaz, gotoel)

               # Possible later addition - ecliptic coordinates

        else:

            print("Error: coordinate system not recognised. Please reinput the coordinate system to convert from.")
