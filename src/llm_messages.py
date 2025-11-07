CATEGORIAS = (
    # Finanzas
    "Tarjeta de Crédito",
    "Inversiones",
    # Comida
    "Supermercado",
    "Salir a Comer",
    "Comida a Domicilio",
    # Vivienda / Hogar
    "Limpieza",
    "Mantenimiento Hogar",
    "Expensas",
    # Transporte
    "Público",
    "Taxi",
    # Servicios básicos
    "Electricidad",
    "Gas",
    "Agua",
    "Internet",
    "Teléfono",
    "Inmobiliario",
    "Municipal",
    # Suscripciones / Tecnología
    "Spotify",
    "ChatBot",
    "Tecnología",
    # Educación / Salud / Bienestar
    "Educación",
    "Gimnasio",
    "Ropa",
    "Salud",
    # Ocio / Sociales
    "Salidas Sociales",
    "Viajes",
    "Regalos y Eventos",
    # Mascotas
    "Mascotas",
    # Seguros
    "Seguros",
    # Misceláneo
    "Test",
    "Otros",
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
