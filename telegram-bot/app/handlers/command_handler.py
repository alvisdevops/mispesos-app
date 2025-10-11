"""
Telegram bot command handlers
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from loguru import logger
from datetime import datetime, timedelta

from app.services.api_client import APIClient


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""

    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot")

    welcome_message = f"""
🎉 ¡Hola {user.first_name}! Bienvenido a MisPesos

Soy tu asistente personal para gestionar gastos de forma inteligente.

💡 **¿Cómo funciona?**
Simplemente escríbeme tus gastos en lenguaje natural:
• "50k almuerzo tarjeta"
• "pagué 25000 de uber efectivo"
• "compré pizza por 35mil"

🚀 **Comandos disponibles:**
/ayuda - Ver todos los comandos
/resumen - Gastos de hoy
/balance - Estado actual
/categorias - Ver categorías

¡Empezemos! Escríbeme tu primer gasto 📝
    """

    # Create inline keyboard with quick actions
    keyboard = [
        [
            InlineKeyboardButton("📊 Ver Resumen", callback_data="summary_today"),
            InlineKeyboardButton("📋 Ayuda", callback_data="help")
        ],
        [
            InlineKeyboardButton("🏷️ Categorías", callback_data="categories"),
            InlineKeyboardButton("💰 Balance", callback_data="balance")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help and /ayuda commands"""

    help_text = """
🔧 **Comandos disponibles:**

📝 **Registro de gastos:**
• Escribe en lenguaje natural: "50k almuerzo tarjeta"
• Envía foto de facturas para OCR automático
• Formatos válidos: 50k, 50mil, 50000

📊 **Consultas:**
• `/resumen` - Gastos de hoy
• `/resumen semanal` - Gastos de la semana
• `/resumen mensual` - Gastos del mes
• `/balance` - Estado financiero actual

🏷️ **Categorías:**
• `/categorias` - Ver todas las categorías
• `/categoria alimentacion` - Gastos por categoría

⚙️ **Configuración:**
• `/corregir [ID]` - Corregir una transacción
• `/validar [ID]` - Marcar como validada
• `/eliminar [ID]` - Eliminar transacción

🤖 **Ejemplos de uso:**
• "50k almuerzo tarjeta en el centro"
• "pagué 25000 de uber efectivo ayer"
• "compré ropa por 80mil débito"
• "gasolina 70k transferencia"

💡 **Tip:** Soy inteligente y entiendo contexto. ¡Habla natural!
    """

    await update.message.reply_text(help_text)


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /resumen command"""

    user_id = update.effective_user.id
    args = context.args

    # Determine summary period
    if args and args[0].lower() in ['semanal', 'semana']:
        period = 'weekly'
        period_text = 'esta semana'
    elif args and args[0].lower() in ['mensual', 'mes']:
        period = 'monthly'
        period_text = 'este mes'
    else:
        period = 'daily'
        period_text = 'hoy'

    try:
        # Get summary from API
        api_client = APIClient()
        summary = await api_client.get_summary(period, user_id)

        if summary:
            # Format summary message
            message = f"📊 **Resumen {period_text}:**\n\n"
            message += f"💰 Total gastado: ${summary['total_amount']:,.0f}\n"
            message += f"📝 Transacciones: {summary['transaction_count']}\n\n"

            # By category
            if summary['by_category']:
                message += "🏷️ **Por categoría:**\n"
                for category, amount in summary['by_category'].items():
                    percentage = (amount / summary['total_amount']) * 100 if summary['total_amount'] > 0 else 0
                    message += f"• {category}: ${amount:,.0f} ({percentage:.1f}%)\n"
                message += "\n"

            # By payment method
            if summary['by_payment_method']:
                message += "💳 **Por método de pago:**\n"
                for method, amount in summary['by_payment_method'].items():
                    message += f"• {method.title()}: ${amount:,.0f}\n"

            await update.message.reply_text(message, parse_mode='Markdown')

        else:
            await update.message.reply_text(
                f"📊 No encontré gastos para {period_text}.\n"
                "¡Empieza registrando tu primer gasto! 💪"
            )

    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error al obtener el resumen. Intenta de nuevo."
        )


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /balance command"""

    user_id = update.effective_user.id

    try:
        api_client = APIClient()

        # Get today's summary
        today_summary = await api_client.get_summary('daily', user_id)
        week_summary = await api_client.get_summary('weekly', user_id)
        month_summary = await api_client.get_summary('monthly', user_id)

        message = "💰 **Balance financiero:**\n\n"

        # Today
        today_amount = today_summary['total_amount'] if today_summary else 0
        today_count = today_summary['transaction_count'] if today_summary else 0
        message += f"📅 **Hoy:** ${today_amount:,.0f} ({today_count} transacciones)\n"

        # Week
        week_amount = week_summary['total_amount'] if week_summary else 0
        week_count = week_summary['transaction_count'] if week_summary else 0
        message += f"📅 **Esta semana:** ${week_amount:,.0f} ({week_count} transacciones)\n"

        # Month
        month_amount = month_summary['total_amount'] if month_summary else 0
        month_count = month_summary['transaction_count'] if month_summary else 0
        message += f"📅 **Este mes:** ${month_amount:,.0f} ({month_count} transacciones)\n\n"

        # Daily average this month
        days_in_month = datetime.now().day
        daily_avg = month_amount / days_in_month if days_in_month > 0 else 0
        message += f"📈 **Promedio diario:** ${daily_avg:,.0f}\n"

        # Top category this month
        if month_summary and month_summary['by_category']:
            top_category = max(month_summary['by_category'].items(), key=lambda x: x[1])
            message += f"🏆 **Categoría principal:** {top_category[0]} (${top_category[1]:,.0f})\n"

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error al obtener el balance. Intenta de nuevo."
        )


async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /categorias command"""

    try:
        api_client = APIClient()
        categories = await api_client.get_categories()

        if categories:
            message = "🏷️ **Categorías disponibles:**\n\n"

            for category in categories:
                icon = category.get('icon', '📦')
                name = category['name']
                count = category.get('transaction_count', 0)
                message += f"{icon} **{name}** ({count} transacciones)\n"

            message += "\n💡 Las categorías se asignan automáticamente usando IA"

            await update.message.reply_text(message, parse_mode='Markdown')

        else:
            await update.message.reply_text(
                "🏷️ No se pudieron cargar las categorías. Intenta de nuevo."
            )

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error al obtener las categorías."
        )


def setup_command_handlers(application: Application) -> None:
    """Setup all command handlers"""

    logger.info("Setting up command handlers...")

    # Basic commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler(["help", "ayuda"], help_command))

    # Summary and balance
    application.add_handler(CommandHandler("resumen", summary_command))
    application.add_handler(CommandHandler("balance", balance_command))

    # Categories
    application.add_handler(CommandHandler("categorias", categories_command))

    logger.info("✅ Command handlers configured")