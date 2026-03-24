from django import template

register = template.Library()

@register.filter(name='normalizar_campo')
def normalizar_campo(value):
    """
    Convierte nombre de producto a formato de campo de formulario.
    Solo reemplaza espacios por guiones, mantiene todo lo demás igual.
    Ejemplo: 'PASO #2' -> 'paso-#2'
             'Gran Pieza' -> 'gran-pieza'
    """
    return value.lower().replace(' ', '-')
    
@register.filter(name='dict_get')
def dict_get(d, key):
    """
    Obtiene un valor de un diccionario.
    Si es un número, lo formatea con punto decimal para compatibilidad con input type=number.
    """
    try:
        value = d.get(key, 0)
        # Asegurar formato con punto decimal para inputs HTML number
        if isinstance(value, (int, float)):
            return str(value).replace(',', '.')
        return value
    except Exception:
        return 0
