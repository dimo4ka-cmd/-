import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import (
    init_db, get_user, add_user, add_to_queue, get_queue, get_user_archive, get_stats,
    get_secret_codes, move_to_archive, block_user, get_payouts, update_payout,
    get_support_tickets, respond_to_ticket, update_balance, create_secret_code,
    create_rent_request, get_rent_requests, update_rent_request_status, create_support_ticket
)
from keyboards import get_user_menu, get_admin_menu, get_ref_code_menu, get_admin_action_menu, get_paginated_requests, get_paginated_queue, get_paginated_tickets
from localization import MESSAGES
from utils import validate_phone, validate_ref_code, is_admin, format_queue, format_archive, format_stats
from config import ADMIN_IDS, MAX_NUMBERS_PER_USER
from datetime import datetime

logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    """Обработка команды /start"""
    init_db()
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "User"
    user = get_user(user_id)
    try:
        if user:
            text = MESSAGES['already_registered'].format(username=username)
            reply_markup = get_user_menu() if not is_admin(user_id) else get_admin_menu()
        else:
            text = MESSAGES['welcome'].format(username=username)
            reply_markup = get_ref_code_menu()
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await update.message.reply_text(MESSAGES['error'], reply_markup=get_ref_code_menu(), parse_mode='HTML')

