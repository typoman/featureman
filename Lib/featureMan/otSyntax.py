from featureMan.lib.properties import glyphBase, glyphProperty
from featureMan.lib.tags import languageTags
import re
from itertools import permutations

rtlScripts = set(['arab', 'hebr', 'syrc', 'thaa'])

def wrap(string, width=70):
    comment = ''
    if string[0] == '#':
        comment = '# '
    if string:
        newstring = ""
        while len(string) > width:
            marker = width - 1
            while not string[marker].isspace():
                marker = marker - 1
            newline = '%s%s%s' %(string[0:marker], "\n", comment)
            newstring = '%s%s' %(newstring, newline)
            string = string[marker + 1:]
        return '%s%s' %(newstring, string)
    return ''

def indent(text, steps=1):
    lines = text.split('\n')
    space = '    '*steps
    result = []
    for line in lines:
        result.append(space+line)
    return '\n'.join(result)

class otClass():
    """
        An object to create opentype classes.
    """

    def __init__(self, name, glyphList):
        """ class takes the class name and list of glyphs """
        self.name = name
        self.glyphList = glyphList

    def syntax(self):
        """ returns the syntax that deifnes the class """
        if len(self.glyphList) < 1:
            return ''
        result = ['@%s = [' %self.name]
        result.append(indent(wrap(' '.join(self.glyphList))))
        result.append('];')
        return '\n'.join(result)

    def otName(self):
        """ returns the class name in ot syntax"""
        return '@%s' %self.name

class GDEF():
    """
        An object to generate GDEF in Opentype syntax
    """
    # there souldn't be any glyph shared between these classes.
    # otherwise a warning should be produced.

    def __init__(self, base, ligature, mark, component, glyphs=set()):
        """ class takes the glyph lists in the written order """
        self.table = ''
        self.classes = ['', '', '', '']
        self.returnNone = True

        base -= component | ligature | mark
        ligature -= component | mark | base
        component -= mark | base
        base = sorted(set(base) & glyphs)
        ligature = sorted(set(ligature) & glyphs)
        mark = sorted(set(mark) & glyphs)
        component = sorted(set(component) & glyphs)


        if base:
            self.baseClass = otClass('GDEF_base', base)
            self.classes[0] = (self.baseClass)
        if ligature:
            self.ligatureClass = otClass('GDEF_ligature', ligature)
            self.classes[1] = (self.ligatureClass)
        if mark:
            self.markClass = otClass('GDEF_mark', mark)
            self.classes[2] = (self.markClass)
        if component:
            self.componentClass = otClass('GDEF_component', component)
            self.classes[3] = (self.componentClass)

        if mark or ligature or base or component:
            self.returnNone = False
        else:
            return

        self.classesSyntax = []
        self.table = []
        for c in self.classes:
            if type(c) != str:
                self.table.append(c.otName())
                self.classesSyntax.append(c.syntax())
            else:
                self.table.append('')

    def syntax(self):
        if not self.returnNone:
            return '%s\n\ntable GDEF {\n    GlyphClassDef\n%s\n} GDEF;' %('\n\n'.join(self.classesSyntax), indent(',\n'.join(self.table)+';', 2))
        else:
            return ''


flagDic = {
    'rtl': 'RightToLeft',
    'mark': 'MarkAttachmentType',
    'nomark': 'IgnoreMarks',
    'nolig': 'IgnoreLigatures'
    }

