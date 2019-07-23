## What is this?
This is my personal package to automate generating OT features in RoboFont. It expects a specific naming scheme from your glyphs. This package has been used for commercial font projects, and it should create a reliable feature code unless you prove me wrong and I encourage you to do that. Although the kerning module was done in python 2 and there are some issues in python 3 that I need to address them. Please let me know about any bugs, I will try to fix it as soon as I can! 

## What features it generates?
`ccmp`, `smcp`, `case`, `fina`, `medi`, `init`, `isol`, `lnum`, `onum`, `pnum`, `tnum`, `zero`, `locl`, `ss01`, `ss02`, `ss03`, `ss04`, `ss05`, `ss06`, `ss07`, `ss08`, `ss09`, `ss10`, `ss11`, `ss12`, `ss13`, `ss14`, `ss15`, `ss16`, `ss17`, `ss18`, `ss19`, `ss20`, `rlig`, `liga`, `dlig`, `curs`, `kern`, `mark`, `mkmk`

## How it works?
### Substitutions
For substitutions, you need to suffix glyph names according to the feature tag. For example, if you have glyphs named `alef` and `alef.fina`, it will generate the `fina` feature for the `alef.fina`. It can create the numbers `lnum`, `onum`, `pnum`, `tnum` features by interpreting the proportions of the numeral glyphs. Ligature names should be named after their components separated by `_` and the component names should be explicit. This means if you have Arabic glyphs named `lam.medi` and `alef.fina` the ligature name should be `lam.medi_alef.fina`. If you want to have that ligature in the `rlig` it should be named `lam.medi_alef.fina.rlig`, so the feature tag gets added at the end.

For `ccmp` feature you need to suffix the glyph with either `cmps` for compositing or `dcmp` for decomposing. Before the suffix separate the component names in the glyph name by `_`. If there is no `_` in the glyph name, the module will decompose the glyph to its components inside the glyph.

### Mark Positioning
For mark positioning in the base letter glyphs, anchors should be named like `top` or `bottom` and in mark glyphs, it should be named `_top` or `_bottom`. For mark to mark positioning the base anchor should be named like `top`, same as base letters.

### Kerning
Kerning for RTL and LTR direction is generated automatically.

### Cursive attachment
Entry anchor should be named `*entry` and exit `*exit`. You can change these in the otCursive module.

## How to install?
1. Clone the repo
2. In terminal go to the repo directory and execute ```pip3 install -e .``` (installing in editable mode).

## How to generate the feature code?
### Using the python module:
You need to use fontParts to open the font, or you can use RoboFont. 

The following example shows how to use it outside RoboFont using fontParts.
```
from featureMan.familyFeatures import generateFeatures
from fontParts.fontshell.font import RFont
f = RFont("path/to/file.ufo")
generateFeatures(f)
```

Inside RoboFont you should also add the repo path to RF environments as described here [in RoboFont website](https://doc.robofont.com/documentation/building-tools/python/external-modules/).

```
from featureMan.familyFeatures import generateFeatures
f = CurrentFont()
generateFeatures(f)
```

### Using shell
You need arguments for the familyFeatures module to work. Use the following command for help:

```python3 "/path/to/repo/Lib/featureMan/familyFeatures.py" -h```


## Are you gonna add more features?
Probably, do you want me to?! I started to develop this package right after graduating from TypeMedia. I was an amateur designer, experimenting with python. The package doesn't contain any test to ensure the integrity of the generated code, and sometimes I encounter bugs. I want to start a new one that saves the features inside the UFO and doesn't deal with AFDKO feature file. But until I make that, I keep fixing bugs if you encounter one.

The issues of AFDKO feature file is not a topic for a discussion here. But for starters, if you've ever worked with Microsoft VOLT, you know how convenient it is to create OpenType tables compared to AFDKO feature file. It's not about the UI, it's about how the data is structured. It makes much more sense in VOLT. I'm studying the spec at the moment, so it's gonna be a long ride!

#### To do
* Fractions
* Superscript
* Subscript
* Ordinals
* Superior
* Inferior
* Sceintific Figures