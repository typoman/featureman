from featureMan.otSyntax import *
"""

to do:

. Don't generate mark pos for base letters is the mark pos is only used for
creating a composite.  This means if glyphs whihc are associated with the
mark class don't have unicode, they should not be generated in the final
feauter. because they're extra data.

. find out whihc glyphs don't need mark pos. Like most of the accented letters in Latin?

. Contexual mark positioning

"""
class mark(abstractFeature):
    """ An object to create mark Feature. """
    tag = 'mark'
    classPrefix = "mark_class"

    def __init__(self, fDic, classes):
        super(mark, self).__init__(fDic, classes)
        self.mark = fDic.marks | fDic.mkmk
        self.base = fDic.bases
        self.anchorDic = fDic.anchors
        self.glyphAnchorDic = fDic.glyphAnchor

        self.markClassNameList = []
        self.markClasses = []
        self.errors = []

        self.re_anchor_base = re.compile(r'_?[A-Za-z]+')
        self.glyphsClassesDefined = {}
        # create classes
        for a in self.anchorDic:
            if a[0] == "_":
                thisClassType = a[1:]
                if thisClassType in self.anchorDic:
                    self.markClasses.append(indent("# anchor class %s" %thisClassType))
                    for g in self.anchorDic[a]:
                        if g in self.glyphsClassesDefined:
                            self.markClasses.append(indent("# Warning: The glyph %s has already been defined in the mark class '%s'" %(g, self.glyphsClassesDefined[g])))
                            continue
                        for anchor in self.glyphAnchorDic[g]:
                            if anchor[1:] != thisClassType:
                                continue
                            if anchor[0] == "_" and anchor[1:] in self.anchorDic:
                                self.markClasses.append("markClass %s <anchor\t%i\t%i> @%s;" %(g,
                                self.glyphAnchorDic[g][anchor][0], self.glyphAnchorDic[g][anchor][1], self.classPrefix+anchor))
                                self.glyphsClassesDefined[g] = anchor[1:]
                                if anchor[1:] not in self.markClassNameList:
                                    self.markClassNameList.append(anchor[1:])
                else:
                    self.errors.append(indent("# Warning: anchor '%s' in glyph(s) '%s' does not exist in another base glyph" %(a, ' '.join(self.anchorDic[a])) ))

        # create mark positioning lists
        # first we need to seperate mark, base and ligatures in different lists
        self.markList = []
        self.ligatureList = []
        self.markToMarkList = []
        for g in self.glyphAnchorDic:
            for a in self.glyphAnchorDic[g]:
                if a[0] == '_':
                    # print(a, g)
                    # this glyph is a mark but let's see if it needs markToMark definition or not
                    for a2 in self.glyphAnchorDic[g]:
                        if a2[0] != '_':
                            # now we know this glyph needs a markToMark definition
                            self.markToMarkList.append(g)
                            break
                    break
                elif '_' in a:
                    # this glyph needs a ligature mark definition because there is no other type of anchor in a ligature
                    self.ligatureList.append(g)
                    break
                else:
                    # this glyph is either a mark or simple glyph (not ligature)
                    # but we need to be sure if there is any '_' name anchor inside glyph
                    for a2 in self.glyphAnchorDic[g]:
                        if a2[0] == '_':
                            # this glyph is a mark get out of this loop
                            self.markToMarkList.append(g)
                            break
                    else:
                        # if the loop didn't break, this glyph is a simple glyph
                        self.markList.append(g)
                    break
        # now we create the OT syntax lines, these lines might have to be wrapped inside lookups
        self.markRules = {}
        self.markToMarkRules = {} # we need a dictionary to seperate different anchors types. e.g: top, bottom
        self.markLigatureRules = {}
        for g in sorted(self.markList):
            posBase = "position base %s" %g
            resultMark = []
            for a in self.glyphAnchorDic[g]:
                if a in self.markClassNameList:
                    self.base.add(g)
                    resultMark.append(self.defineMark(a, self.glyphAnchorDic[g][a][0], self.glyphAnchorDic[g][a][1] ))
            if resultMark != []:
                resultMark.insert(0, posBase)
                resultMark[-1]+=(';')
                try:
                    if g in self.fDic.rtl or self.fDic.glyphScript[g] in rtlScripts:
                        flag = 'rtl'
                    else:
                        flag = 'noflag'
                except KeyError:
                    self.errors.append("#	Warning: The glyph %s doesn't belong to any script and no mark lookup will be generated for it." %g)
                    continue
                if flag in self.markRules:
                    self.markRules[flag].append('\n'.join(resultMark))
                else:
                    self.markRules[flag] = ['\n'.join(resultMark)]
        for g in sorted(self.ligatureList):
            compAnchors = {}
            nextGlyph = False
            for a in sorted(list(self.glyphAnchorDic[g])):
                anchorBaseName = self.re_anchor_base.findall(a)[0]
                if anchorBaseName in self.markClassNameList:
                    if anchorBaseName in compAnchors:
                        compAnchors[anchorBaseName].append((self.glyphAnchorDic[g][a][0], self.glyphAnchorDic[g][a][1]))
                    else:
                        compAnchors[anchorBaseName] = [(self.glyphAnchorDic[g][a][0], self.glyphAnchorDic[g][a][1])]
                else:
                    nextGlyph = True
            if nextGlyph:
                continue
            result = ["position ligature %s" %g]
            self.ligature.add(g)
            ligCompNumber = len(compAnchors[list(compAnchors)[0]])
            if ligCompNumber > 1:
                for i in range(ligCompNumber):
                    for a in compAnchors:
                        try:
                            result.append(self.defineMark( a, compAnchors[a][i][0], compAnchors[a][i][1] ))
                        except IndexError:
                            self.errors.append( "#\tWarning: while defining mark on ligatures: can't find equivalent number of anchors per component in the glyph '%s'" %g )
                    if i+1 != ligCompNumber:
                        result.append(indent("ligComponent", 2 ))
            else:
                compNumbers = len(compAnchors.values()[0])
                for a in compAnchors:
                    for i, p in enumerate(compAnchors[a]):
                        result.append(self.defineMark( a, p[0], p[1] ))
                        if compNumbers - i-1:
                            result.append(indent("ligComponent", 2 ))
            result[-1]+=(';')
            try:
                if g in self.fDic.rtl or self.fDic.glyphScript[g] in rtlScripts:
                    flag = 'rtl'
                else:
                    flag = 'noflag'
            except KeyError:
                self.errors.append("#	Warning: The glyph %s doesn't belong to any script and no mark lookup will be generated for it." %g)
            if flag in self.markLigatureRules:
                self.markLigatureRules[flag].append('\n'.join(result))
            else:
                self.markLigatureRules[flag] = ['\n'.join(result)]

        for a in self.anchorDic:
            # looping based on anchor names so anchors with different names can be seperated
            if '_' not in a and a in self.markClassNameList:
                for g in sorted(self.markToMarkList):
                    for a2 in self.glyphAnchorDic[g]:
                        if a == a2:
                            self.mark.add(g)
                            resultMark = "position mark %s\n%s;" %( g, self.defineMark( a,
                            self.glyphAnchorDic[g][a][0], self.glyphAnchorDic[g][a][1] ))
                            try:
                                if g in self.fDic.rtl or self.fDic.glyphScript[g] in rtlScripts:
                                    flag = 'mark @%s%s' %(self.classPrefix+'_', a)
                                else:
                                    flag = 'rtl mark @%s%s' %(self.classPrefix+'_', a)
                            except KeyError:
                                self.errors.append("#	Warning: The glyph %s doesn't belong to any script and no mark lookup will be generated for it." %g)
                                continue

                            if flag in self.markToMarkRules:
                                self.markToMarkRules[flag].append(resultMark)
                            else:
                                self.markToMarkRules[flag] = [resultMark]

    def defineMark(self, anchor, x, y):
        """
            OT syntax for regular anchor poistion without the glyph name
        """

        return indent("<anchor\t%i\t%i> mark @%s" %( x, y, self.classPrefix+'_'+anchor))

    def syntax(self):
        result = []
        markFeature = feature('mark')
        if self.markRules != {}:
            result.append(self.featureStart('mark'))
        if self.errors:
            result.append('\n'.join(self.errors))
        if self.markClasses:
            result.append('\n'.join(self.markClasses))
        if self.markRules != {}:
            markFeature.addLookup(self.markRules, 'base')
        if self.markLigatureRules != {}:
            markFeature.addLookup(self.markLigatureRules, 'ligature')
        if self.markLigatureRules != {} or self.markRules != {}:
            result.append(markFeature.syntax())
        mmkFeature = feature('mkmk')
        if self.markToMarkRules != {}:
            result.append(self.featureStart('mkmk'))
            mmkFeature.addLookup(self.markToMarkRules)
            result.append(mmkFeature.syntax())
        if result:
            result.append('\n\n')
        return '\n'.join(result)
