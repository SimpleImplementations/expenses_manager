from typing import Final

START_MESSAGE: Final[str] = (
    "<b>👋 Bienvenido</b>\n\n"
    "Enviá un mensaje con un gasto incluyendo monto y comentario.\n"
    "Si la moneda no es ARS podés aclararla.\n\n"
    "<b>Ejemplos:</b>\n"
    "<i>café en la facu 150</i>\n"
    "<i>20.5 USD regalo cumple</i>\n"
    "<i>netflix 799,99</i>\n\n"
    "<b>Tips rápidos:</b>\n"
    "• Editá tu mensaje para modificar un gasto ya cargado.\n"
    "• Respondé al mensaje del gasto con /delete para eliminarlo.\n"
    "• Usá /report para descargar tus gastos en CSV.\n"
    "• Usá /help para ver todos los comandos."
)

HELP_MESSAGE: Final[str] = (
    "📖 <b>Ayuda</b>\n\n"
    "<b>Comandos disponibles:</b>\n"
    "• /help — muestra esta ayuda\n"
    "• /start — introducción rápida\n"
    "• /report — descarga tus gastos en CSV\n"
    "• /delete — elimina un gasto\n\n"
    "<b>Cómo usar el bot:</b>\n"
    "• <b>Registrar un gasto:</b> simplemente escribí el texto del gasto.\n"
    "  Ejemplo:\n"
    "  <i>almuerzo en restaurante 2500</i>\n"
    "  (Se registra un gasto por mensaje. El bot detecta monto, moneda y categoría automáticamente.)\n\n"
    "• <b>Modificar un gasto:</b> editá el mensaje original del gasto.\n"
    "  El registro anterior se elimina y se vuelve a crear actualizado.\n\n"
    "• <b>Eliminar un gasto:</b> respondé al mensaje del gasto con /delete.\n"
    "  Debés citar el mensaje correcto que querés borrar."
)
