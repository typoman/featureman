from builtins import chr
import re
from unicodedata import bidirectional
from featureMan.lib import tags, scripts

"""
- finds unciode of the glyph
- finds the direction of the glyph
- finds script of the glyph
"""

glyphBase = re.compile(r'[^._]+')

directionDic = {
                'L':    False,
                'LRE':  False,
                'LRO':  False,
                'R':    True,
                'AL':   True,
                'RLE':  True,
                'RLO':  True,
                'PDF':  False,
                'EN':   False,
                'ES':   False,
                'ET':   False,
                'AN':   False,
                'CS':   False,
                'NSM':  False,
                'BN':   False,
                'B':    False,
                'S':    False,
                'WS':   False,
                'ON':   False
                }

class glyphProperty():
    """
        This object tries to retrieve the writing system
        the glyph name 'g' is used in. First it tries to
        retrive the unicode from glyph name or components
        then it uses it to find the glyph script tag in
        openType feature specification.
    """

    def __init__(self, g, fDic):
        self.g = g
        self.gBase = glyphBase.findall(g)[0]
        self.fDic = fDic
        self.uniLiga = re.compile(r'(?:uni)?([0-9A-Fa-f]+)')
        self.uniSplit = re.compile(r'(?:uni)?([0-9A-Fa-f]{4})')
        self.gUniSet = set()
        self.scriptTag = ''
        if self.g in self.fDic.glyphUnicode:
            self.gUniSet = self.fDic.glyphUnicode.get(self.g)

    def addUniSet2Glyph(self, name, uniSet):
        if uniSet:
            gBase = glyphBase.findall(name)[0]
            if gBase not in self.fDic.glyphPseudoUnicode:
                self.fDic.glyphPseudoUnicode[self.gBase] = uniSet
            if name not in self.fDic.glyphUnicode:
                self.fDic.glyphUnicode[name] = uniSet
            if self.g not in self.fDic.glyphUnicode:
                self.fDic.glyphUnicode[self.g] = uniSet
            self.gUniSet.update(uniSet)

    def uniResolve(self):
        """
            Retrieve unicode by parsing the name and
            finding uniXXXX patterns in glyph name.
        """
        if len(self.uniLiga.findall(self.g))%4 and len(self.uniSplit.findall(self.g)) != 0:
            for u in self.uniSplit.findall(self.g):
                self.addUniSet2Glyph(self.g, set([int(u, 16)]))
            return True
        return False

    def componentResolve(self):
        """
            Retrieve unicode by going through component
            dictionary and see if the glyph is used in
            another glyph which has unicode.
        """

        if self.g in self.fDic.glyphComps:
            for g2 in self.fDic.glyphComps[self.g]:
                self.addUniSet2Glyph(g2, self.fDic.glyphUnicode.get(g2))
            if self.gUniSet:
                return True
        return False

    def suffixResolve(self):
        """
            Retrieve unicode by parsing glyph name
            and see if another glyph has a similar name
            without the glyph suffix.
        """

        if len(glyphBase.findall(self.g)) > 1:
            for g2 in glyphBase.findall(self.g):
                self.addUniSet2Glyph(g2, self.fDic.glyphPseudoUnicode.get(g2))
            if self.gUniSet:
                return True
        return False

    def unicodes(self):
        """
            If length of list is more than one, it's
            likely that it's a ligature or a composite
            of two glyphs.
        """

        if self.gUniSet:
            return self.gUniSet
        elif self.suffixResolve():
            return self.gUniSet
        elif self.uniResolve():
            return self.gUniSet
        elif self.componentResolve():
            return self.gUniSet

    def script(self):
        unis = self.unicodes()
        if unis:
            u = list(unis)[0]
            if scripts.getScript(chr(u)) in tags.scriptTags:
                self.scriptTag = tags.scriptTags[scripts.getScript(chr(u))]
            else:
                self.scriptTag = 'dflt'
        return self.scriptTag

    def rtl(self):
        unis = self.unicodes()
        if unis:
            u = list(unis)[0]
            direc = bidirectional(chr(u))
            if direc:
                return directionDic[direc]


if __name__ == "__main__":
    from featureMan.otSyntax import *
    f = CurrentFont()
    u = fontDic(f)
    fText = []
    for g in f.templateSelectedGlyphNames:
        guni = glyphProperty(g, u)
        if guni.script():
            fText.append( "%s\t%s" %(g, guni.script()))
        else:
            fText.append( "\tERRROR: %s" %g )
    print('\n'.join(fText))
