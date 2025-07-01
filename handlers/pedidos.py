from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from core.funciones import cargar_menu, guardar_pedido
from core.funciones import cursor, db


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text( # type: ignore
        "🌭¡Bienvenido a Jurassic Panch!🦕 \n"
        "Elegí un pancho jurásico escribiendo el número de la opción:\n"
        "Recordá que todos nuestros DINOPANCHOS vienen con DINOPAPAS"
    )

    menu = cargar_menu()
    for opcion, item in menu.items():
        nombre = item["nombre"]
        descripcion = item["descripcion"]
        ruta_imagen = item["imagen"]
        texto = f"{opcion}. *{nombre}*\n_{descripcion}_\n\nEscribí `{opcion}` para pedir."

        try:
            with open(ruta_imagen, "rb") as foto:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id, # type: ignore
                    photo=foto,
                    caption=texto,
                    parse_mode="Markdown"
                )
        except FileNotFoundError:
            await update.message.reply_text( # type: ignore
                f"❌ No se encontró la imagen para *{nombre}* ({ruta_imagen})",
                parse_mode="Markdown"
            )

async def recibir_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = cargar_menu()
    texto = update.message.text.strip().lower() # type: ignore
    usuario = update.effective_user.username or update.effective_user.first_name # type: ignore

    if texto in menu:
        context.user_data["pedido_pendiente"] = texto # type: ignore
        nombre_pedido = menu[texto]["nombre"]
        await update.message.reply_text(f"🤔 ¿Querés pedir *{nombre_pedido}*? (responde *si* o *no*)", parse_mode="Markdown") # type: ignore

    elif texto == "si" and "pedido_pendiente" in context.user_data: # type: ignore
        opcion = context.user_data.pop("pedido_pendiente") # type: ignore
        pedido = menu[opcion]["nombre"]
        fecha = datetime.now()
        pedido_id = guardar_pedido(usuario, pedido, fecha)

        ticket = (
            "🎟 *Tu Ticket de Jurassic Panch*\n\n"
            f"🆔 Pedido N°: `{pedido_id}`\n"
            f"👤 Usuario: `{usuario}`\n"
            f"🌭 Producto: *{pedido}*\n"
            f"🕒 Fecha y hora: `{fecha.strftime('%d/%m/%Y %H:%M:%S')}`\n"
            "\n¡Gracias por tu pedido jurásico! 🦕🦖"
        )
        await update.message.reply_text(ticket, parse_mode="Markdown") # type: ignore

    elif texto == "no" and "pedido_pendiente" in context.user_data: # type: ignore
        context.user_data.pop("pedido_pendiente") # type: ignore
        await update.message.reply_text("🚫 Pedido cancelado. Volvé a elegir una opción:") # type: ignore
        menu = cargar_menu()
        for opcion, item in menu.items():
            nombre = item["nombre"]
            descripcion = item["descripcion"]
            ruta_imagen = item["imagen"]
            texto = f"{opcion}. *{nombre}*\n_{descripcion}_\n\nEscribí `{opcion}` para pedir."

            try:
                with open(ruta_imagen, "rb") as foto:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id, # type: ignore
                        photo=foto,
                        caption=texto,
                        parse_mode="Markdown"
                    )
            except FileNotFoundError:
                await update.message.reply_text( # type: ignore
                    f"❌ No se encontró la imagen para *{nombre}* ({ruta_imagen})",
                    parse_mode="Markdown"
                )
    else:
        await update.message.reply_text("❌ Opción no reconocida. Escribí un número del menú o respondé *sí* / *no* si estás confirmando un pedido.") # type: ignore

async def callback_entregar_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # type: ignore

    data = query.data  # ejemplo: "entregar_5" # type: ignore
    if data.startswith("entregar_"): # type: ignore
        pedido_id = int(data.split("_")[1]) # type: ignore

        sql = "DELETE FROM pedidos WHERE id = %s"
      
        cursor.execute(sql, (pedido_id,))
        db.commit()

        await query.edit_message_text("✅ Pedido marcado como entregado y eliminado.") # type: ignore
