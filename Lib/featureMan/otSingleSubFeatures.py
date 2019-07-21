from featureMan.otSyntax import *


class singleSub(abstractFeature):
    tag = ''

    def __init__(self, fDic, classes):
        super(singleSub, self).__init__(fDic, classes)
        self.rules = {}
        self.srcClass = None
        self.desClass = None
        self.errors = []
        self.createRules()

    def createRules(self):
        if self.tag in self.fDic.basic_subs:
            srcGlyphs, desGlyphs = self.alterSrcDes(*self.fDic.basic_subs[self.tag])
            if srcGlyphs:
                for srcG, desG in zip(srcGlyphs, desGlyphs):
                    rule = 'sub %s by %s;' %(srcG, desG)
                    flag = 'noflag'
                    if srcG in self.fDic.rtl:
                        flag = 'rtl'
                    if flag in self.rules:
                        self.rules[flag].append(rule)
                    else:
                        self.rules[flag] = [rule]

    def alterSrcDes(self, src, des):
        """
        changes the source in and des in case of features like scmp
        this is overrided in subclass.
        for example in smcp it return the capital letter for the src.
        """
        return src, des

    def syntax(self):
        result = []
        singleSubFeature = feature(self.tag)
        if self.rules != {}:
            result.append(self.featureStart())
            self.aalt.add(self.tag)
            singleSubFeature.addLookup(self.rules, '')
            result.append(singleSubFeature.syntax())
        return '\n'.join(result)


class smcpFeature(singleSub):
    tag = 'smcp'

    def alterSrcDes(self, src, des):
        resultSrc = []
        resultDes = []
        for srcG, desG in zip(src, des):
            srcG = srcG.lower()
            if srcG in self.fDic.glyphs:
                resultSrc.append(srcG)
                resultDes.append(desG)

        return resultSrc, resultDes

class caseFeature(singleSub):
    tag = 'case'

class zeroFeature(singleSub):
    tag = 'zero'

class ss01Feature(singleSub):
    tag = 'ss01'
class ss02Feature(singleSub):
    tag = 'ss02'
class ss03Feature(singleSub):
    tag = 'ss03'
class ss04Feature(singleSub):
    tag = 'ss04'
class ss05Feature(singleSub):
    tag = 'ss05'
class ss06Feature(singleSub):
    tag = 'ss06'
class ss07Feature(singleSub):
    tag = 'ss07'
class ss08Feature(singleSub):
    tag = 'ss08'
class ss09Feature(singleSub):
    tag = 'ss09'
class ss10Feature(singleSub):
    tag = 'ss10'
class ss11Feature(singleSub):
    tag = 'ss11'
class ss12Feature(singleSub):
    tag = 'ss12'
class ss13Feature(singleSub):
    tag = 'ss13'
class ss14Feature(singleSub):
    tag = 'ss14'
class ss15Feature(singleSub):
    tag = 'ss15'
class ss16Feature(singleSub):
    tag = 'ss16'
class ss17Feature(singleSub):
    tag = 'ss17'
class ss18Feature(singleSub):
    tag = 'ss18'
class ss19Feature(singleSub):
    tag = 'ss19'
class ss20Feature(singleSub):
    tag = 'ss20'

# if glyph has init but not medi define the init inside medi too

class arabicFeatures(abstractFeature):
    """init medi fina isol"""
    tags = ['init', 'medi', 'fina', 'isol']

    def __init__(self, fDic, classes):
        super(arabicFeatures, self).__init__(fDic, classes)
        self.tag2srcGlyphs = {}
        self.tag2desGlyphs = {}
        self.tag2rules = {}
        self.aalt = set()
        self.createRules()

    def createRules(self):
        for tag in self.tags:
            self.tag2rules[tag] = {'rtl': []}
            if tag in self.fDic.basic_subs:
                srcGlyphs, desGlyphs = self.fDic.basic_subs[tag]
                for srcG, desG in zip(srcGlyphs, desGlyphs):
                    rule = 'sub %s by %s;' %(srcG, desG)
                    try:
                        self.tag2srcGlyphs[tag].append(srcG)
                        self.tag2desGlyphs[tag].append(desG)
                    except KeyError:
                        self.tag2srcGlyphs[tag] = [srcG]
                        self.tag2desGlyphs[tag] = [desG]

                    self.tag2rules[tag]['rtl'].append(rule)

        if 'init' in self.tag2srcGlyphs:
            for srcG, desG in zip(self.tag2srcGlyphs['init'], self.tag2desGlyphs['init']):
                if srcG not in self.tag2srcGlyphs['medi']:
                    rule = 'sub %s by %s;' %(srcG, desG)
                    self.tag2rules['medi']['rtl'].append(rule)

    def syntax(self):
        result = []
        for tag in self.tag2rules:
            arabicFeature = feature(tag)
            try:
                rules = self.tag2rules[tag]
            except KeyError:
                continue
            arabicFeature.addLookup(rules)
            syntax = arabicFeature.syntax()
            if syntax:
                self.aalt.add(tag)
                result.append(self.featureStart(tag))
                result.append(syntax+"\n")
        return '\n'.join(result)
