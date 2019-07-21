from featureMan.otSingleSubFeatures import *
from featureMan.otNumberFeatures import *
from featureMan.otLanguages import *
from featureMan.otLocalized import *
from featureMan.otLigatureFeatures import *
from featureMan.otMark import mark
from featureMan.otSyntax import fontDic, GDEF
from featureMan.otKern import kern
from featureMan.otCursive import cursive

def l2str(l):
    return '\n'.join(l)

def generateFeatures(f, marksToSkip=None, include=None, base="", path=""):
    from time import time
    start = time()
    if marksToSkip == None:
        marksToSkip = set("a c d e i k l n o r s t u y z A C D E G I J K L N O R S T U Y Z dotlessi acute breve caron cedilla circumflex dieresis dotaccent grave hungarumlaut macron ogonek ring tilde acute.case breve.case caron.case circumflex.case dieresis.case dotaccent.case grave.case hungarumlaut.case macron.case ring.case tilde.case caronslovak commaturnedtop commaaccent".split(" "))

    fDic = fontDic(f, marksToSkip)
    aaltSet = set()
    interpretTime = time()
    print("Elapsed time for interpreting the ufo data: %s" %(interpretTime - start))
    marksSet = set()
    basesSet = set()
    ligaturesSet = set()
    componentsSet = set()
    classes = {}

    allFeatures = [
        ccmpFeature, smcpFeature, caseFeature, arabicFeatures,

        lnumFeature, onumFeature, pnumFeature, tnumFeature,

        zeroFeature, localized,

        ss01Feature, ss02Feature, ss03Feature, ss04Feature, ss05Feature, ss06Feature, ss07Feature,
        ss08Feature, ss09Feature, ss10Feature, ss11Feature, ss12Feature, ss13Feature, ss14Feature,
        ss15Feature, ss16Feature, ss17Feature, ss18Feature, ss19Feature, ss20Feature,

        rligFeature, ligaFeature, dligFeature,

        cursive, kern, mark
        ]

    middleSyntax = []
    for feaClass in allFeatures:
        fea = feaClass(fDic, classes)
        feaSyntax = fea.syntax()
        if feaSyntax:
            middleSyntax.append((fea.tag, feaSyntax))
            classes.update(fea.classes)
            aaltSet.update(fea.aalt)
            marksSet.update(fea.mark)
            basesSet.update(fea.base)
            componentsSet.update(fea.component)
            ligaturesSet.update(fea.ligature)
    gdef = GDEF(basesSet, ligaturesSet, marksSet, componentsSet, fDic.glyphs)
    finalAalt = aaltFeature(aaltSet)
    langs = languages(fDic)
    allFeaturesSyntax = []
    allFeaturesSyntax.append(('logs' , l2str(fDic.log)))
    allFeaturesSyntax.append(('lang' , langs.syntax()))
    allFeaturesSyntax.append(('aalt' , finalAalt.syntax()))
    allFeaturesSyntax.extend(middleSyntax)
    allFeaturesSyntax.append(('gdef', gdef.syntax()))

    finaFea = base
    if include is not None:
        if type(include) is str:
            include = set(include.split(","))
        elif type(include) is list:
            include = set(include)
        finaFea += l2str([f[1] for f in allFeaturesSyntax if f[0] in include])
    else:
        finaFea += l2str([f[1] for f in allFeaturesSyntax])

    featTime = time()
    print("Elapsed time for generating the features: %s" %(featTime - interpretTime))

    fontName = ''
    fontPath = ''

    if f.path:
        fontName = f.path.split("/")[-1].split('.')[0]
        fontPath = '/'.join(f.path.split("/")[:-1])

    if path:
        fontPath = path

    feaPath = '%s_features.fea' %(fontPath+'/'+fontName)
    relativePath = '%s_features.fea' %fontName
    with open(feaPath, 'w') as File:
        File.write(finaFea)

    f.features.text = 'include(%s);' %relativePath
    f.features.changed()

    print("Elapsed time for saving the features: %s" %(time() - featTime))
    print("Elapsed time for the whole process: %s" %(time() - start))

if __name__ == '__main__':
    import argparse
    from fontParts.fontshell.font import RFont
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--ufo", help="Path to the ufo file.", type=str)
    parser.add_argument("-b", "--base", help="Base features to include in the begining. It can be used to add some manual features at top of the feature file.", type=str, default="")
    parser.add_argument("-o", "--only", help="Only unclude the comma seperated feature tags written here. For example: mark,gdef", type=str)
    parser.add_argument("-p", "--path", help="Path to save the feature file at, default path is next to the UFO.", type=str)
    args = parser.parse_args()
    if args.ufo is not None:
        f = RFont(args.ufo)
        generateFeatures(f, marksToSkip=None, base=args.base, include=args.only, path=args.path)
    else:
        print('You need a UFO for the familyFeatures module to work. Use the following command for help:\npython3 "/path/to/repo/Lib/featureMan/familyFeatures.py" -h')
