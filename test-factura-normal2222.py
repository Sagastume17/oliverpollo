
#importar lo necesario
import InfileFel
import emisor 
import receptor 

#crear el DTE a Certificar
dte_fel_a_certificar = InfileFel.fel_dte()

# crear el emisor
emisor_fel = emisor.emisor()

# crear el receptor
receptor_fel = receptor.receptor()

# crear los totales
total_fel = InfileFel.totales()

#totales impuestos
totales_impuestos = InfileFel.total_impuesto()


# setear direccion del emisor
emisor_fel.set_direccion('direccion ','01001','guatemala','guatemala','GT')

# setear datos del emisor fel
# Parametros:  afiliacion_iva, codigo_establecimiento, correo_emisor, nit_emisor, nombre_comercial, nombre_emisor
emisor_fel.set_datos_emisor('GEN','1','cescmazariegos@gmail.com','11200188K','GHORTENSIA_DEMO','infile s.a.' )

# setear direccion del receptor
receptor_fel.set_direccion('5TA. CALLE Y 13 AVENIDA ESQUINA ZONA1 ZACAPA','19001','ZACAPA','guatemala','GT')

# setear datos del receptor
receptor_fel.set_datos_receptor('cescmazariegos@gmail.com','28208129','kua kua kua')

#identificador unico del dte del cliente
dte_fel_a_certificar.set_clave_unica('20200411')

#setear datos generales
dte_fel_a_certificar.set_datos_generales('GTQ','2023-02-13T00:00:00-06:00','FACT')

#agregar los datos del emisor
dte_fel_a_certificar.set_datos_emisor(emisor_fel)
# agregar los datos del receptor
dte_fel_a_certificar.set_datos_receptor(receptor_fel)

# agregar las frases
dte_fel_a_certificar.frase_fel.set_frase('1','1')
#dte_fel_a_certificar.frase_fel.set_frase('1','1','20185687029123456789','2018-10-11')

# crear el item del detalle de la factura
item_1 = InfileFel.item()

#crear los impuestos del detalle de la factura
item_1_impuesto = InfileFel.impuesto()

#llenar el item con los datos necesarios
item_1.set_numero_linea(1)
item_1.set_bien_o_servicio('B')
item_1.set_cantidad(1)
item_1.set_unidad_medida('UND')
item_1.set_descripcion('DESCRIPCION DEL ITEM A VENDER POR UNIDAD DESDE PY')
item_1.set_precio_unitario(112)
item_1.set_precio(112)
item_1.set_descuento(0)
item_1.set_total(112)

#llenar los impuestos del item
item_1_impuesto.set_monto_impuesto(12)
item_1_impuesto.set_monto_gravable(100)
item_1_impuesto.set_codigo_unidad_gravable(1)
item_1_impuesto.set_nombre_corto('IVA')
item_1.set_impuesto(item_1_impuesto)


# Agregar el item 1
dte_fel_a_certificar.agregar_item(item_1)

# crear el item 2
item_2 = InfileFel.item()


item_2_impuesto = InfileFel.impuesto()

item_2.set_numero_linea(1)
item_2.set_bien_o_servicio('S')
item_2.set_cantidad(1)
item_2.set_unidad_medida('UND')
item_2.set_descripcion('22222  DESCRIPCION DEL ITEM A VENDER POR UNIDAD DESDE PY')
item_2.set_precio_unitario(112)
item_2.set_precio(112)
item_2.set_descuento(0)
item_2.set_total(112)


item_2_impuesto.set_monto_impuesto(12)
item_2_impuesto.set_monto_gravable(100)
item_2_impuesto.set_codigo_unidad_gravable(1)
item_2_impuesto.set_nombre_corto('IVA')
item_2.set_impuesto(item_2_impuesto)

# agregar el item 2
dte_fel_a_certificar.agregar_item(item_2)

### agregar el gran total 
total_fel.set_gran_total(224)

### agregar datos del gran total de impuestos

totales_impuestos.set_nombre_corto('IVA')
totales_impuestos.set_total_monto_impuesto(24)

total_fel.set_total_impuestos(totales_impuestos)
 
###agregar los totales
dte_fel_a_certificar.agregar_totales(total_fel)

#agregar adendas al gusto 
fel_adenda = InfileFel.adenda()
fel_adenda.nombre= "factura_ruta"
fel_adenda.valor= "s"
dte_fel_a_certificar.agregar_adenda(fel_adenda)

#contingencia
#dte_fel_a_certificar.set_acceso('123123')

#agregando el tipo de personeria
#dte_fel_a_certificar.set_tipo_personeria('2')

#realizar el llamado a la certificada
certificacion_fel= dte_fel_a_certificar.certificar()
if (certificacion_fel["resultado"]):
    print ("UUID:" + certificacion_fel["uuid"])
    print ("FECHA:"+ certificacion_fel["fecha"])
    print ("SERIE:"+ certificacion_fel["serie"])
    print ("numero:"+ str(certificacion_fel["numero"]))
else:
    print("No pudo ser certificada")  
    print("Descripcion: " +  certificacion_fel["descripcion"] )

for error_fel in certificacion_fel["descripcion_errores"]:
    print("Mensaje Error: " +  error_fel["fuente"] )
    print("fuente: " +  error_fel["mensaje_error"] )
    print("categoria: " +  error_fel["categoria"] )
    print("numeral: " +  error_fel["numeral"] )
    print("validacion: " +  error_fel["validacion"] )