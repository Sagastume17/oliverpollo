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
