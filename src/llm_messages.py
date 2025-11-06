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

CONTEXT = f"""El mensaje contiene información sobre un gasto de dinero.
Extrae los siguientes campos del mensaje:
- categoría: la categoría del gasto {CATEGORIAS}.
- moneda: la moneda en la que se realizó el gasto, por defencto es ARS.
"""