async def admin_command(update: Update, context: CallbackContext):
    """Обработка команды /admin"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "Admin"
    try:
        if not is_admin(user_id):
            await update.message.reply_text(
                MESSAGES['access_denied'],
                reply_markup=get_user_menu(),
                parse_mode='HTML'
            )
            return
        await update.message.reply_text(
            MESSAGES['admin_panel'].format(username=username),
            reply_markup=get_admin_menu(),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Ошибка в /admin: {e}")
        await update.message.reply_text(MESSAGES['error'], reply_markup=get_user_menu(), parse_mode='HTML')

async def handle_message(update: Update, context: CallbackContext):
    """Обработка текстовых сообщений"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "User"
    message = update.message.text.strip()
    user = get_user(user_id)

    try:
        if not user:
            await update.message.reply_text(
                MESSAGES['enter_ref_code'].format(username=username),
                reply_markup=get_ref_code_menu(),
                parse_mode='HTML'
            )
            return

        if user[4]:  # is_blocked
            await update.message.reply_text(
                MESSAGES['user_blocked_message'],
                reply_markup=get_user_menu() if not is_admin(user_id) else get_admin_menu(),
                parse_mode='HTML'
            )
            return

        # Ввод номера телефона
        if context.user_data.get('awaiting_phone', False):
            if not validate_phone(message):
                await update.message.reply_text(
                    MESSAGES['invalid_phone'],
                    reply_markup=get_user_menu(),
                    parse_mode='HTML'
                )
                return
            queue = get_queue()
            if any(q[2] == message for q in queue):
                await update.message.reply_text(
                    MESSAGES['phone_in_queue'],
                    reply_markup=get_user_menu(),
                    parse_mode='HTML'
                )
                return
            if len([q for q in queue if q[1] == user_id]) >= MAX_NUMBERS_PER_USER:
                await update.message.reply_text(
                    MESSAGES['max_numbers_reached'].format(max=MAX_NUMBERS_PER_USER),
                    reply_markup=get_user_menu(),
                    parse_mode='HTML'
                )
                return
            success, response = add_to_queue(user_id, message)
            if success:
                request_id = create_rent_request(user_id, message)
                for admin_id in ADMIN_IDS:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=MESSAGES['new_rent_request'].format(
                            request_id=request_id,
                            username=username,
                            user_id=user_id,
                            phone_number=message,
                            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M')
                        ),
                        parse_mode='HTML'
                    )
            await update.message.reply_text(
                response,
                reply_markup=get_user_menu(),
                parse_mode='HTML'
            )
            context.user_data['awaiting_phone'] = False
            return

        # Запрос в поддержку
        if context.user_data.get('awaiting_support', False):
            if len(message) < 5:
                await update.message.reply_text(
                    MESSAGES['support_too_short'],
                    reply_markup=get_user_menu(),
                    parse_mode='HTML'
                )
                return
            ticket_id = create_support_ticket(user_id, message)
            for admin_id in ADMIN_IDS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=MESSAGES['new_support_ticket'].format(
                        ticket_id=ticket_id,
                        username=username,
                        user_id=user_id,
                        question=message[:100] + ('...' if len(message) > 100 else ''),
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M')
                    ),
                    parse_mode='HTML'
                )
            await update.message.reply_text(
                MESSAGES['support_submitted'].format(ticket_id=ticket_id),
                reply_markup=get_user_menu(),
                parse_mode='HTML'
            )
            context.user_data['awaiting_support'] = False
            return

        # Админ-команды
        if is_admin(user_id):
            if context.user_data.get('awaiting_code', False):
                try:
                    code, max_uses = message.split()
                    max_uses = int(max_uses)
                    if not validate_ref_code(code):
                        raise ValueError("Неверный формат кода")
                    create_secret_code(code, max_uses)
                    await update.message.reply_text(
                        MESSAGES['code_created'].format(code=code),
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                except (ValueError, IndexError):
                    await update.message.reply_text(
                        MESSAGES['create_code_format'],
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                context.user_data['awaiting_code'] = False
            elif context.user_data.get('awaiting_archive', False):
                try:
                    queue_id, status, amount = message.split()
                    queue_id = int(queue_id)
                    amount = float(amount)
                    move_to_archive(queue_id, status, amount)
                    await update.message.reply_text(
                        MESSAGES['moved_to_archive'],
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                except (ValueError, IndexError):
                    await update.message.reply_text(
                        MESSAGES['move_archive_format'],
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                context.user_data['awaiting_archive'] = False
            elif context.user_data.get('awaiting_payout', False):
                try:
                    payout_id, status = message.split()
                    payout_id = int(payout_id)
                    update_payout(payout_id, status)
                    await update.message.reply_text(
                        MESSAGES['payout_updated'].format(payout_id=payout_id),
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                except (ValueError, IndexError):
                    await update.message.reply_text(
                        MESSAGES['update_payout_format'],
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                context.user_data['awaiting_payout'] = False
            elif context.user_data.get('awaiting_ticket', False):
                try:
                    ticket_id, response = message.split(' ', 1)
                    ticket_id = int(ticket_id)
                    respond_to_ticket(ticket_id, response)
                    ticket = [t for t in get_support_tickets() if t[0] == ticket_id]
                    if ticket:
                        await context.bot.send_message(
                            chat_id=ticket[0][1],
                            text=MESSAGES['ticket_response'].format(
                                ticket_id=ticket_id,
                                response=response
                            ),
                            parse_mode='HTML'
                        )
                    await update.message.reply_text(
                        MESSAGES['ticket_responded'].format(ticket_id=ticket_id),
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                except (ValueError, IndexError):
                    await update.message.reply_text(
                        MESSAGES['respond_ticket_format'],
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                context.user_data['awaiting_ticket'] = False
            elif context.user_data.get('awaiting_block', False):
                try:
                    target_user_id = message.strip()
                    block_user(target_user_id)
                    await update.message.reply_text(
                        MESSAGES['user_blocked'].format(user_id=target_user_id),
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                except Exception:
                    await update.message.reply_text(
                        MESSAGES['block_user_format'],
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                context.user_data['awaiting_block'] = False
            elif context.user_data.get('awaiting_balance', False):
                try:
                    target_user_id, amount = message.split()
                    amount = float(amount)
                    update_balance(target_user_id, amount)
                    await update.message.reply_text(
                        MESSAGES['balance_updated'].format(user_id=target_user_id),
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                except (ValueError, IndexError):
                    await update.message.reply_text(
                        MESSAGES['update_balance_format'],
                        reply_markup=get_admin_menu(),
                        parse_mode='HTML'
                    )
                context.user_data['awaiting_balance'] = False
            else:
                await update.message.reply_text(
                    MESSAGES['admin_unknown_command'],
                    reply_markup=get_admin_menu(),
                    parse_mode='HTML'
                )
        else:
            await update.message.reply_text(
                MESSAGES['unknown_command'],
                reply_markup=get_user_menu(),
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        await update.message.reply_text(MESSAGES['error'], reply_markup=get_user_menu(), parse_mode='HTML')

async def handle_callback_query(update: Update, context: CallbackContext):
    """Обработка инлайн-кнопок"""
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    username = query.from_user.username or "User"
    data = query.data
    user = get_user(user_id)

    try:
        if not user:
            await query.message.edit_text(
                MESSAGES['enter_ref_code'].format(username=username),
                reply_markup=get_ref_code_menu(),
                parse_mode='HTML'
            )
            return

        if user[4]:  # is_blocked
            await query.message.edit_text(
                MESSAGES['user_blocked_message'],
                reply_markup=get_user_menu() if not is_admin(user_id) else get_admin_menu(),
                parse_mode='HTML'
            )
            return

        if data == "ref_code:ABC123":
            success, response = add_user(user_id, username, "ABC123")
            if success:
                for admin_id in ADMIN_IDS:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=MESSAGES['new_user'].format(
                            username=username,
                            user_id=user_id,
                            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M')
                        ),
                        parse_mode='HTML'
                    )
            await query.message.edit_text(
                response,
                reply_markup=get_user_menu() if success and not is_admin(user_id) else get_admin_menu() if success else get_ref_code_menu(),
                parse_mode='HTML'
            )
            return

        if not is_admin(user_id):
            if data == "action:queue":
                queue = get_queue()
                text = format_queue(queue, user_id)
                await query.message.edit_text(
                    text,
                    reply_markup=get_user_menu(),
                    parse_mode='HTML'
                )
            elif data == "action:archive":
                archive = get_user_archive(user_id)
                text = format_archive(archive)
                await query.message.edit_text(
                    text,
                    reply_markup=get_user_menu(),
                    parse_mode='HTML'
                )
            elif data == "action:stats":
                total_users, today_numbers = get_stats()
                text = format_stats(total_users, today_numbers)
                await query.message.edit_text(
                    text,
                    reply_markup=get_user_menu(),
                    parse_mode='HTML'
                )
            elif data == "action:payout":
                balance = user[3]
                text = MESSAGES['balance'].format(username=username, balance=balance)
                await query.message.edit_text(
                    text,
                    reply_markup=get_user_menu(),
                    parse_mode='HTML'
                )
            elif data == "action:add_phone":
                context.user_data['awaiting_phone'] = True
                await query.message.edit_text(
                    MESSAGES['enter_phone'],
                    reply_markup=None,
                    parse_mode='HTML'
                )
            elif data == "action:support":
                context.user_data['awaiting_support'] = True
                await query.message.edit_text(
                    MESSAGES['support_prompt'],
                    reply_markup=None,
                    parse_mode='HTML'
                )
            return

        # Админ-действия
        if data == "action:codes":
            codes = get_secret_codes()
            text = MESSAGES['codes_title'] + "<br><br>" + "<br>".join([
                f"🔑 <b>{c[0]}</b><br>   Использовано: <i>{c[3]}/{c[2]}</i><br>   Тип: <i>{'Одноразовый' if c[1] else 'Многоразовый'}</i><br>   Создатель: <i>{c[4]}</i>"
                for c in codes
            ]) if codes else MESSAGES['no_codes']
            await query.message.edit_text(
                text,
                reply_markup=get_admin_action_menu('codes'),
                parse_mode='HTML'
            )
        elif data.startswith("action:queue"):
            page = int(data.split(":")[2]) if len(data.split(":")) > 2 else 1
            queue = get_queue()
            text, reply_markup = get_paginated_queue(queue, page, user_id, is_admin=True)
            await query.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        elif data == "action:payouts":
            payouts = get_payouts()
            text = MESSAGES['payouts_title'] + "<br><br>" + "<br>".join([
                f"💸 <b>ID: {p[0]}</b><br>   Пользователь: <i>@{get_user(p[1])['username']} ({p[1]})</i><br>   Сумма: <i>${p[2]}</i><br>   Статус: <i>{p[3]}</i><br>   Дата: <i>{p[4]}</i>"
                for p in payouts
            ]) if payouts else MESSAGES['no_payouts']
            await query.message.edit_text(
                text,
                reply_markup=get_admin_action_menu('payouts'),
                parse_mode='HTML'
            )
        elif data.startswith("action:tickets"):
            page = int(data.split(":")[2]) if len(data.split(":")) > 2 else 1
            tickets = get_support_tickets()
            text, reply_markup = get_paginated_tickets(tickets, page)
            await query.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        elif data.startswith("action:requests"):
            page = int(data.split(":")[2]) if len(data.split(":")) > 2 else 1
            requests = get_rent_requests()
            text, reply_markup = get_paginated_requests(requests, page)
            await query.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        elif data == "action:block":
            context.user_data['awaiting_block'] = True
            await query.message.edit_text(
                MESSAGES['block_user_prompt'],
                reply_markup=None,
                parse_mode='HTML'
            )
        elif data == "action:balance":
            context.user_data['awaiting_balance'] = True
            await query.message.edit_text(
                MESSAGES['update_balance_prompt'],
                reply_markup=None,
                parse_mode='HTML'
            )
        elif data == "action:admin_stats":
            total_users, today_numbers = get_stats()
            requests = get_rent_requests()
            tickets = get_support_tickets()
            text = MESSAGES['admin_stats'].format(
                username=username,
                total_users=total_users,
                today_numbers=today_numbers,
                total_requests=len(requests),
                total_tickets=len(tickets)
            )
            await query.message.edit_text(
                text,
                reply_markup=get_admin_menu(),
                parse_mode='HTML'
            )
        elif data == "action:create_code":
            context.user_data['awaiting_code'] = True
            await query.message.edit_text(
                MESSAGES['create_code_prompt'],
                reply_markup=None,
                parse_mode='HTML'
            )
        elif data == "action:move_archive":
            context.user_data['awaiting_archive'] = True
            await query.message.edit_text(
                MESSAGES['move_archive_prompt'],
                reply_markup=None,
                parse_mode='HTML'
            )
        elif data == "action:update_payout":
            context.user_data['awaiting_payout'] = True
            await query.message.edit_text(
                MESSAGES['update_payout_prompt'],
                reply_markup=None,
                parse_mode='HTML'
            )
        elif data == "action:respond_ticket":
            context.user_data['awaiting_ticket'] = True
            await query.message.edit_text(
                MESSAGES['respond_ticket_prompt'],
                reply_markup=None,
                parse_mode='HTML'
            )
        elif data.startswith("action:approve_request:"):
            request_id = int(data.split(":")[2])
            update_rent_request_status(request_id, 'approved')
            request = [r for r in get_rent_requests() if r[0] == request_id]
            if request:
                await context.bot.send_message(
                    chat_id=request[0][1],
                    text=MESSAGES['request_approved'].format(phone_number=request[0][2]),
                    parse_mode='HTML'
                )
            await query.message.edit_text(
                MESSAGES['request_approved_admin'].format(request_id=request_id),
                reply_markup=get_admin_menu(),
                parse_mode='HTML'
            )
        elif data.startswith("action:reject_request:"):
            request_id = int(data.split(":")[2])
            update_rent_request_status(request_id, 'rejected')
            request = [r for r in get_rent_requests() if r[0] == request_id]
            if request:
                await context.bot.send_message(
                    chat_id=request[0][1],
                    text=MESSAGES['request_rejected'].format(phone_number=request[0][2]),
                    parse_mode='HTML'
                )
            await query.message.edit_text(
                MESSAGES['request_rejected_admin'].format(request_id=request_id),
                reply_markup=get_admin_menu(),
                parse_mode='HTML'
            )
        elif data == "action:back":
            await query.message.edit_text(
                MESSAGES['admin_panel'].format(username=username),
                reply_markup=get_admin_menu(),
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Ошибка в handle_callback_query: {e}")
        await query.message.edit_text(
            MESSAGES['error'],
            reply_markup=get_admin_menu() if is_admin(user_id) else get_user_menu(),
            parse_mode='HTML'
        )