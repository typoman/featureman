from featureMan.otSyntax import *


class ligatureAbstractFeature(abstractFeature):
    tag = ''

    def __init__(self, fDic, classes):
        super(ligatureAbstractFeature, self).__init__(fDic, classes)
        # self.rules = {}
        self.rules = []
        self.createRules()

    def createRules(self):
        alreadyAssigned = []
        if self.tag in self.fDic.composites:
            subs = sorted(self.fDic.composites[self.tag], key=lambda x: x[0], reverse=True) # sorting based on number of components
            for sub in subs:
                numComps, comps, liga = sub
                # flag = self.getFlags(comps+liga)
                # flag = 'noflag'
                rule = 'sub %s by %s;' %(' '.join(comps), ' '.join(liga))
                if comps in alreadyAssigned:
                    self.log.append("# this sub '%s' was skipped because it's already defined" %rule)
                    continue
                if self.tag != 'ccmp':
                    self.component.update(comps)
                    self.ligature.update(liga)
                self.rules.append(rule)
                alreadyAssigned.append(comps)

    def syntax(self):
        result = []
        if self.rules != []:
            ligaFeature = feature(self.tag)
            result.append(self.featureStart())
            ligaFeature.content('\n'.join(self.rules))
            # ligaFeature.addLookup(self.rules)
            result.append(ligaFeature.syntax())
        return '\n'.join(result)

class dligFeature(ligatureAbstractFeature):
    tag = 'dlig'

class ligaFeature(ligatureAbstractFeature):
    tag = 'liga'

class rligFeature(ligatureAbstractFeature):
    tag = 'rlig'

class ccmpFeature(ligatureAbstractFeature):
    tag = 'ccmp'
