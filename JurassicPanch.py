from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import os
from dotenv import load_dotenv
from handlers.pedidos import start, recibir_pedido, callback_entregar_pedido
from handlers.menu_admin import ver_pedidos, agregar_pancho, eliminar_pancho, lista_panchos

load_dotenv()

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()  # type: ignore

    # Handlers de usuario
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_pedido))

    # Handlers de admin
    app.add_handler(CommandHandler("verpedidos", ver_pedidos))
    app.add_handler(CommandHandler("agregarpancho", agregar_pancho))
    app.add_handler(CommandHandler("eliminarpancho", eliminar_pancho))
    app.add_handler(CommandHandler("listapanchos", lista_panchos))

    # Callback para entrega de pedidos
    app.add_handler(CallbackQueryHandler(callback_entregar_pedido))

    print("Jurassic Panch está funcando")
    app.run_polling()
