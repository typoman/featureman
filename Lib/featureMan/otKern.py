from featureMan.otSyntax import *
"""
I don't use this module anymore! Instead use the ufo2ft.
"""

class kern(abstractFeature):
    tag = 'kern'
    """ An object to create kern Feature. """
    #  the order of kern pairs definitions are:
    #  1. #  glyph, glyph
    #  2. #  glyph, glyph exceptions
    #  3. #  glyph, group exceptions (enum)
    #  4. #  group, glyph exceptions (enum)
    #  5. #  glyph, group
    #  6. #  group, group/glyph
    #  RTL kerning flag = lookupflag RightToLeft IgnoreMarks
    deleteExtraCharactersInClassMap = {'@': None}

    def __init__(self, fDic, classes):
        super(kern, self).__init__(fDic, classes)
        self.warnings = []
        self.classRules = set() #  class definitions with no flags
        self._classes = set()
        self.emptyClasses = set() #  classes with empty glyphs
        self.kernRules = {} #  map of flags to OT rules
        self.gglist = [] #  type 1: glyph, glyph
        self.ggelist = [] #  type 2: glyph, glyph exceptions
        self.ggrElist = [] #  type 3: glyph, group exceptions (enum)
        self.grgElist = []  #  type 4: group, glyph exceptions (enum)
        self.ggrlist = [] #  type 5: glyph, group
        self.grgrlist = [] #  type 6: group, group/glyph
        self.pairTypeList = [self.gglist, self.ggelist,
        self.ggrElist, self.grgElist, self.ggrlist, self.grgrlist ]
        self.pairNameTypeList = ['glyph, glyph', 'glyph, glyph exception',
        'glyph, group exception', 'group, glyph exception',
        'glyph, group', 'group, group/glyph' ]

        for pairkern in sorted(self.fDic.kerning):
            value = self.fDic.kerning[pairkern]
            if value == 0:
                continue
            leftG, rightG = pairkern
            if set(pairkern) & set(self.fDic.groups):
                #  there is a group in the pair
                if set(pairkern) & self.fDic.glyphs:
                    #  there is also a glyph in the pair (type 3 to 6)
                    if leftG in self.fDic.groups:
                        #  group - glyph
                        self._classes.add(leftG)
                        if rightG in self.fDic.rightGrouped:
                            self.grgElist.append((pairkern, value))  #  type 4: group, glyph exceptions (enum)
                        else:
                            self.grgrlist.append((pairkern, value)) #  type 6: group, group/glyph
                    elif rightG in self.fDic.groups:
                        self._classes.add(rightG)
                        #   glyph - group
                        if leftG in self.fDic.leftGrouped:
                            self.ggrElist.append((pairkern, value)) #  type 3: glyph, group exceptions (enum)
                        else:
                            self.ggrlist.append((pairkern, value)) #  type 5: glyph, group
                elif len(set(pairkern) - set(self.fDic.groups)) == 0:
                    self._classes.update(pairkern)
                    self.grgrlist.append((pairkern, value)) #  type 6: group, group/glyph
                else:
                    self.warnings.append(wrap('#  WARNING: There is a missing group/glyph in the \"%s\" pair, skipping the pair.\n'
                    %' , '.join(pairkern)))
            elif len(set(pairkern) - set(self.fDic.glyphs)) == 0:
                #  there is no group in the pair
                if leftG in self.fDic.leftGrouped or rightG in self.fDic.rightGrouped:
                    self.ggelist.append((pairkern, value)) #  type 2: glyph, glyph exceptions
                else:
                    self.gglist.append((pairkern, value)) #  type 1: glyph, glyph
            else:
                self.warnings.append(wrap('#  WARNING: There is a missing group/glyph in the \"%s\" pair, skipping the pair.\n'
                %' , '.join(pairkern)))

        for cls in self._classes:
            className = cls.translate(self.deleteExtraCharactersInClassMap) #  translate deletes extra @ char
            rawContent = set(self.fDic.groups.get(cls))
            classContents = set()
            if rawContent:
                classContents = rawContent & self.fDic.glyphs
                missingContent = rawContent - self.fDic.glyphs
            if classContents:
                otCls = otClass(className, classContents)
                self.classRules.add(otCls.syntax())
            else:
                self.warnings.append(wrap('#  WARNING: The class "%s" is empty. skipping.\n' %cls))
                self.emptyClasses.add(cls)
                continue
            if missingContent:
                self.warnings.append(wrap('#  WARNING: The glyphs "%s" from the class "%s" is a missing from the font. skipping missing glyphs.\n'
                %(' , '.join(missingContent), cls) ))

        for i, pairType in enumerate(self.pairTypeList):
            rtlG = self.fDic.rtl | self.fDic.rtlGroups
            enum = False
            pairNameType = '#  %s' %self.pairNameTypeList[i]
            for pairkern in pairType:
                pair, value = pairkern
                if set(pair) & self.emptyClasses:
                    continue
                if set(pair) & rtlG:
                    #  pair contains a right to left glyph
                    flag = 'nomark rtl'
                    rtlState = True
                else:
                    flag = 'noflag'
                    rtlState = False
                if 1 < i < 4: #  type 3 and 4 with index of 2 and 3
                    enum = True

                kernRule = self.defKern(pair, value, enum, rtlState)
                spaces = ' '*(75 - len(kernRule))
                finalRule = '%s%s%s' %(kernRule, spaces, pairNameType)
                try:
                    self.kernRules[flag].append(finalRule)
                except KeyError:
                    self.kernRules[flag] = [finalRule]

    def defKern(self, pair, value, enum=False, rtl=False):
        value = str(value)
        finalPair = list(pair)
        for i, g in enumerate(pair):
            if g in self.fDic.groups and g[0] != '@':
                g = g.translate(self.deleteExtraCharactersInClassMap)
                finalPair[i] = '@%s' %(g)
        leftG, rightG = finalPair
        enumStr = ''
        if rtl is True:
            value = '<%s 0 %s 0>' %(value, value)
        if enum is True:
            enumStr = 'enum '
        return '%spos %s %s %s;' %(enumStr, leftG, rightG, value)

    def syntax(self):
        result = []
        kernFea = feature(self.tag)
        if self.kernRules:
            result.append(self.featureStart())
        if self.warnings:
            kernFea.content('\n'.join(self.warnings))
        if self.classRules:
            kernFea.content('\n\n'.join(self.classRules)+'\n\n')
        if self.kernRules:
            kernFea.addLookup(self.kernRules)
            result.append(kernFea.syntax()+'\n')
        return '\n'.join(result)
