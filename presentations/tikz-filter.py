#!/usr/bin/env python3

"""
Pandoc filter to process raw latex tikz environments into images.
Assumes that pdflatex is in the path, and that the standalone
package is available.  Also assumes that ImageMagick's convert
is in the path. Images are put in the tikz-images directory.
"""

import hashlib
import re
import os
import sys
import shutil
from pandocfilters import toJSONFilter, Para, Image
from subprocess import Popen, PIPE, call
from tempfile import mkdtemp

imagedir = "tikz-images"


def sha1(x):
    return hashlib.sha1(x.encode(sys.getfilesystemencoding())).hexdigest()


def tikz2image(tikz, filetype, outfile):
    tmpdir = mkdtemp()
    olddir = os.getcwd()
    os.chdir(tmpdir)
    f = open('tikz.tex', 'w')
    f.write("""\\RequirePackage{luatex85}
             \\documentclass{standalone}
             \\usepackage{tikz}
             
             \\usetikzlibrary{positioning,shapes,arrows, fit}
             \\begin{document}
             \\begin{tikzpicture}
             """)
    f.write(tikz)
    f.write("\n\\end{tikzpicture}\n\\end{document}\n")
    f.close()
    p = call(["lualatex", 'tikz.tex'], stdout=sys.stderr)
    os.chdir(olddir)
    if filetype == 'pdf':
        shutil.copyfile(tmpdir + '/tikz.pdf', outfile + '.pdf')
    elif filetype == 'svg':
        call(["pdf2svg", tmpdir+'/tikz.pdf', outfile + '.svg'])
    else:
        call(["convert", tmpdir + '/tikz.pdf', outfile + '.' + filetype])
    shutil.rmtree(tmpdir)


def tikz(key, value, format, meta):
    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value
        caption = "caption"
        if 'tikz' in classes:
            outfile = imagedir + '/' + sha1(code)
            if format == "latex":
                filetype = "pdf"
            else:
                filetype = "svg"
            src = outfile + '.' + filetype
            if not os.path.isfile(src):
                try:
                    os.mkdir(imagedir)
                    sys.stderr.write('Created directory ' + imagedir + '\n')
                except OSError:
                    pass
                tikz2image(code, filetype, outfile)
                sys.stderr.write('Created image ' + src + '\n')
            return Para([Image(['', [], []], [], [src, ""])])

if __name__ == "__main__":
        toJSONFilter(tikz)