class feature:
    """
        An object to create a feature syntax in OpenType.
    """
    def __init__(self, featureName):
        """ class takes the feature name first """
        self.featureName = featureName
        self.contents = ''
        self.lookupSet = set()

    def content(self, contents):
        """ this function adds the input to the feature block """
        self.contents += '%s\n' %indent(contents)

    def addLookup(self, rulesDic, lookupName=''):
        """ lookupName is arbitrary and is given while creating the feature.
        rulesDic has this sctructure:
        rulesDic[flag] = listOfOpenTyperules
        flag is s string in which abreviated names of flags which are defined
        in flagDic are written with a space sepereating them like:
        ['rtl mark']

        listOfOpenTyperules is a list or set of rules which is going to be
        written inside the lookup which in turns goes inside this feature.
        These are basically the rules written in OT syntax. They will be
        joined with a newline character and will be added to the feature
        block.
        """
        if lookupName != '':
            lookupName = '_%s' %lookupName
        result = []
        # (lookupType), (beforeContext, afterContext, )
        for flag in rulesDic:
            if rulesDic[flag]:
                re_name = re.compile(r'[A-Za-z0-9]+') # trying to interpret the flags
                flagName = '_'.join(re_name.findall(flag)) # converting flags to somthing to be used as the lookup name
                i = 1
                thisLookupName = '%s_lookup_%s%s_%i' %(self.featureName, flagName, lookupName, i)
                while thisLookupName in self.lookupSet: # trying to avoid duplicated names for lookups
                    i += 1
                    thisLookupName = '%s_lookup_%s_%s_%i' %(self.featureName,
                    flag, lookupName, i)
                self.lookupSet.add(thisLookupName)
                Lookup = lookup(thisLookupName)
                Lookup.flag(flag)
                Lookup.content('\n'.join(rulesDic[flag]))
                result.append(Lookup.syntax())
        self.contents += ''.join(result)

    def syntax(self):
        """ return the whole feature block sytnax with its definition """
        pat = re.compile(' |\n|\t')
        rawContent = re.sub(pat, '', self.contents)
        if rawContent: # cheking if there is any rules inside the block
            return "feature %s {\n%s} %s;" %(self.featureName, self.contents, self.featureName)
        return ''

class lookup:
    """
        An object to create a lookup syntax in OpenType.
    """
    def __init__(self, lookupName):
        self.lookupName = lookupName
        self.flags = ''
        self.contents = ''
        self.languages = []

    def language(self, languages=None):
        """ language or list of languages that substituion(s) is performed on. """
        if languages:
            self.languages.append(indent(languages))

    def flag(self, inputflags=''):
        """
        input: string of flags from flagdic keys seperated by space:
            e.g:
                'rtl nomark'
        """
        result = []
        if inputflags != 'noflag':
            # self.flags = inputflags
            result.append('\nlookupflag')
            for f in inputflags.split(' '):
                if f in flagDic:
                    result.append(flagDic[f])
                else:
                    result.append(f)
            self.flags += indent(' '.join(result))+';'

    def call(self):
        return 'lookup %s;' %self.lookupName

    def content(self, contents):
        """
        contents are the block of rules text joined with ";\n"
        """
        self.contents += indent(contents, 2)

    def syntax(self):
        return 'lookup %s {%s\n%s\n} %s;\n' %(self.lookupName, self.flags, self.contents, self.lookupName)

class sub:
    """

    """

class chain:
    """
        create a chain contextual for certain lookup(s).
    """


# which suffix belongs to which feature, and summary of supported features
suffix2tag = {
    "init": "init",  # inital
    "medi": "medi",  # medial
    "fina": "fina",  # final
    "isol": "isol",  # isolated
    "liga": "liga",  # standard ligatures (on by default)
    "rlig": "rlig",  # required ligatures (always on)
    "dlig": "dlig",  # discretionally ligatures
    "cmps": "ccmp",  # glyph composing
    "dcmp": "ccmp",  # glyph decomposing
    "calt": "calt",  # contextual alternates
    "conc": "calt", # arabic cursive connections
    "cap": "case",  # case sensetive
    "case": "case",  # case sensetive
    "zero": "zero",  # slashed zero
    "smcp": "smcp",  # small caps
    "lnum": "lnum",  # lining numbers
    "pnum": "pnum",  # proportional numbers
    "onum": "onum",  # old style numbers
    "tnum": "tnum",  # tabular number

    "onum_pnum": ("onum", "pnum"),
    "lnum_pnum": ("lnum", "pnum"),
    "onum_tnum": ("onum", "tnum"),
    "lnum_tnum": ("lnum", "tnum"),

    "ss01": "ss01",  # stylistic set 1
    "ss02": "ss02",  # stylistic set 2
    "ss03": "ss03",  # stylistic set 3
    "ss04": "ss04",  # stylistic set 4
    "ss05": "ss05",  # stylistic set 5
    "ss06": "ss06",  # stylistic set 6
    "ss07": "ss07",  # stylistic set 7
    "ss08": "ss08",  # stylistic set 8
    "ss09": "ss09",  # stylistic set 9
    "ss10": "ss10",  # stylistic set 10
    "ss11": "ss11",  # stylistic set 11
    "ss12": "ss12",  # stylistic set 12
    "ss13": "ss13",  # stylistic set 13
    "ss14": "ss14",  # stylistic set 14
    "ss15": "ss15",  # stylistic set 15
    "ss16": "ss16",  # stylistic set 16
    "ss17": "ss17",  # stylistic set 17
    "ss18": "ss18",  # stylistic set 18
    "ss19": "ss19",  # stylistic set 19
    "ss20": "ss20",  # stylistic set 20
}

