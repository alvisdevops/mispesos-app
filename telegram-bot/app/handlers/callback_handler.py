"""
Telegram bot callback handlers for inline keyboard buttons
"""

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
from loguru import logger

from app.services.api_client import APIClient


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries from inline keyboards"""

    query = update.callback_query
    user_id = update.effective_user.id
    data = query.data

    logger.info(f"Processing callback query from user {user_id}: {data}")

    # Answer the callback query to remove loading state
    await query.answer()

    try:
        if data.startswith("validate_"):
            await handle_validate_transaction(query, context, data)

        elif data.startswith("edit_"):
            await handle_edit_transaction(query, context, data)

        elif data.startswith("delete_"):
            await handle_delete_transaction(query, context, data)

        elif data == "summary_today":
            await handle_summary_callback(query, context, "daily")

        elif data == "summary_weekly":
            await handle_summary_callback(query, context, "weekly")

        elif data == "summary_monthly":
            await handle_summary_callback(query, context, "monthly")

        elif data == "balance":
            await handle_balance_callback(query, context)

        elif data == "categories":
            await handle_categories_callback(query, context)

        elif data == "help":
            await handle_help_callback(query, context)

        elif data == "examples":
            await handle_examples_callback(query, context)

        else:
            logger.warning(f"Unknown callback data: {data}")
            await query.edit_message_text("❌ Acción no reconocida")

    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        await query.edit_message_text("❌ Ocurrió un error. Intenta de nuevo.")


async def handle_validate_transaction(query, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    """Handle transaction validation"""

    transaction_id = int(data.split("_")[1])
    user_id = query.from_user.id

    try:
        api_client = APIClient()
        success = await api_client.validate_transaction(transaction_id)

        if success:
            await query.edit_message_text(
                f"✅ **Transacción #{transaction_id} validada**\n\n"
                "La transacción ha sido marcada como correcta.\n"
                "Esto ayuda a mejorar la precisión del sistema de IA."
            )
        else:
            await query.edit_message_text(
                f"❌ **Error al validar transacción #{transaction_id}**\n\n"
                "No se pudo encontrar o validar la transacción."
            )

    except Exception as e:
        logger.error(f"Error validating transaction {transaction_id}: {e}")
        await query.edit_message_text("❌ Error al validar. Intenta de nuevo.")


async def handle_edit_transaction(query, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    """Handle transaction editing (placeholder)"""

    transaction_id = int(data.split("_")[1])

    # For now, just provide instructions
    message = f"✏️ **Editar Transacción #{transaction_id}**\n\n"
    message += "Para editar esta transacción, puedes:\n\n"
    message += "1️⃣ **Corregir con nuevo mensaje:**\n"
    message += "   Escribe: 'corregir [nuevo_monto] [descripción]'\n\n"
    message += "2️⃣ **Eliminar y crear nueva:**\n"
    message += "   Usa el botón 🗑️ Eliminar y escribe una nueva\n\n"
    message += "3️⃣ **Cambiar categoría:**\n"
    message += "   Escribe: 'categoria [nombre_categoria]'\n\n"
    message += "💡 **Próximamente:** Interface de edición completa"

    await query.edit_message_text(message)


async def handle_delete_transaction(query, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    """Handle transaction deletion"""

    transaction_id = int(data.split("_")[1])

    try:
        api_client = APIClient()
        success = await api_client.delete_transaction(transaction_id)

        if success:
            await query.edit_message_text(
                f"🗑️ **Transacción #{transaction_id} eliminada**\n\n"
                "La transacción ha sido eliminada exitosamente."
            )
        else:
            await query.edit_message_text(
                f"❌ **Error al eliminar transacción #{transaction_id}**\n\n"
                "No se pudo encontrar o eliminar la transacción."
            )

    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {e}")
        await query.edit_message_text("❌ Error al eliminar. Intenta de nuevo.")


async def handle_summary_callback(query, context: ContextTypes.DEFAULT_TYPE, period: str) -> None:
    """Handle summary callback"""

    user_id = query.from_user.id

    try:
        api_client = APIClient()
        summary = await api_client.get_summary(period, user_id)

        period_text = {"daily": "hoy", "weekly": "esta semana", "monthly": "este mes"}[period]

        if summary:
            message = f"📊 **Resumen {period_text}:**\n\n"
            message += f"💰 Total: ${summary['total_amount']:,.0f}\n"
            message += f"📝 Transacciones: {summary['transaction_count']}\n\n"

            # Top categories
            if summary['by_category']:
                message += "🏆 **Principales categorías:**\n"
                sorted_categories = sorted(
                    summary['by_category'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]

                for category, amount in sorted_categories:
                    percentage = (amount / summary['total_amount']) * 100
                    message += f"• {category}: ${amount:,.0f} ({percentage:.1f}%)\n"

            await query.edit_message_text(message)

        else:
            await query.edit_message_text(
                f"📊 No hay gastos registrados para {period_text}.\n"
                "¡Empieza registrando tu primer gasto!"
            )

    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        await query.edit_message_text("❌ Error al obtener resumen.")


async def handle_balance_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle balance callback"""

    user_id = query.from_user.id

    try:
        api_client = APIClient()

        # Get summaries for all periods
        today = await api_client.get_summary('daily', user_id)
        week = await api_client.get_summary('weekly', user_id)
        month = await api_client.get_summary('monthly', user_id)

        message = "💰 **Balance rápido:**\n\n"
        message += f"📅 Hoy: ${today['total_amount']:,.0f}\n" if today else "📅 Hoy: $0\n"
        message += f"📅 Semana: ${week['total_amount']:,.0f}\n" if week else "📅 Semana: $0\n"
        message += f"📅 Mes: ${month['total_amount']:,.0f}\n" if month else "📅 Mes: $0\n"

        await query.edit_message_text(message)

    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        await query.edit_message_text("❌ Error al obtener balance.")


