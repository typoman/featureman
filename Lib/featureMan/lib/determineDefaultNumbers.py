NumbersSuffix = ['lnum', 'onum', 'tnum', 'pnum']
defaultNumbers = 'zero one two three four five six seven eight nine'

def get(thisF):
    defList = defaultNumbers.split(' ')
    metricsError = 1
    oldstyleDiff = 17
    width = 0
    tnum = True
    lnum = 0
    defNumber = ''
    firstGlyph = defList[0]
    if firstGlyph in thisF:
        firstGlyph = thisF[firstGlyph]
        if firstGlyph.bounds:
            height = firstGlyph.bounds[-1] - firstGlyph.bounds[1] # basic height is height of the zero
            nuance = height*oldstyleDiff/100
            widthType = NumbersSuffix[2]
            for gl in defList:
                g = thisF[gl]
                if width:
                    if width - metricsError < g.width < width + metricsError and tnum:
                        tnum = True
                    elif tnum:
                        tnum = False
                        widthType = NumbersSuffix[3]
                width = g.width
                gheight = 0
                if g.bounds:
                    gheight = g.bounds[-1] - g.bounds[1]
                if height:
                    if abs(gheight - height) < nuance:
                        lnum += 1
                    else:
                        lnum -= 1
            if lnum > 0:
                defNumber += NumbersSuffix[0]+'_'
            else:
                defNumber += NumbersSuffix[1]+'_'
            defNumber += widthType
