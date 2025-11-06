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

CONTEXT = f"""El mensaje describe un gasto de dinero personal de un usuario.
Extrae:
- valor: monto numérico del gasto (usar punto como separador decimal).
- categoría: la categoría del gasto. Las opciones son: {", ".join(CATEGORIAS)}.
- moneda: la moneda del gasto (por defecto ARS si no se menciona).
"""

if __name__ == "__main__":
    print(CONTEXT)