async def handle_categories_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle categories callback"""

    try:
        api_client = APIClient()
        categories = await api_client.get_categories()

        if categories:
            message = "🏷️ **Categorías:**\n\n"

            for category in categories[:8]:  # Show first 8
                icon = category.get('icon', '📦')
                name = category['name']
                message += f"{icon} {name}\n"

            if len(categories) > 8:
                message += f"\n... y {len(categories) - 8} más"

            await query.edit_message_text(message)

        else:
            await query.edit_message_text("❌ Error al cargar categorías.")

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        await query.edit_message_text("❌ Error al obtener categorías.")


async def handle_help_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle help callback"""

    help_text = """
🔧 **Ayuda rápida:**

📝 **Ejemplos de uso:**
• "50k almuerzo tarjeta"
• "25000 uber efectivo"
• "compré pizza 35mil"

📊 **Comandos:**
• `/resumen` - Gastos de hoy
• `/balance` - Estado actual
• `/categorias` - Ver categorías

💡 **¡Habla natural!** El bot entiende contexto.
    """

    await query.edit_message_text(help_text)


async def handle_examples_callback(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle examples callback"""

    examples_text = """
💡 **Ejemplos válidos:**

💰 **Formatos de dinero:**
• "50k" = 50,000
• "50mil" = 50,000
• "50000" = 50,000
• "50.5k" = 50,500

📝 **Mensajes completos:**
• "50k almuerzo tarjeta"
• "pagué 25000 de uber efectivo"
• "compré pizza por 35mil débito"
• "gasolina 70k transferencia"
• "cine 15000 efectivo ayer"

🏷️ **Categorías detectadas:**
• Alimentación, Transporte, Servicios
• Entretenimiento, Salud, Ropa
• Educación, Casa, Otros

💳 **Métodos de pago:**
• tarjeta, efectivo, transferencia, débito
    """

    await query.edit_message_text(examples_text)


def setup_callback_handlers(application: Application) -> None:
    """Setup all callback handlers"""

    logger.info("Setting up callback handlers...")

    # All callback queries
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    logger.info("✅ Callback handlers configured")