fea2name = {
    'tnum': 'Tabular Numbers',
    'pnum': 'Proportional Numbers',
    'onum': 'Oldstyle Numbers',
    'lnum': 'Lining Numbers',
    'ss01': 'Stylistic Set 1',
    'ss02': 'Stylistic Set 2',
    'ss03': 'Stylistic Set 3',
    'ss04': 'Stylistic Set 4',
    'ss05': 'Stylistic Set 5',
    'ss06': 'Stylistic Set 6',
    'ss07': 'Stylistic Set 7',
    'ss08': 'Stylistic Set 8',
    'ss09': 'Stylistic Set 9',
    'ss10': 'Stylistic Set 10',
    'ss11': 'Stylistic Set 11',
    'ss12': 'Stylistic Set 12',
    'ss13': 'Stylistic Set 13',
    'ss14': 'Stylistic Set 14',
    'ss15': 'Stylistic Set 15',
    'ss16': 'Stylistic Set 16',
    'ss17': 'Stylistic Set 17',
    'ss18': 'Stylistic Set 18',
    'ss19': 'Stylistic Set 19',
    'ss20': 'Stylistic Set 20',
    'zero': 'Slashed Zero',
    'medi': 'Medial Forms',
    'init': 'Initial Forms',
    'isol': 'Isolated Forms',
    'fina': 'Final Forms',
    'smcp': 'Small Caps',
    'case': 'Case Senstive Forms',
    'ccmp': 'Glyph Composition/Decomposition',
    'rlig': 'Required Ligatures',
    'liga': 'Standard Ligatures',
    'dlig': 'Discretionary Ligatures',
    'mark': 'Mark Positioning',
    'mkmk': 'Mark to Mark Positioning',
    'calt': 'Contextaul Alternates',
    'curs': 'Cursive Attatchment',
    'kern': 'Kerning',
    'aalt': 'Access All Alternates',
    'locl': 'Localized Froms',
}


compositeTags = set(["liga", "dlig", "rlig", "ccmp"])
reversed_composite_suffixes = set(["dcmp"])

lig_splitter = "_"

