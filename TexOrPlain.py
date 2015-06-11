class TexOrPlain:
    def __init__(self, latex = False, numcol=1):
        "Helper class for plain or latex tables"

        self.latex     = latex
        self.colsep    = '&' if self.latex else '|'
        self.rowstart  = '' if self.latex else '|'
        self.rowend    = '\\\\' if self.latex else '|'
        self.rowsep    = '\\hline\\hline' if self.latex else '-'
        self.pm        = '\\pm' if self.latex else '+-'
        self.times     = '\\times' if self.latex else 'x'
        self.math      = '$' if self.latex else ''
        self.grpbeg    = '{' if self.latex else ''
        self.grpend    = '}' if self.latex else ''
        self.ext       = '.tex' if self.latex else '.txt'

        if latex:
            self.filebeg  = """
\\documentstyle[12pt, epsfig]{article}
\\setlength {\\textheight} {23 true cm}
\\setlength {\\textwidth} {15 true cm}
\\setlength {\\oddsidemargin} {-1.5 mm}
\\setlength {\\evensidemargin} {10.55 mm}
\\setlength {\\topmargin} {-5 mm}
\\setlength {\\headheight} {15 pt}
\\setlength {\\headsep} {30 pt}
\\textfloatsep 10 mm
\\pagestyle{empty}
\\begin{document} 
\\begin{table} [h]
\\begin{tabular}[h]{|%s}
""" % ('l|'*numcol)
        else: 
            self.filebeg=''

        if latex:
            self.fileend = """
\\end{tabular}
\\end{table}
\\end{document}
"""
        else:
            self.fileend=''

        pass
    pass
