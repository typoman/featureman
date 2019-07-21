class languages():

    def __init__(self, fDic):
        self.fDic = fDic
        self.scripts = set(self.fDic.scripts)
        self.scripts.discard('dflt')

    def languageSyntax(self, script, language):
        return 'languagesystem %s %s;' %(script, language)

    def syntax(self):
        result = [self.languageSyntax('DFLT', 'dflt')]
        for script in self.scripts:
            result.append(self.languageSyntax(script, 'dflt'))
        for script, language in self.fDic.localized.keys():
            result.append(self.languageSyntax(script, language))
        return '\n'.join(result)