class fontDic():

    """
        Object that converts font data to dictionaries which are used
        to interpret font data, to speedup font data queiries.
        This object now is adapted to robofont, but it could be
        adapted to other environments.
    """

    def __init__(self, f, marksToSkip=set(), skipGlyphs=set()):
        self.f = f
        self.marksToSkip = marksToSkip # glyphs that should not have mark positoning rules (arbitrary)
        self.skipGlyphs = set(['.null', '.notdef']) | skipGlyphs
        if self.f is not None:
            self.scripts = {} # {scriptName : [glyphName1, glyphName2] }
            self.localized = {} # {(script, language) : [gName1, gName2, ...]
            self.glyphScript = {} # {glyphName : scriptName}
            self.glyphAnchor = {} # hash of glyph names to list of anchors and thier positions
            self.anchors = {} # hash of anchor names to the glyph names
            self.glyphUnicode = {} # hash of glyph names to unicode values
            self.unicodToGlyphs = dict(self.f.getCharacterMapping()) # hash of unicode value to glyph name
            self.components = self.f.getReverseComponentMapping()
            self.glyphComps = {} # {gName : [comp1, comp2, ...]}
            self.baseGlyphOffsets = {} # {baseGlyph: [(composite: offset), ...}
            self.compOffsets = {} # {compositeName: {baseGlyph: offset}}
            self.glyphOrder = [g for g in f.glyphOrder if g in f and g not in self.skipGlyphs] # eliminating non existing glyphs
            self.marks = set()
            self.bases = set()
            self.mkmk = set() # glyphs that have mark to mark positioning
            self.skipVirtualMarks = set() # duplicated components means implicit mark positioning and should be skipped
            self.rtl = set() # set of the right to left glyphs in the font
            self.rtlGroups = set() # set of rtl groups
            self._groups = list(self.f.groups) #
            self.groups = dict(self.f.groups.items()) # hash of group names to their members
            self.rightGrouped = set() # set of glyphs which exist in right groups
            self.leftGrouped = set() # set of glyphs which exist in left groups
            self.kerning = dict(f.kerning) # kerning data
            self.glyphs = set() # set of glyph names
            self.composites = {} # ligatures and composites
            self.basic_subs = {} # fina, cap, etc
            # report of the problems in naming scheme, etc
            self.log = []
            # list of glyph which might never be substited
            self.substituted = set()
            self.possible_malfunctions = []
            languageTagsKeys = set(languageTags)
            languageTagsValues = set([x.lower() for x in languageTags.values()])

            self.glyphPseudoUnicode = {}
            for gName in self.glyphOrder:

                g = self.f[gName]
                self.glyphs.add(gName)

                gBase = glyphBase.findall(g.name)[0]
                if gBase in self.glyphPseudoUnicode and g.unicode is not None:
                    self.glyphPseudoUnicode[gBase].add(g.unicode)
                elif g.unicode is not None:
                    self.glyphPseudoUnicode[gBase] = set([g.unicode])
                # making unicode dictionary
                if gName in self.glyphUnicode and g.unicode is not None:
                    # gBase = glyphBase.findall(gName)[0]
                    self.glyphUnicode[gName].add(g.unicode)
                elif g.unicode is not None:
                    self.glyphUnicode[gName] = set([g.unicode])

                gAnchors = {}
                if g.components:
                    self.compOffsets[gName] = {}
                    for comp in g.components:
                        base = comp.baseGlyph
                        try:
                            self.baseGlyphOffsets[base]
                        except KeyError:
                            self.baseGlyphOffsets[base] = {}
                        offset = comp.offset
                        try:
                            self.baseGlyphOffsets[base][gName].add(offset)
                            self.skipVirtualMarks.add(gName) # glyps which has duplicated glyphs
                        except KeyError:
                            self.baseGlyphOffsets[base][gName] = set([offset])
                        try:
                            self.glyphComps[gName].append(base)
                        except KeyError:
                            self.glyphComps[gName] = [base]
                        self.compOffsets[gName][base] = comp.offset
                    self.glyphComps[gName] = tuple(self.glyphComps[gName])
                    if g.contours:
                        self.skipVirtualMarks.add(gName)

                # making anchor dictionaries
                if gName not in self.marksToSkip:
                    if len(g.anchors) > 0:
                        for anchor in g.anchors:
                            anchorName = anchor.name
                            if anchorName is not None:
                                if anchorName[0] == '_':
                                    self.marks.add(gName)
                                else:
                                    self.bases.add(gName)
                                if anchorName not in gAnchors:
                                    gAnchors[anchorName] = (anchor.x, anchor.y)
                                else:
                                    self.log.append("#\tWarning: anchor name '%s' is duplicated in glyph '%s'" %(anchorName, gName))
                                try:
                                    self.anchors[anchorName].add(gName)
                                except KeyError:
                                    self.anchors[anchorName] = set([gName])
                        self.glyphAnchor[gName] = gAnchors
                        self.skipVirtualMarks.discard(gName) # glyps which has duplicated glyphs but have anchors

            self.mkmk = self.marks & self.bases
            self.bases = self.bases - self.marks
            self._makeVirtualMarks()
            self.marksToSkip = self.marksToSkip | self.skipVirtualMarks
            for item in [self.marks, self.mkmk]:
                item -= self.marksToSkip

            # if all the glyphs from a anchor class doesn't have unicodes,
            # delete the class. but we need to make sure that these glyphs are
            # not substituted later by any gsub lookup.

            self.glyphSort = sorted(self.glyphOrder)
            for gName in self.glyphSort:
                g = self.f[gName]
                gp = glyphProperty(gName, self)
                gscript = gp.script()
                if gp.rtl():
                    self.rtl.add(gName)
                if gscript != '' and gscript in self.scripts:
                    self.scripts[gscript].append(gName)
                elif gscript != '':
                    self.scripts[gscript] = [gName]
                if gscript != '' and gName in self.glyphScript:
                    self.glyphScript[gName].append(gscript)
                elif gscript != '':
                    self.glyphScript[gName] = gscript

                # ------------ Making feature dictionaries -----------
                assigned = False

                suffix = gName.split(".")
                if gName in skipGlyphs:
                    continue
                ligas = gName.split(lig_splitter)
                base_glyph = None
                feature_tag = None
                if len(ligas) > 1:
                    comps = []  # ligature components
                    # we have a ligature or composite
                    ligature_without_suffix = ".".join(suffix[:-1]).split(lig_splitter)
                    if not set(ligas) - self.glyphs:
                        # all the components are found
                        comps = ligas
                        if gName in self.glyphUnicode:
                            feature_tag = "rlig"
                            # by default a ligature with unicode is a required
                            # ligature
                        else:
                            feature_tag = "liga"
                    elif not set(ligature_without_suffix) - self.glyphs:
                        # components are found if suffix is removed
                        comps = ligature_without_suffix
                        try:
                            feature_tag = suffix2tag[suffix[-1]]
                        except KeyError:
                            self.log.append(wrap("#\tWarning: Parsing name of glyph '%s' suffix and can't associate it with an OpenType syntax." %(gName)))

                    num_comps = len(comps)

                    if feature_tag in compositeTags:
                        assigned = True
                        notUni = set(comps) - set(self.glyphUnicode)
                        if notUni and notUni - self.substituted:
                            self.possible_malfunctions.append(gName)
                        self.substituted.add(gName)
                        sub_order = (num_comps, comps, [gName])
                        self._addComposite(feature_tag, sub_order)

                if not assigned:
                    comps = self._getNestedComps(gName)
                    markComps = [c for c in comps if c in self.marks] # can't use set intersection because it removes duplicates
                    baseComps = [c for c in self.glyphComps.get(gName, []) if c in self.bases]
                    if len(suffix) > 1:
                        base_glyph = ".".join(suffix[:-1])
                        if suffix[-1] == 'dcmp':
                            feature_tag = 'ccmp'
                            decomposed = []
                            comps = self.glyphComps.get(gName)
                            while comps:
                                for c in reversed(comps):
                                    if c not in self.glyphComps or len(self.glyphComps.get(c)) == 1:
                                        decomposed.insert(0, c)
                                comps = self._getComps(comps)
                            if decomposed:
                                missing = set(decomposed) - self.glyphs
                                if missing:
                                    self.log.append("#\tWarning: Can't decompose glyph '%s' to its components, missing component(s): %s" %(gName, ', '.join(missing)))
                                else:
                                    assigned = True
                                    sub_order = (1, [gName], decomposed)
                                    self._addComposite(feature_tag, sub_order)

                        elif base_glyph in self.glyphs:
                            suffixes = set([x.lower() for x in suffix[-1].split('_')]) # making sure pnum_onum also gets in
                            if not suffixes - set(suffix2tag):
                                for suffix in suffixes:
                                    feature_tag = suffix2tag[suffix]
                                    self.substituted.add(gName)
                                    assigned = True
                                    if base_glyph not in self.glyphUnicode and base_glyph not in self.substituted:
                                        self.possible_malfunctions.append(base_glyph)
                            elif not suffixes - languageTagsKeys or not suffixes - languageTagsValues:
                                for suffix in suffixes:
                                    if suffix in languageTagsKeys:
                                        language = languageTags[suffix]
                                        assigned = True
                                    elif suffix in languageTagsValues:
                                        language = suffix.upper()
                                        assigned = True
                                    else:
                                        continue
                                    script = self.glyphScript[gName]
                                    if script == 'dflt':
                                        script = 'latn'
                                    try:
                                        self.localized[(script, language)].append((base_glyph, gName))
                                    except KeyError:
                                        self.localized[(script, language)] = [(base_glyph, gName)]
                                    feature_tag = 'locl'
                            if assigned:
                                try:
                                    self.basic_subs[feature_tag][0].append(base_glyph)
                                    self.basic_subs[feature_tag][1].append(gName)
                                except KeyError:
                                    self.basic_subs[feature_tag] = [[base_glyph], [gName]]
                    elif (markComps and baseComps) or len(markComps) > 1:
                        assigned = True # not nessecary because there is no suffix
                        feature_tag = 'ccmp'
                        order = len(markComps)
                        allMarkPositions = permutations(markComps)
                        for comps in allMarkPositions:
                            # trying to compose glyph from its components if there
                            # is marks inside the glyph
                            sub_order = (order, baseComps + list(comps), [gName])
                            self._addComposite(feature_tag, sub_order)

                if (len(ligas) > 1 or len(suffix) > 1) and not assigned:
                    self.log.append("#\tWarning: Can't parse glyph name or associate glyph '%s' with a feature." %(gName))
                if assigned:
                    self.substituted.add(gName)


            for gr in self.groups:
                grGlyphs = self.groups[gr]
                if len(grGlyphs) > 0:
                    if set(grGlyphs) & self.rtl:
                        self.rtlGroups.add(gr)
                if '_R_' in gr:
                    self.rightGrouped.update(grGlyphs)
                elif '_L_' in gr:
                    self.leftGrouped.update(grGlyphs)
            if self.possible_malfunctions:
                error = wrap("#\tWarning: following glyphs might never be substituted in a text engine ever, check their unicode or the base glyph(s) unicode: %s" %(' '.join(self.possible_malfunctions)))
                self.log.append(error)
        else:
            raise Exception( "No font is available!")

    def _makeVirtualMarks(self):
        # adding marks to components according to base glyph if they don't
        # have that mark
        # note: if there are multiple marks in a composite which mark
        # should take which anchor for mark pos?
        defined = set()
        markBaseGlyphs = set(self.baseGlyphOffsets.keys()) & self.bases
        markBaseGlyphs -= self.marks
        while markBaseGlyphs:
            for markBase in set(markBaseGlyphs):
                markBaseGlyphs.discard(markBase)
                for extramark in self.baseGlyphOffsets.get(markBase, []):
                    # extramark is name of the glyph composite we're definging
                    # new marks for
                    offset = sorted(self.baseGlyphOffsets[markBase][extramark])[0]
                    if extramark in self.baseGlyphOffsets:
                        markBaseGlyphs.add(extramark)
                    x, y = offset
                    self.bases.add(extramark)
                    baseanchors = self.glyphAnchor[markBase]
                    anchors = {}
                    for anchorName, anchorpos in baseanchors.items():
                        x2, y2 = anchorpos
                        anchors[anchorName] = (x+x2, y+y2)
                    for baseMarkGlyph in set(self.glyphComps.get(extramark, [])) & self.marks:
                        # remove unnessasary marks which are alreddy composed
                        # inside the composite glyph.
                        for anchorName in self.glyphAnchor[baseMarkGlyph]:
                            anchors.pop(anchorName[1:], None)
                    for baseMarkGlyph in set(self.glyphComps.get(extramark, [])) & self.mkmk:
                        # add marks if the mark glyph has mkmk, so if there is
                        # diacritic in the composite, the composite will get a
                        # mark position according to the mark glyph.
                        x, y = self.compOffsets[extramark][baseMarkGlyph]
                        for anchorName, anchorpos in self.glyphAnchor[baseMarkGlyph].items():
                            if anchorName[0] == '_':
                                continue
                            x2, y2 = anchorpos
                            anchors[anchorName] = (x+x2, y+y2)
                    anchors.update(self.glyphAnchor.get(extramark, {})) # don't override added marks by user

                    for anchorName in anchors:
                        self.anchors[anchorName].add(extramark)
                    self.glyphAnchor[extramark] = anchors
        for gName in self.skipVirtualMarks:
            self.glyphAnchor.pop(gName, None)
        for a, gSet in self.anchors.items():
            self.anchors[a] = gSet - self.skipVirtualMarks

    def _getComps(self, glist):
        comps = []
        for gName in glist:
            compList = self.glyphComps.get(gName)
            if compList and len(compList) > 1:
                comps.extend(compList)
        return comps

    def _getNestedComps(self, gName):
        comps = list(self.glyphComps.get(gName, []))
        for comp in comps[:]:
            nested = self._getNestedComps(comp)
            if nested:
                comps.extend(nested)
                comps.remove(comp)
        return comps

    def _addComposite(self, feature_tag, sub_order):
        try:
            self.composites[feature_tag].append(sub_order)
        except KeyError:
            self.composites[feature_tag] = [sub_order]

    def __iter__(self):
        return self.glyphs.__iter__()

    def __getitem__(self, i):
        if i in self.glyphUnicode:
            return self.glyphUnicode.__getitem__(i)
        elif i in self.glyphs:
            return None
        else:
            raise KeyError("Glyph '%s' doesn't exist in the font" %i)


