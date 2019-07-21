from featureMan.otSyntax import *


class localized(abstractFeature):
    tag = 'locl'

    def __init__(self, fDic, classes):
        super(localized, self).__init__(fDic, classes)
        self.rules = {}
        self.srcClass = None
        self.desClass = None
        self.errors = []
        self.lookups = []
        self.rules = []
        self.createRules()

    def createRules(self):
        last_script = None
        flag = 'noflag'

        for scriptlanguage, gPairList in sorted(self.fDic.localized.items()):

            script, language = scriptlanguage
            if script != last_script:
                self.rules.append('script %s;' %script)
                last_script = script
            if script in rtlScripts:
                flag = 'rtl'
            else:
                flag = 'noflag'
            self.rules.append(indent('language %s exclude_dflt;' %language))
            thisLookup = lookup('local.%s.%s.%s' %(script, language, flag))
            thisLookup.flag(flag)
            lookupRules = []
            for srcG, desG in gPairList:
                lookupRules.append('sub %s by %s;' %(srcG, desG))
            thisLookup.content('\n'.join(lookupRules))
            self.lookups.append(thisLookup)
            self.rules.append(indent(thisLookup.call(), 2))

    def syntax(self):
        result = []
        if self.lookups != []:
            result.append(self.featureStart())
        for l in self.lookups:
            result.append(l.syntax())
        locFeature = feature(self.tag)
        if self.rules != []:
            self.aalt.add(self.tag)
            locFeature.content('\n'.join(self.rules))
            result.append(locFeature.syntax())
        return '\n'.join(result)
