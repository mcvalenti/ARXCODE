'''
Created on 9 ene. 2018

@author: curso
'''

from reportlab.pdfgen import canvas

def fonts(c):
    from reportlab.lib.units import inch
    text = "Now is the time for all good men to..."
    x = 1.8*inch
    y = 2.7*inch
    for font in c.getAvailableFonts():
        c.setFont(font, 10)
        c.drawString(x,y,text)
        c.setFont("Helvetica", 10)
        c.drawRightString(x-10,y, font+":")
        y = y-13
    
def hello(c):
    c.drawString(100,100,"Hello World")

c = canvas.Canvas("hello01.pdf")

#hello(c)
fonts(c)
c.showPage()
c.save()


"""


def horizontalscale(canvas):
    from reportlab.lib.units import inch
        textobject = canvas.beginText()
        textobject.setTextOrigin(3, 2.5*inch)
        textobject.setFont("Helvetica-Oblique", 12)
        horizontalscale = 80 # 100 is default
    for line in lyrics:
    textobject.setHorizScale(horizontalscale)
    textobject.textLine("%s: %s" %(horizontalscale,line))
    horizontalscale = horizontalscale+10
    textobject.setFillColorCMYK(0.0,0.4,0.4,0.2)
    textobject.textLines('''
     With many apologies to the Beach Boys
     and anyone else who finds this objectionable
     ''')
    canvas.drawText(textobject)
"""
