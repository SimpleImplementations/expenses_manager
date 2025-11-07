CATEGORIAS = (
    # Finanzas
    "TARJETA DE CRÉDITO",
    "INVERSIONES",
    # Comida
    "SUPERMERCADO",
    "SALIR A COMER",
    "COMIDA A DOMICILIO",
    # Vivienda / Hogar
    "LIMPIEZA",
    "MANTENIMIENTO HOGAR",
    "EXPENSAS",
    # Transporte
    "PÚBLICO",
    "TAXI",
    # Servicios básicos
    "ELECTRICIDAD",
    "GAS",
    "AGUA",
    "INTERNET",
    "TELÉFONO",
    "INMOBILIARIO",
    "MUNICIPAL",
    # Suscripciones / Tecnología
    "SPOTIFY",
    "CHATBOT",
    "TECNOLOGÍA",
    # Educación / Salud / Bienestar
    "EDUCACIÓN",
    "GIMNASIO",
    "ROPA",
    "SALUD",
    # Ocio / Sociales
    "SALIDAS SOCIALES",
    "VIAJES",
    "REGALOS",
    # Mascotas
    "MASCOTAS",
    # Misceláneo
    "TEST",
    "OTROS",
)


CONTEXT = f"""El mensaje describe un gasto de dinero personal de un usuario enviado por un corto mensaje de texto.
Extrae:
- valor: monto numérico del gasto (usar punto como separador decimal).
- categoría: la categoría del gasto. Las opciones son: {", ".join(CATEGORIAS)}.
- moneda: la moneda del gasto (por defecto ARS si no se menciona).
Si no hay buena coincidencia con las categorías, usar "Otros".
Si no hay valor, asignar 0.0.
"""

if __name__ == "__main__":
    print(CONTEXT)