class abstractFeature(object):
    tag = ''

    def __init__(self, fDic, classes):
        self.base = set()
        self.ligature = set()
        self.mark = set()
        self.component = set()
        self.fDic = fDic
        self.classes = classes # {className : [glyphName1, glyphName2, ...]
        self.aalt = set() # if the feature has rules then this will containt the feature tag(s)
        self.log = []

    def checkClass(self, className, classContents):
        """
        checks if the class is already defined, if so check its contents.
        if the contents match then it reutrns the class without changes.
        otherwise returns an alternate name and the contents.
        """
        incrementor = 0
        tempClass = className
        classSort = classContents[:]
        classContents = set(classContents)

        while tempClass in self.classes and not classContents - set(self.classes[tempClass]):
            incrementor += 1
            classContents = classContents - set(self.classes[tempClass])
            tempClass = '%s_%i' %(className, incrementor)

        classContents = sorted(classContents, key=lambda x: classSort.index(x))

        return tempClass, classContents

    def getFlags(self, gList):
        """
        gets a glyph list and returns associated lookup flag
        """
        flags = []
        if not set(gList) - self.fDic.rtl:
            flags.append('rtl')
        if not set(gList) & self.fDic.marks:
            flags.append('nomark')
        if not flags:
            flags = ['noflag']
        return ' '.join(flags)

    def featureStart(self, tag=None):
        if tag is None:
            tag = self.tag
        return '\n#*************************************************************************\n#\n# %s \n#\n#*************************************************************************\n\n%s' %(fea2name[tag], '\n'.join(self.log))


class aaltFeature(object):
    tag = 'aalt'

    def __init__(self, aalt):
        self.aalt = aalt # list of features that needs to be included

    def featureStart(self, tag=None):
        if tag is None:
            tag = self.tag
        return '\n#*************************************************************************\n#\n# %s \n#\n#*************************************************************************\n\n' %fea2name[tag]

    def syntax(self):
        result = []
        if self.aalt:
            result.append(self.featureStart())
            finaFea = feature(self.tag)
            rules = []
            for fea in self.aalt:
                rule = 'feature %s;' %fea
                rules.append(rule)
            finaFea.content('\n'.join(rules))
            result.append('\n' + finaFea.syntax())
        return ''.join(result)
