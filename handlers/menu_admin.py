from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os
from core.funciones import cargar_menu, cursor, db
from datetime import date
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID"))  # type: ignore

async def ver_pedidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:  # type: ignore
        await update.message.reply_text("🚫 No tenés permisos para ver los pedidos.")  # type: ignore
        return
    sql = "SELECT id, usuario, pedido FROM pedidos WHERE DATE(fecha) = %s"
    cursor.execute(sql, (date.today(),))
    resultados = cursor.fetchall()
    if resultados:
        botones = []
        for id, usuario, pedido in resultados:
            texto_boton = f"{usuario}: {pedido}"
            botones.append([InlineKeyboardButton(text=texto_boton, callback_data=f"entregar_{id}")])

        reply_markup = InlineKeyboardMarkup(botones)
        await update.message.reply_text(  # type: ignore
            "📋 *Pedidos del día:* \n Seleccioná uno para marcar como entregado",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("📭 No hay pedidos para hoy.")  # type: ignore

async def agregar_pancho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:  # type: ignore
        await update.message.reply_text("🚫 No tenés permisos para agregar panchos.")  # type: ignore
        return

    if not context.args:
        await update.message.reply_text("❗ Formato incorrecto.\nUsá: `/agregarpancho Nombre | Descripción | imagen.jpg`", parse_mode="Markdown")  # type: ignore
        return

    datos_crudos = " ".join(context.args)
    partes = [p.strip() for p in datos_crudos.split("|")]

    if len(partes) != 3:
        await update.message.reply_text("❌ Faltan datos. Usá: `/agregarpancho Nombre | Descripción | imagen.jpg`", parse_mode="Markdown")  # type: ignore
        return

    nombre, descripcion, imagen = partes

    try:
        sql = "INSERT INTO menu (nombre, descripcion, imagen) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, descripcion, imagen))
        db.commit()
        await update.message.reply_text(f"✅ Pancho agregado: *{nombre}*", parse_mode="Markdown")  # type: ignore
    except Exception as e:
        await update.message.reply_text(f"❌ Error al agregar pancho: {e}")  # type: ignore

async def eliminar_pancho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None or user.id != ADMIN_ID:
        await update.message.reply_text("🚫 No tenés permisos para eliminar panchos.")  # type: ignore
        return

    if not context.args:
        await update.message.reply_text("❗ Usá: `/eliminarpancho <id>`", parse_mode="Markdown")  # type: ignore
        return

    try:
        pancho_id = int(context.args[0])
        cursor.execute("SELECT nombre FROM menu WHERE id = %s", (pancho_id,))
        resultado = cursor.fetchone()
        if not resultado:
            await update.message.reply_text("❌ No se encontró ese pancho.")  # type: ignore
            return

        nombre = resultado[0]  # type: ignore
        cursor.execute("DELETE FROM menu WHERE id = %s", (pancho_id,))
        db.commit()
        await update.message.reply_text(f"🗑 Pancho eliminado: *{nombre}*", parse_mode="Markdown")  # type: ignore
    except ValueError:
        await update.message.reply_text("❌ ID inválido. Usá un número.")  # type: ignore

async def lista_panchos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = cargar_menu()
    if not menu:
        await update.message.reply_text("📭 El menú está vacío.")  # type: ignore
        return

    texto = "📋 *Lista de Panchos*\n\n"
    for id_, item in menu.items():
        texto += f"🆔 {id_} - *{item['nombre']}*\n_{item['descripcion']}_\n📷 {os.path.basename(item['imagen'])}\n\n"

    await update.message.reply_text(texto, parse_mode="Markdown")  # type: ignore
