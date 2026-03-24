from decimal import Decimal
from io import BytesIO

from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.styles import ParagraphStyle, TA_CENTER,TA_LEFT
from reportlab.lib.units import inch, mm,cm
from reportlab.lib import colors
from reportlab.platypus import (
        Paragraph, 
        Table, 
        SimpleDocTemplate, 
        Spacer, 
        TableStyle, 
        Paragraph)
from reportlab.lib.styles import getSampleStyleSheet
from Venta.models import Venta,Detalle
from django.db.models import Sum
from datetime import datetime
import time
from reportlab.platypus import Image




class Comprobante():

    def __init__(self,t):
        self.buf = BytesIO()
        self.v = Venta.objects.get(token=t)
        
        

    def run(self):
        self.doc = SimpleDocTemplate(self.buf,title=f"Detalle-{self.v.factura}",pagesize=(90 * mm, 297 * mm),topMargin=0.1*mm)#prueba 1100,prueba dos 90,prueba tres 78
        self.story = []
        self.encabezado()
        self.crearTabla()
        self.doc.build(self.story, onFirstPage=self.numeroPagina, 
            onLaterPages=self.numeroPagina)
        pdf = self.buf.getvalue()
        self.buf.close()
        return pdf
        

    def encabezado(self):
       
        
        total = Detalle.objects.filter(token=self.v.token ).aggregate(tot=Sum('total'))#total de la venta
        piezas = Detalle.objects.filter(token=self.v.token).aggregate(cantidad=Sum('cantidad'))#total de la venta
        mifecha = datetime.now()
        imagen_logo = Image("Dash/logo2.jpg", width=150, height=70)
        if self.v.total==None:
            total['tot']=0.00
        else:
            pass
        pp = Paragraph("SOCIEDAD ANONIMA", self.estiloPC())
        p1 = Paragraph(f"DETALLE COMPRA {self.v.factura}", self.estiloPC())
        a3 = Paragraph(f"Fecha {self.v.fecha}", self.estiloPC())
        despacho = Paragraph(f"Atendio {self.v.usuario}", self.estiloPC())
        fecha = Paragraph(f"Fecha {self.v.fecha.strftime('%d-%m-%Y')}", self.estiloPC())
        #n = Paragraph(f"", self.totalPC())
        #nom = Paragraph(f"Nombre:_______", self.totalPC())
        self.story.append(imagen_logo)
        self.story.append(pp)
        self.story.append(p1)
        self.story.append(a3)
        #self.story.append(n)
        #self.story.append(nom)
        self.story.append(despacho)

    def crearTabla(self):
        vv = Venta.objects.get(token=self.v.token)
        prop = round(vv.total*Decimal(0.10),2)
        to =  round(vv.total+(vv.total*Decimal(0.10)),2)
        data = [["Des","Can","Total"]] \
            +[[ x.platillo.nombre,x.cantidad, "Q."+str(x.total)] 
                for x in Detalle.objects.filter(token=self.v.token)]\
            +[["SUB-TOTAL DE VENTA "," ","Q."+str(vv.total)]]\
            +[[f"PROPINA 10% DE VENTA"," ","Q."+str(prop)]]\
            +[[f"TOTAL DE VENTA"," ","Q."+str(to)]]\
            +[["ULTIMA LINEA","----------------------",""]]


        table = Table(data,colWidths=[5.0*cm,1.2*cm,1.2*cm],hAlign=TA_CENTER)
        table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), "LEFT"),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,0), 7),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
    ]))    

        self.story.append(table)

    
    def totalPC(self):
        return ParagraphStyle(name='izquierda',
                          alignment=0,
                          fontName='Helvetica',
                          fontSize=8,
                          textColor=colors.black,
                          )
                          
    def estiloPC(self):
        return ParagraphStyle(name='izquierda',
                          alignment=0,
                          fontName='Helvetica',
                          fontSize=10,
                          leftIndent=0,
                          textColor=colors.black,)

    def estiloPC2(self):
        return ParagraphStyle(name='izquierda',
                          alignment=TA_CENTER,
                          fontName='Helvetica',
                          fontSize=8,
                          textColor=colors.black,
                          leftIndent=0,
                          allowWindows=1,)

    def estiloPC3(self):
        return ParagraphStyle(name='derecha',
                           fontName="Helvetica",
                           fontSize=8,
                           alignment=0,
                           spaceAfter=0)                       


    def numeroPagina(self,canvas,doc):
        num = canvas.getPageNumber()
        text = "Pagina %s" % num
        #canvas.drawRightString(50*mm, 20*mm, text)