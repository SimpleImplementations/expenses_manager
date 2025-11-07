from typing import Final

START_MESSAGE: Final[str] = (
    "👋 Bienvenido\n\n"
    "Enviá un mensaje con un gasto incluyendo monto y comentario.\n"
    "Si la moneda no es ARS podés aclararla.\n\n"
    "Ejemplos:\n"
    '"café en la facu 150"\n'
    '"20.5 USD regalo cumple"\n'
    '"netflix 799,99"\n\n'
    "Tips rápidos:\n"
    "• Editá tu mensaje para modificar un gasto ya cargado.\n"
    "• Respondé al mensaje del gasto con /delete para eliminarlo.\n"
    "• Usá /report para descargar tus gastos en CSV.\n"
    "• Usá /help para ver todos los comandos."
)

HELP_MESSAGE: Final[str] = (
    "📖 *Ayuda*\n\n"
    "Comandos disponibles:\n"
    "• /help — muestra esta ayuda\n"
    "• /start — introducción rápida\n"
    "• /report — descarga tus gastos en CSV\n"
    "• /delete — elimina un gasto\n\n"
    "Cómo usar el bot:\n"
    "• *Registrar un gasto*  simplemente escribí el texto del gasto por ejemplo\n"
    "almuerzo en restaurante 2500\n"
    "  siempre un gasto a la vez. El chat se encargará de asignarle una categoría y guardarlo\n"
    "• *Modificar un gasto ya cargado*  editá el mensaje original del gasto\n"
    "  el registro anterior se elimina y se vuelve a crear con el nuevo contenido\n"
    "• *Eliminar un gasto*  respondé al mensaje del gasto con /delete\n"
    "  debés citar el mensaje del gasto que querés borrar\n"
)
