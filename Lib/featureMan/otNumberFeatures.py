from featureMan.otSyntax import *
from featureMan.lib import determineDefaultNumbers

class numberAbstractFeature(abstractFeature):

    def __init__(self, fDic, classes):
        super(numberAbstractFeature, self).__init__(fDic, classes)

        self.numberList = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        self.onum_pnumSuffix = "onum_pnum"
        self.lnum_pnumSuffix = "lnum_pnum"
        self.onum_tnumSuffix = "onum_tnum"
        self.lnum_tnumSuffix = "lnum_tnum"
        self.exchange_name = {self.lnum_pnumSuffix: "lnum_pnum", self.lnum_tnumSuffix: "lnum_tnum", self.onum_tnumSuffix: "onum_tnum", self.onum_pnumSuffix: "onum_pnum"}
        self.def_num = []
        self.onum_pnum = []
        self.lnum_pnum = []
        self.onum_tnum = []
        self.lnum_tnum = []
        self.groupNameDictionary = {1: self.onum_pnumSuffix, 2: self.lnum_pnumSuffix, 3: self.onum_tnumSuffix, 4: self.lnum_tnumSuffix}
        self.groupDictionary = {1: self.onum_pnum, 2: self.lnum_pnum, 3: self.onum_tnum, 4: self.lnum_tnum}
        self.rules = []

        defNumRef = ""
        for g in self.fDic.glyphSort:
            # if self.checkSuffix(g) in self.numberList:
            gname = g.rpartition('.')
            if gname[0]: # if glyph name has suffix
                if self.onum_pnumSuffix in gname[-1] and gname[0] in self.numberList:
                    self.onum_pnum.append(g)
                    # self.onum_pnumGlyphList.append(g)
                    if defNumRef != "lnum_pnum" and defNumRef != "lnum_tnum" and defNumRef != "onum_tnum":
                        if gname[0] in self.fDic.glyphSort:
                            self.def_num.append(gname[0])
                        defNumRef = "onum_pnum"
                elif self.lnum_pnumSuffix in gname[-1] and gname[0] in self.numberList:
                    self.lnum_pnum.append(g)
                    # self.lnum_pnumGlyphList.append(g)
                    if defNumRef != "lnum_tnum" and defNumRef != "onum_pnum" and defNumRef != "onum_tnum":
                        if gname[0] in self.fDic.glyphSort:
                            self.def_num.append(gname[0])
                        defNumRef = "lnum_pnum"
                elif self.onum_tnumSuffix in gname[-1] and gname[0] in self.numberList:
                    self.onum_tnum.append(g)
                    # self.onum_tnumGlyphList.append(g)
                    if defNumRef != "lnum_pnum" and defNumRef != "onum_pnum" and defNumRef != "lnum_tnum":
                        if gname[0] in self.fDic.glyphSort:
                            self.def_num.append(gname[0])
                        defNumRef = "onum_tnum"
                elif self.lnum_tnumSuffix in gname[-1] and gname[0] in self.numberList:
                    self.lnum_tnum.append(g)
                    # self.lnum_tnumGlyphList.append(g)
                    if defNumRef != "lnum_pnum" and defNumRef != "onum_pnum" and defNumRef != "onum_tnum":
                        if gname[0] in self.fDic.glyphSort:
                            self.def_num.append(gname[0])
                        defNumRef = "lnum_tnum"
        self.groupDictionary[1] = self.onum_pnum
        self.groupDictionary[2] = self.lnum_pnum
        self.groupDictionary[3] = self.onum_tnum
        self.groupDictionary[4] = self.lnum_tnum
        index = 0
        for l in self.groupNameDictionary:
            index += 1
            if self.exchange_name[self.groupNameDictionary[l]] == determineDefaultNumbers.get(self.fDic.f):
                self.groupDictionary[index] = self.def_num
        self.createRulesByGroupID()

    def addRuleBySuffix(self, suffix):
        result = []
        if suffix in self.fDic.basic_subs:
            srcGlyphs, desGlyphs = self.fDic.basic_subs[suffix]
            if srcGlyphs:
                for srcG, desG in zip(srcGlyphs, desGlyphs):
                    if srcG not in self.numberList:
                        rule = 'sub %s by %s;' %(srcG, desG)
                        result.append(rule)
        return '\n'.join(result)

    def createRulesByGroupID(self, g1, g2, g3, g4, g5, g6):
        extraNumbers = self.addRuleBySuffix(g5) + self.addRuleBySuffix(g6)
        if extraNumbers:
            self.rules.append(extraNumbers)
        if self.groupDictionary[g1] and self.groupDictionary[g2]:
            groupSrc = self.groupNameDictionary[g1]
            groupDes = self.groupNameDictionary[g2]
            self.rules.append( 'sub @%s by @%s;' %(groupSrc, groupDes))
        if self.groupDictionary[g3] and self.groupDictionary[g4]:
            groupSrc = self.groupNameDictionary[g3]
            groupDes = self.groupNameDictionary[g4]
            self.rules.append('sub @%s by @%s;' %(groupSrc, groupDes))

    def syntax(self):
        result = []
        if self.rules != []:
            result.append(self.featureStart())
            self.aalt.add(self.tag)
            for group in self.groupDictionary:
                className, classContents = self.checkClass(self.groupNameDictionary[group], self.groupDictionary[group])
                if classContents:
                    classObj = otClass(className, classContents)
                    rule = classObj.syntax()
                    result.append(rule+"\n")
                    self.classes[className] = classContents

            numFeature = feature(self.tag)
            numFeature.addLookup({'noflag': self.rules})
            result.append(numFeature.syntax())
        return '\n'.join(result)

class pnumFeature(numberAbstractFeature):
    tag = "pnum"

    def createRulesByGroupID(self):
        super(pnumFeature, self).createRulesByGroupID(3, 1, 4, 2, 'pon', 'pln')

class tnumFeature(numberAbstractFeature):
    tag = "tnum"

    def createRulesByGroupID(self):
        super(tnumFeature, self).createRulesByGroupID(1, 3, 2, 4, 'ton', 'tln')

class onumFeature(numberAbstractFeature):
    tag = "onum"

    def createRulesByGroupID(self):
        super(onumFeature, self).createRulesByGroupID(4, 3, 2, 1, 'ton', 'pon')

class lnumFeature(numberAbstractFeature):
    tag = "lnum"

    def createRulesByGroupID(self):
        super(lnumFeature, self).createRulesByGroupID(3, 4, 1, 2, 'tln', 'pln')
        if ((self.groupDictionary[1] and self.groupDictionary[2]) or (self.groupDictionary[3] and self.groupDictionary[4])): # case sensitive glyphs beside lining figures
            self.rules.append(self.addRuleBySuffix('case'))


if __name__ == "__main__":
    glyphSort = []
    unicodeDic = {}

    f = CurrentFont()
    fDic = fontDic(f)
    classes = {}

    lnum = lnumFeature(fDic, classes)
    print(lnum.syntax())
    classes.update(lnum.classes)

    onum = onumFeature(fDic, classes)
    print(onum.syntax())
    classes.update(onum.classes)

    pnum = pnumFeature(fDic, classes)
    print(pnum.syntax())
    classes.update(pnum.classes)

    tnum = tnumFeature(fDic, classes)
    print(tnum.syntax())
