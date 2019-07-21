from featureMan.otSyntax import *


class cursive(abstractFeature):
    """ An object to create cursive attathcment. """
    entryAnchroName = "entry"
    exitAnchorName = "exit"
    prefixTag = "*"
    defaulFlags = 'nomark rtl'
    tag = 'curs'

    def __init__(self, fDic, classes):
        super(cursive, self).__init__(fDic, classes)
        self.anchorDic = fDic.anchors
        self.glyphAnchorDic = fDic.glyphAnchor
        self.rules = []
        self._classes = []
        self.baseGlyphs = {} # glyph : [entryAnchor, exitAnchor]
        self.attatchedGlyphs = {}
        for anchor, glyphs in self.anchorDic.items():
            if self.isCursiveAnchor(anchor):
                for glyph in glyphs:
                    entryAnchor = None
                    exitAnchor = None
                    for glyphAnchor, position in self.glyphAnchorDic[glyph].items():
                        if self.isCursiveAnchor(glyphAnchor):
                            if glyphAnchor[1:] == self.entryAnchroName:
                                entryAnchor = position
                            if glyphAnchor[1:] == self.exitAnchorName:
                                exitAnchor = position
                    self.attatchedGlyphs[glyph] = (entryAnchor, exitAnchor)

        for glyph, cursiveAnchors in self.attatchedGlyphs.items():
            entryAnchor, exitAnchor = cursiveAnchors
            rule = self.defineCursive(glyph, entryAnchor, exitAnchor)
            self.rules.append(rule)

    def isCursiveAnchor(self, anchor):
        if anchor[0] != self.prefixTag:
            return False
        if anchor[1:] in [self.entryAnchroName, self.exitAnchorName]:
            return True
        return False

    def strPose(self, positions):
        if positions is None:
            return 'NULL '
        result = []
        for pose in positions:
            if pose is not None:
                result.append(str(int(pose)))
        return ' '.join(result)

    def defineCursive(self, glyph, entryAnchor, exitAnchor):

        return 'position cursive %s <anchor %s> <anchor %s>;' %(glyph, self.strPose(entryAnchor), self.strPose(exitAnchor))

    def syntax(self):
        result = []
        cursiveFeature = feature(self.tag)
        if self.rules != []:
            result.append(self.featureStart())
            cursiveFeature.addLookup({self.defaulFlags: self.rules})
            result.append(cursiveFeature.syntax())
            return '\n'.join(result)
