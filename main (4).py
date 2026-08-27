import asyncio
import logging
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, FSInputFile, URLInputFile, MessageEntity
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN") or "8913302857:AAG1kt8-4ADipml3SvprhcgpS_0cJzBqOY8"

MAIN_MENU_IMAGE_PATH = "https://i.ibb.co/WWjt2f9w/1000043281.jpg"

SUPPORT_USERNAME = "FunPayToBank"

OWNER_IDS = {7259247242}

LOG_GROUP_ID = -1004393528650

MOSCOW_TZ = timezone(timedelta(hours=3))

SUPPORTED_LANGUAGES = ["ru", "en", "cn"]
DEFAULT_LANGUAGE = "ru"

TRANSLATIONS = {
    "ru": {
        "welcome_title": "Fun Pay - #1 По трейдингу NFT подарков.",
        "body_text": "Покупайте и продавайте всё, что угодно – безопасно! Сделки проходят легко и без риска.",
        "wallet_line": "Удобное управление кошельками",
        "guarantee_line": "Безопасные сделки с гарантией",
        "choose_section": "Выберите нужный раздел ниже:",
        "btn_create_deal": "Создать сделку",
        "btn_wallet": "Кошелёк",
        "btn_requisites": "Управление реквизитами",
        "btn_my_deals": "Мои сделки",
        "btn_change_language": "Language",
        "btn_support": "Поддержка",
        "requisites_title": "Управление реквизитами",
        "requisites_text": "Используйте кнопки ниже чтобы добавить/изменить реквизиты",
        "btn_edit_wallet": "Добавить/изменить кошелёк",
        "btn_edit_card": "Добавить/изменить карту",
        "btn_back_to_menu": "Вернуться в меню",
        "card_add_title": "Добавьте ваши реквизиты:",
        "card_add_text": "Пожалуйста, отправьте реквизиты в таком формате:",
        "card_example": "ЕвроБанк – 1234567891012345",
        "card_current_title": "Ваши текущие реквизиты карты:",
        "card_current_text": "Отправьте новые реквизиты для изменения или нажмите кнопку ниже для возврата в меню.",
        "card_saved_confirm": "Реквизиты карты сохранены ✅",
        "blocked_message": "🚫 Вы заблокированы и не можете пользоваться ботом. Обратитесь в поддержку.",
        "btn_owner_panel": "👑 OWNER PANEL",
        "btn_admin_panel": "🛠 Админ панель",

        "panel_owner_title": "👑 OWNER PANEL",
        "panel_admin_title": "🛠 Админ панель",
        "btn_panel_give_balance": "💰 Выдать/списать баланс",
        "btn_panel_give_balance_self": "💰 Выдать/списать себе баланс",
        "btn_panel_edit_deals_count": "🏆 Изменить успешные сделки",
        "btn_panel_edit_deals_count_self": "🏆 Изменить себе успешные сделки",
        "btn_panel_edit_freeze": "❄️ Заморозка/разморозка баланса",
        "panel_ask_freeze_delta": "Введите изменение заморозки в {currency_code}. Положительное число — заморозить, отрицательное — снять заморозку (например: 100 или -50):",
        "panel_invalid_freeze_delta": "❌ Некорректное число. Введите число, например 100 или -50.",
        "panel_freeze_updated": "✅ Заморозка пользователя {target} изменена на {delta} {symbol}. Текущая заморозка: {total} {symbol}.",
        "panel_ask_deals_count_delta": "Введите изменение количества успешных сделок. Положительное число — добавить, отрицательное — убрать (например: 5 или -2):",
        "panel_invalid_deals_count_delta": "❌ Некорректное число. Введите целое число, например 5 или -2.",
        "panel_deals_count_updated": "✅ Счётчик успешных сделок пользователя {target} изменён на {delta}. Текущий итоговый счётчик: {total}.",
        "btn_panel_block": "🚫 Блокировка/разблокировка",
        "btn_panel_manage_admins": "👤 Управление админами",
        "btn_panel_stats": "📊 Статистика",
        "panel_ask_target": "Введите username (с @ или без) или user_id пользователя:",
        "panel_user_not_found": "❌ Пользователь не найден. Он должен хотя бы раз написать боту /start.",
        "panel_ask_currency": "Выберите валюту:",
        "panel_ask_amount": "Введите сумму. Положительное число — выдать, отрицательное — списать (например: 10 или -5.5):",
        "panel_invalid_amount": "❌ Некорректная сумма. Введите число, например 10 или -5.5.",
        "panel_balance_updated": "✅ Баланс пользователя {target} изменён на {delta} {symbol}. Новый баланс: {new_amount} {symbol}.",
        "panel_block_menu_title": "Кого заблокировать или разблокировать?",
        "btn_panel_block_user": "🚫 Заблокировать пользователя",
        "btn_panel_unblock_user": "✅ Разблокировать пользователя",
        "panel_blocked_done": "🚫 Пользователь {target} заблокирован.",
        "panel_unblocked_done": "✅ Пользователь {target} разблокирован.",
        "panel_admins_menu_title": "Управление админами:",
        "btn_panel_add_admin": "➕ Добавить админа",
        "btn_panel_remove_admin": "➖ Убрать админа",
        "btn_panel_list_admins": "📋 Список админов",
        "panel_admin_added": "✅ Пользователь {target} назначен админом.",
        "panel_admin_removed": "✅ Права админа у пользователя {target} сняты.",
        "panel_admins_list_empty": "Младших админов пока нет.",
        "panel_admins_list_title": "Список младших админов:",
        "panel_stats_title": "📊 Статистика бота",
        "panel_stats_total_users": "Всего пользователей",
        "panel_stats_blocked": "Заблокировано",
        "panel_stats_admins_count": "Младших админов",
        "panel_stats_balances_title": "Суммарные балансы по валютам:",
        "btn_panel_back": "⬅️ Назад",
        "panel_no_access": "⛔ У вас нет доступа к этому разделу.",
        "btn_panel_view_requisites": "🔎 Просмотр реквизитов",
        "panel_requisites_title": "Реквизиты пользователя {target}:",
        "panel_requisites_card": "💳 Карта",
        "panel_requisites_wallet": "🔍 TON-кошелёк",
        "panel_requisites_not_set": "не указано",

        "deal_create_title": "Создание сделки",
        "deal_create_ask_currency": "В какой валюте будет сделка? Выберите валюту:",
        "deal_create_ask_price": "Введите сумму {currency_code} сделки в формате: 100.5",
        "deal_create_invalid_price": "Некорректная сумма. Введите сумму {currency_code} сделки в формате: 100.5",
        "deal_create_below_minimum": "Минимальная сумма сделки — {min_amount} {currency_code}. Введите сумму не меньше этой.",
        "deal_create_need_card": "Сначала добавьте ваш номер карты перед созданием сделки.",
        "deal_create_need_wallet": "Сначала добавьте ваш кошелек перед созданием сделки.",
        "btn_back_to_main_menu": "Вернуться в меню",
        "deal_create_ask_nft_link": "Укажите ссылку на NFT:\n\nПожалуйста, отправьте ссылку на NFT\n\nПример:",
        "deal_create_nft_link_example": "t.me/nft/UFCStrike-14196",
        "deal_create_nft_link_required": "Пожалуйста, укажите ссылку на NFT — это обязательное поле.",
        "deal_created_title": "Сделка успешно создана!",
        "deal_created_amount_label": "Сумма",
        "deal_created_nft_label": "NFT",
        "deal_created_nft_view_text": "посмотреть",
        "deal_created_buyer_link_label": "Ссылка для покупателя",
        "deal_detail_description": "Описание: {description}",
        "deal_detail_nft_link": "Ссылка на NFT: {nft_link}",
        "deal_nft_name": "🎁 {name}",
        "deal_join_not_found": "❌ Сделка с таким кодом не найдена.",
        "deal_join_wrong_status": "❌ Эта сделка уже не доступна для присоединения (уже занята, отменена или завершена).",
        "deal_join_own_deal": "❌ Вы не можете присоединиться к собственной сделке.",
        "deal_join_insufficient_balance": "❌ Недостаточно средств в валюте {currency}. Ваш доступный баланс: {available} {symbol}, требуется: {price} {symbol}.",
        "deal_joined_success": "Пользователь {username}\nПрисоединился к сделке\n#{deal_id}",
        "deal_join_successful_deals_label": "· Успешные сделки: {count}",
        "deal_join_check_user_warning": "Проверьте соответствие пользователя",
        "deal_info_title": "Информация о сделке #{deal_id}",
        "deal_info_your_role_buyer": "Вы покупатель в сделке.",
        "deal_info_your_role_seller": "Вы продавец в сделке.",
        "deal_info_seller_label": "Продавец: {seller}",
        "deal_info_successful_deals_label": "· Успешные сделки: {count}",
        "deal_info_nft_label": "· NFT: {view_text}",
        "deal_info_nft_view_text": "посмотреть",
        "deal_info_payment_address_label": "Адрес для оплаты:",
        "deal_info_payment_address_card": "Реквизиты",
        "deal_info_payment_address_ton": "{address}",
        "deal_info_payment_address_stars": "Звезды будут переведены автоматически",
        "deal_info_amount_label": "Сумма к оплате: {amount} {symbol}",
        "deal_info_comment_label": "Комментарий к платежу:",
        "deal_info_manager_label": "Менеджер для передачи NFT:",
        "deal_info_warning": "Пожалуйста, убедитесь в правильности данных перед оплатой. Комментарий обязателен!",
        "btn_deal_pay": "Оплатить",
        "deal_pay_insufficient_balance": "❌ Недостаточно средств для оплаты. Доступно: {available} {symbol}, требуется: {price} {symbol}. Пополните баланс и попробуйте снова.",
        "deal_pay_wrong_status": "❌ Эту сделку уже нельзя оплатить (статус изменился).",
        "deal_pay_success_buyer_confirmed": "Оплата по вашей сделке подтверждена.",
        "deal_pay_success_buyer_wait": "Ожидайте, продавец отправит NFT менеджеру @{support_username} для безопасной передачи.",
        "deal_pay_success_buyer_wait_notify": "Ожидайте уведомления о передаче NFT.",
        "deal_pay_success_seller_title": "Оплата по вашей сделке подтверждена",
        "deal_pay_success_seller_credited": "Средства успешно зачислены на баланс и временно заблокированы до завершения сделки.",
        "deal_pay_success_seller_instruction": "Переведите подарок на аккаунт поддержки и подтвердите передачу подарка @{support_username}",
        "deal_pay_success_seller_warning": "Важно: Передача подарка на любой аккаунт, кроме @{support_username}, приведет к потере средств.",
        "btn_deal_gift_sent": "Подарок отправлен",
        "btn_deal_contact_manager": "Связаться с менеджером",
        "deal_buyer_confirm_delivery_notice": "Продавец успешно передал подарок менеджеру. Пожалуйста, подтвердите отправку, для успешного завершения сделки.",
        "btn_deal_confirm_transfer": "Подтвердить передачу",
        "deal_final_completed_message": "Сделка успешно завершена. Благодарим вас за выбор нашего сервиса и надеемся на дальнейшее сотрудничество.",
        "deal_list_empty": "У вас пока нет активных или завершенных сделок. Все будущие операции будут отображаться в этом разделе.",
        "deal_list_title": "📋 Мои сделки:",
        "deal_role_seller": "Продавец",
        "deal_role_buyer": "Покупатель",
        "deal_status_created": "⏳ Ожидает покупателя",
        "deal_status_joined": "🤝 Покупатель найден",
        "deal_status_paid": "💰 Оплачено",
        "deal_status_sent": "📦 NFT отправлен гаранту",
        "deal_status_completed": "✅ Завершена",
        "deal_status_cancelled": "🚫 Отменена",
        "deal_detail_title": "Сделка {deal_id}",
        "deal_detail_role": "Ваша роль: {role}",
        "deal_detail_price": "Цена: {price} {symbol}",
        "deal_detail_status": "Статус: {status}",
        "deal_detail_date": "Дата создания: {date}",
        "btn_deal_cancel": "Отменить сделку",
        "btn_deal_confirm_sent": "📦 Я отправил NFT гаранту",
        "btn_deal_confirm_received": "✅ Я получил подарок",
        "deal_cancel_confirm": "Вы вышли из сделки. Сделка снова доступна для других покупателей.",
        "deal_sent_seller_accepted": "Подарок успешно принят сервисом",
        "deal_sent_seller_transferred": "Передано контролирующему менеджеру.",
        "deal_sent_seller_wait_verification": "Пожалуйста, ожидайте верификации транзакции.",
        "deal_sent_seller_buyer_notified": "Покупателю отправлено системное уведомление о передаче подарка менеджеру.",
        "deal_sent_notify_buyer": "📦 Продавец отметил, что отправил NFT-подарок на аккаунт гаранта @{support_username}. Проверьте получение и подтвердите в сделке {deal_id}.",
        "deal_completed_confirm": "✅ Сделка {deal_id} завершена! Средства переведены продавцу.",
        "deal_completed_notify_seller": "✅ Покупатель подтвердил получение NFT-подарка. Сделка {deal_id} завершена, средства переведены на ваш баланс.",
        "deal_cancelled_notify_other": "{role} вышел из сделки. Сделка снова доступна для других.",
        "btn_deal_view": "Сделка {deal_id} ({status})",
        "btn_back_to_menu_simple": "Назад",
        "wallet_add_title": "Добавьте ваш кошелек:",
        "wallet_add_text": "Пожалуйста, отправьте адрес вашего кошелька типа: UQBQB43qD_zotENaeJZtSBIGkt8D2WiKD2VXvnSChqlmnMSw",
        "wallet_current_title": "Ваш текущий TON-кошелек:",
        "wallet_current_text": "Отправьте новый адрес кошелька для изменения или нажмите кнопку ниже для возврата в меню.",
        "balance_title": "Кошелёк",
        "balance_your_balance": "Ваш баланс",
        "balance_approx": "≈",
        "btn_topup": "Пополнение",
        "btn_withdraw": "Вывод",
        "withdraw_ask_currency": "Выберите валюту для вывода",
        "withdraw_zero_balance_error": "Проведение данной операции заблокировано системой из-за нулевого баланса на вашем счете.\n\nЕсли вы считаете, что это ошибка, пожалуйста, обратитесь в уполномоченную службу поддержки @{support_username}",
        "withdraw_ask_amount": "Введите сумму вывода",
        "withdraw_invalid_amount": "Некорректная сумма. Введите положительное число, например 100 или 50.5.",
        "withdraw_exceeds_balance": "Сумма превышает доступный баланс. Ваш доступный баланс: {available} {symbol}.",
        "withdraw_confirm_requisites_title": "Подтвердите актуальность реквизитов",
        "btn_withdraw_confirm": "Подтвердить",
        "btn_withdraw_change_requisites": "Изменить реквизиты",
        "withdraw_request_sent": "Заявка на вывод {amount} {symbol} принята. Ожидайте обработки.",
    },
    "en": {
        "welcome_title": "Fun Pay - #1 in NFT gift trading.",
        "body_text": "Buy and sell anything – safely! Deals go smoothly and risk-free.",
        "wallet_line": "Convenient wallet management",
        "guarantee_line": "Secure guaranteed deals",
        "choose_section": "Choose a section below:",
        "btn_create_deal": "Create a deal",
        "btn_wallet": "Wallet",
        "btn_requisites": "Manage requisites",
        "btn_my_deals": "My deals",
        "btn_change_language": "Language",
        "btn_support": "Support",
        "requisites_title": "Manage requisites",
        "requisites_text": "Use the buttons below to add/change your requisites",
        "btn_edit_wallet": "Add/change wallet",
        "btn_edit_card": "Add/change card",
        "btn_back_to_menu": "Back to menu",
        "card_add_title": "Add your requisites:",
        "card_add_text": "Please send your requisites in this format:",
        "card_example": "EuroBank – 1234567891012345",
        "card_current_title": "Your current card requisites:",
        "card_current_text": "Send new requisites to change them, or press the button below to return to the menu.",
        "card_saved_confirm": "Card requisites saved ✅",
        "blocked_message": "🚫 You are blocked and cannot use this bot. Please contact support.",
        "btn_owner_panel": "👑 OWNER PANEL",
        "btn_admin_panel": "🛠 Admin Panel",

        "panel_owner_title": "👑 OWNER PANEL",
        "panel_admin_title": "🛠 Admin Panel",
        "btn_panel_give_balance": "💰 Give/take balance",
        "btn_panel_give_balance_self": "💰 Give/take my own balance",
        "btn_panel_edit_deals_count": "🏆 Edit successful deals",
        "btn_panel_edit_deals_count_self": "🏆 Edit my successful deals",
        "btn_panel_edit_freeze": "❄️ Freeze/unfreeze balance",
        "panel_ask_freeze_delta": "Enter the freeze change in {currency_code}. Positive — freeze, negative — unfreeze (e.g. 100 or -50):",
        "panel_invalid_freeze_delta": "❌ Invalid number. Enter a number, e.g. 100 or -50.",
        "panel_freeze_updated": "✅ Freeze for {target} changed by {delta} {symbol}. Current freeze: {total} {symbol}.",
        "panel_ask_deals_count_delta": "Enter the change in the number of successful deals. Positive — add, negative — remove (e.g. 5 or -2):",
        "panel_invalid_deals_count_delta": "❌ Invalid number. Enter an integer, e.g. 5 or -2.",
        "panel_deals_count_updated": "✅ Successful deals counter for {target} changed by {delta}. Current total: {total}.",
        "btn_panel_block": "🚫 Block/unblock",
        "btn_panel_manage_admins": "👤 Manage admins",
        "btn_panel_stats": "📊 Statistics",
        "panel_ask_target": "Enter the username (with or without @) or user_id:",
        "panel_user_not_found": "❌ User not found. They must have written /start to the bot at least once.",
        "panel_ask_currency": "Choose a currency:",
        "panel_ask_amount": "Enter the amount. Positive — give, negative — take (e.g. 10 or -5.5):",
        "panel_invalid_amount": "❌ Invalid amount. Enter a number, e.g. 10 or -5.5.",
        "panel_balance_updated": "✅ Balance of {target} changed by {delta} {symbol}. New balance: {new_amount} {symbol}.",
        "panel_block_menu_title": "Who to block or unblock?",
        "btn_panel_block_user": "🚫 Block user",
        "btn_panel_unblock_user": "✅ Unblock user",
        "panel_blocked_done": "🚫 User {target} has been blocked.",
        "panel_unblocked_done": "✅ User {target} has been unblocked.",
        "panel_admins_menu_title": "Manage admins:",
        "btn_panel_add_admin": "➕ Add admin",
        "btn_panel_remove_admin": "➖ Remove admin",
        "btn_panel_list_admins": "📋 List of admins",
        "panel_admin_added": "✅ User {target} has been made an admin.",
        "panel_admin_removed": "✅ Admin rights revoked from {target}.",
        "panel_admins_list_empty": "There are no admins yet.",
        "panel_admins_list_title": "List of admins:",
        "panel_stats_title": "📊 Bot statistics",
        "panel_stats_total_users": "Total users",
        "panel_stats_blocked": "Blocked",
        "panel_stats_admins_count": "Admins",
        "panel_stats_balances_title": "Total balances by currency:",
        "btn_panel_back": "⬅️ Back",
        "panel_no_access": "⛔ You don't have access to this section.",
        "btn_panel_view_requisites": "🔎 View requisites",
        "panel_requisites_title": "Requisites of user {target}:",
        "panel_requisites_card": "💳 Card",
        "panel_requisites_wallet": "🔍 TON wallet",
        "panel_requisites_not_set": "not set",

        "deal_create_title": "Creating a deal",
        "deal_create_ask_currency": "Which currency will the deal use? Choose a currency:",
        "deal_create_ask_price": "Enter the {currency_code} amount of the deal in this format: 100.5",
        "deal_create_invalid_price": "Invalid amount. Enter the {currency_code} amount of the deal in this format: 100.5",
        "deal_create_below_minimum": "The minimum deal amount is {min_amount} {currency_code}. Enter an amount that is not lower than this.",
        "deal_create_need_card": "First add your card number before creating a deal.",
        "deal_create_need_wallet": "First add your wallet before creating a deal.",
        "btn_back_to_main_menu": "Back to menu",
        "deal_create_ask_nft_link": "Provide the NFT link:\n\nPlease send the link to the NFT\n\nExample:",
        "deal_create_nft_link_example": "t.me/nft/UFCStrike-14196",
        "deal_create_nft_link_required": "Please provide an NFT link — this field is required.",
        "deal_created_title": "Deal successfully created!",
        "deal_created_amount_label": "Amount",
        "deal_created_nft_label": "NFT",
        "deal_created_nft_view_text": "view",
        "deal_created_buyer_link_label": "Link for the buyer",
        "deal_detail_description": "Description: {description}",
        "deal_detail_nft_link": "NFT link: {nft_link}",
        "deal_nft_name": "🎁 {name}",
        "deal_join_not_found": "❌ No deal found with that code.",
        "deal_join_wrong_status": "❌ This deal is no longer available to join (already taken, cancelled, or completed).",
        "deal_join_own_deal": "❌ You can't join your own deal.",
        "deal_join_insufficient_balance": "❌ Insufficient {currency} balance. Available: {available} {symbol}, required: {price} {symbol}.",
        "deal_joined_success": "User {username}\nJoined the deal\n#{deal_id}",
        "deal_join_successful_deals_label": "· Successful deals: {count}",
        "deal_join_check_user_warning": "Please verify the user's identity",
        "deal_info_title": "Deal information #{deal_id}",
        "deal_info_your_role_buyer": "You are the buyer in this deal.",
        "deal_info_your_role_seller": "You are the seller in this deal.",
        "deal_info_seller_label": "Seller: {seller}",
        "deal_info_successful_deals_label": "· Successful deals: {count}",
        "deal_info_nft_label": "· NFT: {view_text}",
        "deal_info_nft_view_text": "view",
        "deal_info_payment_address_label": "Payment address:",
        "deal_info_payment_address_card": "Requisites",
        "deal_info_payment_address_ton": "{address}",
        "deal_info_payment_address_stars": "Stars will be transferred automatically",
        "deal_info_amount_label": "Amount to pay: {amount} {symbol}",
        "deal_info_comment_label": "Payment comment:",
        "deal_info_manager_label": "Manager for NFT transfer:",
        "deal_info_warning": "Please make sure the details are correct before paying. The comment is required!",
        "btn_deal_pay": "Pay",
        "deal_pay_insufficient_balance": "❌ Insufficient funds. Available: {available} {symbol}, required: {price} {symbol}. Top up your balance and try again.",
        "deal_pay_wrong_status": "❌ This deal can no longer be paid for (status has changed).",
        "deal_pay_success_buyer_confirmed": "Payment for your deal has been confirmed.",
        "deal_pay_success_buyer_wait": "Wait for the seller to send the NFT to the manager @{support_username} for safe transfer.",
        "deal_pay_success_buyer_wait_notify": "Wait for the notification about the NFT transfer.",
        "deal_pay_success_seller_title": "Payment for your deal has been confirmed",
        "deal_pay_success_seller_credited": "Funds have been successfully credited to your balance and are temporarily frozen until the deal is completed.",
        "deal_pay_success_seller_instruction": "Transfer the gift to the support account and confirm the transfer @{support_username}",
        "deal_pay_success_seller_warning": "Important: Transferring the gift to any account other than @{support_username} will result in loss of funds.",
        "btn_deal_gift_sent": "Gift sent",
        "btn_deal_contact_manager": "Contact manager",
        "deal_buyer_confirm_delivery_notice": "The seller has successfully handed over the gift to the manager. Please confirm receipt to complete the deal successfully.",
        "btn_deal_confirm_transfer": "Confirm transfer",
        "deal_final_completed_message": "The deal has been successfully completed. Thank you for choosing our service, we hope for further cooperation.",
        "deal_list_empty": "You don't have any active or completed deals yet. All future operations will be displayed in this section.",
        "deal_list_title": "📋 My deals:",
        "deal_role_seller": "Seller",
        "deal_role_buyer": "Buyer",
        "deal_status_created": "⏳ Waiting for buyer",
        "deal_status_joined": "🤝 Buyer found",
        "deal_status_paid": "💰 Paid",
        "deal_status_sent": "📦 NFT sent to guarantor",
        "deal_status_completed": "✅ Completed",
        "deal_status_cancelled": "🚫 Cancelled",
        "deal_detail_title": "Deal {deal_id}",
        "deal_detail_role": "Your role: {role}",
        "deal_detail_price": "Price: {price} {symbol}",
        "deal_detail_status": "Status: {status}",
        "deal_detail_date": "Created: {date}",
        "btn_deal_cancel": "Cancel deal",
        "btn_deal_confirm_sent": "📦 I sent the NFT to the guarantor",
        "btn_deal_confirm_received": "✅ I received the gift",
        "deal_cancel_confirm": "You left the deal. The deal is available for other buyers again.",
        "deal_sent_seller_accepted": "Gift successfully accepted by the service",
        "deal_sent_seller_transferred": "Transferred to the supervising manager.",
        "deal_sent_seller_wait_verification": "Please wait for transaction verification.",
        "deal_sent_seller_buyer_notified": "The buyer has been sent a system notification about the gift transfer to the manager.",
        "deal_sent_notify_buyer": "📦 The seller marked the NFT gift as sent to the guarantor account @{support_username}. Check it and confirm in deal {deal_id}.",
        "deal_completed_confirm": "✅ Deal {deal_id} completed! Funds transferred to the seller.",
        "deal_completed_notify_seller": "✅ The buyer confirmed receiving the NFT gift. Deal {deal_id} is completed, funds transferred to your balance.",
        "deal_cancelled_notify_other": "{role} left the deal. The deal is available for others again.",
        "btn_deal_view": "Deal {deal_id} ({status})",
        "btn_back_to_menu_simple": "Back",
        "wallet_add_title": "Add your wallet:",
        "wallet_add_text": "Please send your wallet address, e.g.: UQBQB43qD_zotENaeJZtSBIGkt8D2WiKD2VXvnSChqlmnMSw",
        "wallet_current_title": "Your current TON wallet:",
        "wallet_current_text": "Send a new wallet address to change it, or press the button below to return to the menu.",
        "balance_title": "Wallet",
        "balance_your_balance": "Your balance",
        "balance_approx": "≈",
        "btn_topup": "Top-up",
        "btn_withdraw": "Withdrawal",
        "withdraw_ask_currency": "Choose a currency for withdrawal",
        "withdraw_zero_balance_error": "This operation has been blocked by the system due to a zero balance on your account.\n\nIf you believe this is a mistake, please contact our official support @{support_username}",
        "withdraw_ask_amount": "Enter the withdrawal amount",
        "withdraw_invalid_amount": "Invalid amount. Enter a positive number, e.g. 100 or 50.5.",
        "withdraw_exceeds_balance": "The amount exceeds your available balance. Available: {available} {symbol}.",
        "withdraw_confirm_requisites_title": "Please confirm your requisites are up to date",
        "btn_withdraw_confirm": "Confirm",
        "btn_withdraw_change_requisites": "Change requisites",
        "withdraw_request_sent": "Withdrawal request for {amount} {symbol} accepted. Please wait for processing.",
    },
    "cn": {
        "welcome_title": "Fun Pay - NFT礼品交易第一平台。",
        "body_text": "安全买卖任何物品！交易简单无风险。",
        "wallet_line": "便捷的钱包管理",
        "guarantee_line": "安全担保交易",
        "choose_section": "请选择下方所需的板块：",
        "btn_create_deal": "创建交易",
        "btn_wallet": "钱包",
        "btn_requisites": "管理收款信息",
        "btn_my_deals": "我的交易",
        "btn_change_language": "Language",
        "btn_support": "客服支持",
        "requisites_title": "管理收款信息",
        "requisites_text": "请使用下方按钮添加/修改您的收款信息",
        "btn_edit_wallet": "添加/修改钱包",
        "btn_edit_card": "添加/修改银行卡",
        "btn_back_to_menu": "返回菜单",
        "card_add_title": "添加您的收款信息：",
        "card_add_text": "请按以下格式发送您的收款信息：",
        "card_example": "欧洲银行 – 1234567891012345",
        "card_current_title": "您当前的银行卡信息：",
        "card_current_text": "发送新信息以修改，或点击下方按钮返回菜单。",
        "card_saved_confirm": "银行卡信息已保存 ✅",
        "blocked_message": "🚫 您已被封禁，无法使用此机器人。请联系客服。",
        "btn_owner_panel": "👑 OWNER PANEL",
        "btn_admin_panel": "🛠 管理员面板",

        "panel_owner_title": "👑 OWNER PANEL",
        "panel_admin_title": "🛠 管理员面板",
        "btn_panel_give_balance": "💰 增加/扣除余额",
        "btn_panel_give_balance_self": "💰 增加/扣除我的余额",
        "btn_panel_edit_deals_count": "🏆 修改成功交易数",
        "btn_panel_edit_deals_count_self": "🏆 修改我的成功交易数",
        "btn_panel_edit_freeze": "❄️ 冻结/解冻余额",
        "panel_ask_freeze_delta": "请输入{currency_code}的冻结变化量。正数为冻结，负数为解冻（例如：100 或 -50）：",
        "panel_invalid_freeze_delta": "❌ 数字无效。请输入数字，例如 100 或 -50。",
        "panel_freeze_updated": "✅ 用户 {target} 的冻结金额已变更 {delta} {symbol}。当前冻结：{total} {symbol}。",
        "panel_ask_deals_count_delta": "请输入成功交易数的变化量。正数为增加，负数为减少（例如：5 或 -2）：",
        "panel_invalid_deals_count_delta": "❌ 数字无效。请输入整数，例如 5 或 -2。",
        "panel_deals_count_updated": "✅ 用户 {target} 的成功交易计数器已变更 {delta}。当前总计：{total}。",
        "btn_panel_block": "🚫 封禁/解封",
        "btn_panel_manage_admins": "👤 管理员管理",
        "btn_panel_stats": "📊 统计数据",
        "panel_ask_target": "请输入用户名（带@或不带）或user_id：",
        "panel_user_not_found": "❌ 未找到该用户。该用户必须至少向机器人发送过一次 /start。",
        "panel_ask_currency": "请选择货币：",
        "panel_ask_amount": "请输入金额。正数为增加，负数为扣除（例如：10 或 -5.5）：",
        "panel_invalid_amount": "❌ 金额无效。请输入数字，例如 10 或 -5.5。",
        "panel_balance_updated": "✅ 用户 {target} 的余额已变更 {delta} {symbol}。新余额：{new_amount} {symbol}。",
        "panel_block_menu_title": "要封禁还是解封谁？",
        "btn_panel_block_user": "🚫 封禁用户",
        "btn_panel_unblock_user": "✅ 解封用户",
        "panel_blocked_done": "🚫 用户 {target} 已被封禁。",
        "panel_unblocked_done": "✅ 用户 {target} 已解封。",
        "panel_admins_menu_title": "管理员管理：",
        "btn_panel_add_admin": "➕ 添加管理员",
        "btn_panel_remove_admin": "➖ 移除管理员",
        "btn_panel_list_admins": "📋 管理员列表",
        "panel_admin_added": "✅ 用户 {target} 已被设为管理员。",
        "panel_admin_removed": "✅ 已撤销 {target} 的管理员权限。",
        "panel_admins_list_empty": "暂无管理员。",
        "panel_admins_list_title": "管理员列表：",
        "panel_stats_title": "📊 机器人统计",
        "panel_stats_total_users": "用户总数",
        "panel_stats_blocked": "已封禁",
        "panel_stats_admins_count": "管理员数量",
        "panel_stats_balances_title": "各货币总余额：",
        "btn_panel_back": "⬅️ 返回",
        "panel_no_access": "⛔ 您没有权限访问此部分。",
        "btn_panel_view_requisites": "🔎 查看收款信息",
        "panel_requisites_title": "用户 {target} 的收款信息：",
        "panel_requisites_card": "💳 银行卡",
        "panel_requisites_wallet": "🔍 TON钱包",
        "panel_requisites_not_set": "未设置",

        "deal_create_title": "创建交易",
        "deal_create_ask_currency": "交易使用哪种货币？请选择货币：",
        "deal_create_ask_price": "请按以下格式输入交易的{currency_code}金额：100.5",
        "deal_create_invalid_price": "金额无效。请按以下格式输入交易的{currency_code}金额：100.5",
        "deal_create_below_minimum": "交易最低金额为 {min_amount} {currency_code}。请输入不低于此金额的数字。",
        "deal_create_need_card": "请先添加您的银行卡号，然后再创建交易。",
        "deal_create_need_wallet": "请先添加您的钱包，然后再创建交易。",
        "btn_back_to_main_menu": "返回菜单",
        "deal_create_ask_nft_link": "请提供NFT链接：\n\n请发送NFT的链接\n\n示例：",
        "deal_create_nft_link_example": "t.me/nft/UFCStrike-14196",
        "deal_create_nft_link_required": "请提供NFT链接——此字段为必填项。",
        "deal_created_title": "交易已成功创建！",
        "deal_created_amount_label": "金额",
        "deal_created_nft_label": "NFT",
        "deal_created_nft_view_text": "查看",
        "deal_created_buyer_link_label": "买家链接",
        "deal_detail_description": "描述：{description}",
        "deal_detail_nft_link": "NFT链接：{nft_link}",
        "deal_nft_name": "🎁 {name}",
        "deal_join_not_found": "❌ 未找到该代码对应的交易。",
        "deal_join_wrong_status": "❌ 该交易已不可加入（已被占用、已取消或已完成）。",
        "deal_join_own_deal": "❌ 您不能加入自己创建的交易。",
        "deal_join_insufficient_balance": "❌ {currency} 余额不足。可用余额：{available} {symbol}，需要：{price} {symbol}。",
        "deal_joined_success": "用户 {username}\n已加入交易\n#{deal_id}",
        "deal_join_successful_deals_label": "· 成功交易数：{count}",
        "deal_join_check_user_warning": "请核实用户身份",
        "deal_info_title": "交易信息 #{deal_id}",
        "deal_info_your_role_buyer": "您是该交易的买家。",
        "deal_info_your_role_seller": "您是该交易的卖家。",
        "deal_info_seller_label": "卖家：{seller}",
        "deal_info_successful_deals_label": "· 成功交易数：{count}",
        "deal_info_nft_label": "· NFT：{view_text}",
        "deal_info_nft_view_text": "查看",
        "deal_info_payment_address_label": "付款地址：",
        "deal_info_payment_address_card": "收款信息",
        "deal_info_payment_address_ton": "{address}",
        "deal_info_payment_address_stars": "Stars将自动转账",
        "deal_info_amount_label": "应付金额：{amount} {symbol}",
        "deal_info_comment_label": "付款备注：",
        "deal_info_manager_label": "NFT转交经理：",
        "deal_info_warning": "付款前请确认信息无误。备注为必填项！",
        "btn_deal_pay": "付款",
        "deal_pay_insufficient_balance": "❌ 余额不足。可用：{available} {symbol}，需要：{price} {symbol}。请充值后重试。",
        "deal_pay_wrong_status": "❌ 该交易已无法付款（状态已变更）。",
        "deal_pay_success_buyer_confirmed": "您的交易付款已确认。",
        "deal_pay_success_buyer_wait": "请等待卖家将NFT发送给经理 @{support_username} 进行安全转交。",
        "deal_pay_success_buyer_wait_notify": "请等待NFT转交通知。",
        "deal_pay_success_seller_title": "您的交易付款已确认",
        "deal_pay_success_seller_credited": "资金已成功存入您的余额，并在交易完成前暂时冻结。",
        "deal_pay_success_seller_instruction": "请将礼物转交至客服账户并确认转交 @{support_username}",
        "deal_pay_success_seller_warning": "重要提示：将礼物转交至除 @{support_username} 以外的任何账户都将导致资金损失。",
        "btn_deal_gift_sent": "礼物已发送",
        "btn_deal_contact_manager": "联系经理",
        "deal_buyer_confirm_delivery_notice": "卖家已成功将礼物转交给经理。请确认收货，以成功完成交易。",
        "btn_deal_confirm_transfer": "确认转交",
        "deal_final_completed_message": "交易已成功完成。感谢您选择我们的服务，期待进一步合作。",
        "deal_list_empty": "您目前还没有任何进行中或已完成的交易。未来所有操作都将显示在此板块中。",
        "deal_list_title": "📋 我的交易：",
        "deal_role_seller": "卖家",
        "deal_role_buyer": "买家",
        "deal_status_created": "⏳ 等待买家",
        "deal_status_joined": "🤝 已找到买家",
        "deal_status_paid": "💰 已付款",
        "deal_status_sent": "📦 NFT已发送给担保人",
        "deal_status_completed": "✅ 已完成",
        "deal_status_cancelled": "🚫 已取消",
        "deal_detail_title": "交易 {deal_id}",
        "deal_detail_role": "您的角色：{role}",
        "deal_detail_price": "价格：{price} {symbol}",
        "deal_detail_status": "状态：{status}",
        "deal_detail_date": "创建时间：{date}",
        "btn_deal_cancel": "取消交易",
        "btn_deal_confirm_sent": "📦 我已将NFT发送给担保人",
        "btn_deal_confirm_received": "✅ 我已收到礼物",
        "deal_cancel_confirm": "您已退出交易。该交易已重新对其他买家开放。",
        "deal_sent_seller_accepted": "礼物已被服务成功接收",
        "deal_sent_seller_transferred": "已转交给监管经理。",
        "deal_sent_seller_wait_verification": "请等待交易验证。",
        "deal_sent_seller_buyer_notified": "已向买家发送有关礼物转交经理的系统通知。",
        "deal_sent_notify_buyer": "📦 卖家已标记NFT礼物已发送至担保人账户 @{support_username}。请查收并在交易 {deal_id} 中确认。",
        "deal_completed_confirm": "✅ 交易 {deal_id} 已完成！资金已转给卖家。",
        "deal_completed_notify_seller": "✅ 买家已确认收到NFT礼物。交易 {deal_id} 已完成，资金已转入您的余额。",
        "deal_cancelled_notify_other": "{role}已退出交易。该交易已重新对其他人开放。",
        "btn_deal_view": "交易 {deal_id}（{status}）",
        "btn_back_to_menu_simple": "返回",
        "wallet_add_title": "添加您的钱包：",
        "wallet_add_text": "请发送您的钱包地址，例如：UQBQB43qD_zotENaeJZtSBIGkt8D2WiKD2VXvnSChqlmnMSw",
        "wallet_current_title": "您当前的TON钱包：",
        "wallet_current_text": "发送新的钱包地址以修改，或点击下方按钮返回菜单。",
        "balance_title": "钱包",
        "balance_your_balance": "您的余额",
        "balance_approx": "≈",
        "btn_topup": "充值",
        "btn_withdraw": "提现",
        "withdraw_ask_currency": "请选择提现货币",
        "withdraw_zero_balance_error": "由于您账户余额为零，系统已阻止此操作。\n\n如果您认为这是错误，请联系官方客服 @{support_username}",
        "withdraw_ask_amount": "请输入提现金额",
        "withdraw_invalid_amount": "金额无效。请输入正数，例如 100 或 50.5。",
        "withdraw_exceeds_balance": "金额超过您的可用余额。可用余额：{available} {symbol}。",
        "withdraw_confirm_requisites_title": "请确认您的收款信息是最新的",
        "btn_withdraw_confirm": "确认",
        "btn_withdraw_change_requisites": "修改收款信息",
        "withdraw_request_sent": "提现 {amount} {symbol} 的申请已受理。请等待处理。",
    },
}


def t(lang: str, key: str) -> str:
    """Получить перевод по ключу. Если язык/ключ не найден — fallback на русский."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["ru"])
    return lang_dict.get(key, TRANSLATIONS["ru"].get(key, key))


CUSTOM_EMOJI = {
    "heart": ("5951665890079544884", "️✅"),
    "store": ("5983399041197675256", "🏪"),
    "wallet": ("5769403330761593044", "👛"),
    "shield": ("5931409969613116639", "🛡"),
    "arrow_down": ("5886451926995833684", "⬇️"),
    "btn_create_deal": ("5879841310902324730", "✏️"),
    "btn_my_deals": ("5956561916573782596", "📄"),
    "btn_support": ("5897488197650223178", "📞"),
    "btn_requisites": ("5927169041595634481", "💳"),
    "btn_change_language": ("5879585266426973039", "🌐"),
    "btn_back": ("5877536313623711363", "⬅️"),
    "envelope": ("5927169041595634481", "📩"),
    "diamond": ("5778546023349621090", "💎"),
    "wallet_search": ("5778546023349621090", "🔍"),
    "down_arrow_small": ("5875008416132370818", "🔽"),
    "btn_topup": ("5366431056461312678", "🙏"),
    "btn_withdraw": ("5258332798409783582", "🚀"),
    "deal_create_envelope": ("5877465816030515018", "🔗"),
    "deal_create_link": ("5877465816030515018", "🔗"),
    "deal_create_coin": ("5992430854909989581", "🪙"),
    "deal_create_gift": ("6032937473162614352", "🎁"),
    "deal_cancel_x": ("5778527486270770928", "❌"),
    "deal_join_warning": ("5447644880824181073", "⚠️"),
    "deal_join_info": ("5877597667231534929", "🗒"),
    "deal_join_seller_pin": ("5796440171364749940", "📌"),
    "deal_join_ton_diamond": ("5807499888245612254", "💎"),
    "deal_join_amount": ("5987880246865565644", "💰"),
    "deal_join_comment_pen": ("5985774024968379294", "🖊"),
    "deal_pay_confirm": ("5776375003280838798", "✅"),
    "deal_paid_check": ("5825794181183836432", "✔️"),
    "deal_paid_clock": ("5776213190387961618", "🕓"),
    "deal_paid_seller_person": ("5954175920506933873", "👤"),
    "deal_paid_seller_warning": ("5881702736843511327", "⚠️"),
    "balance_frozen_snow": ("5449449325434266744", "❄️"),
    "deal_confirm_transfer_plus": ("5775937998948404844", "➕"),
    "deal_sent_seller_person": ("5877530150345641603", "👤"),
    "deal_list_empty_x": ("5967355281057779430", "❌"),
}

CURRENCIES = {
    "rub": {"emoji": "🇷🇺", "name": {"ru": "Российский рубль", "en": "Russian Ruble", "cn": "俄罗斯卢布"}, "code": "RUB",
            "symbol": "₽", "rub_rate": 1.0},
    "usd": {"emoji": "🇺🇸", "name": {"ru": "Доллар США", "en": "US Dollar", "cn": "美元"}, "code": "USD", "symbol": "$",
            "rub_rate": 73.5},
    "eur": {"emoji": "🇪🇺", "name": {"ru": "Евро", "en": "Euro", "cn": "欧元"}, "code": "EUR", "symbol": "€",
            "rub_rate": 84.0},
    "uah": {"emoji": "🇺🇦", "name": {"ru": "Украинская гривна", "en": "Ukrainian Hryvnia", "cn": "乌克兰格里夫纳"},
            "code": "UAH", "symbol": "₴", "rub_rate": 1.8},
    "kzt": {"emoji": "🇰🇿", "name": {"ru": "Казахстанский тенге", "en": "Kazakhstani Tenge", "cn": "哈萨克斯坦坚戈"},
            "code": "KZT", "symbol": "₸", "rub_rate": 0.14},
    "byn": {"emoji": "🇧🇾", "name": {"ru": "Белорусский рубль", "en": "Belarusian Ruble", "cn": "白俄罗斯卢布"},
            "code": "BYN", "symbol": "Br", "rub_rate": 23.0},
    "cny": {"emoji": "🇨🇳", "name": {"ru": "Китайский юань", "en": "Chinese Yuan", "cn": "人民币"}, "code": "CNY",
            "symbol": "¥", "rub_rate": 10.8},
    "ton": {"emoji": "💎", "name": {"ru": "TON", "en": "TON", "cn": "TON"}, "code": "TON", "symbol": "TON",
            "rub_rate": 250.0},
    "stars": {"emoji": "⭐", "name": {"ru": "Telegram Stars", "en": "Telegram Stars", "cn": "Telegram Stars"},
              "code": "STARS", "symbol": "⭐", "rub_rate": 1.5},
    "azn": {"emoji": "🇦🇿", "name": {"ru": "Азербайджанский манат", "en": "Azerbaijani Manat", "cn": "阿塞拜疆马纳特"},
            "code": "AZN", "symbol": "₼", "rub_rate": 43.0},
    "amd": {"emoji": "🇦🇲", "name": {"ru": "Армянский драм", "en": "Armenian Dram", "cn": "亚美尼亚德拉姆"},
            "code": "AMD", "symbol": "֏", "rub_rate": 0.19},
    "kgs": {"emoji": "🇰🇬", "name": {"ru": "Киргизский сом", "en": "Kyrgyzstani Som", "cn": "吉尔吉斯斯坦索姆"},
            "code": "KGS", "symbol": "сом", "rub_rate": 0.84},
    "mdl": {"emoji": "🇲🇩", "name": {"ru": "Молдавский лей", "en": "Moldovan Leu", "cn": "摩尔多瓦列伊"}, "code": "MDL",
            "symbol": "L", "rub_rate": 4.2},
    "tjs": {"emoji": "🇹🇯", "name": {"ru": "Таджикский сомони", "en": "Tajikistani Somoni", "cn": "塔吉克斯坦索莫尼"},
            "code": "TJS", "symbol": "смн", "rub_rate": 6.9},
    "uzs": {"emoji": "🇺🇿", "name": {"ru": "Узбекский сум", "en": "Uzbekistani Som", "cn": "乌兹别克斯坦索姆"},
            "code": "UZS", "symbol": "сум", "rub_rate": 0.0058},
    "jpy": {"emoji": "🇯🇵", "name": {"ru": "Японская иена", "en": "Japanese Yen", "cn": "日元"}, "code": "JPY",
            "symbol": "¥", "rub_rate": 0.49},
    "krw": {"emoji": "🇰🇷", "name": {"ru": "Южнокорейская вона", "en": "South Korean Won", "cn": "韩元"}, "code": "KRW",
            "symbol": "₩", "rub_rate": 0.053},
    "inr": {"emoji": "🇮🇳", "name": {"ru": "Индийская рупия", "en": "Indian Rupee", "cn": "印度卢比"}, "code": "INR",
            "symbol": "₹", "rub_rate": 0.86},
}

CURRENCY_ORDER = list(CURRENCIES.keys())

CURRENCIES_PER_PAGE = 9

MIN_DEAL_AMOUNT_RUB = 200.0


def get_min_deal_amount(currency: str) -> float:
    """
    Возвращает минимально допустимую сумму сделки в указанной валюте —
    эквивалент MIN_DEAL_AMOUNT_RUB рублей, пересчитанный по rub_rate этой
    валюты. Используется при создании сделки, чтобы продавец не мог
    выставить сумму ниже разумного порога ни в одной из 18 валют.
    """
    rate = CURRENCIES[currency]["rub_rate"]
    if rate <= 0:
        return MIN_DEAL_AMOUNT_RUB
    return MIN_DEAL_AMOUNT_RUB / rate


def convert(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Конвертирует сумму из одной валюты в другую через RUB как общую базу.
    Сейчас все rub_rate (кроме самого RUB) равны 0.0, поэтому результат
    конвертации в любую валюту, кроме RUB, всегда 0.0 — это ожидаемо до
    подключения реальных курсов.
    """
    if from_currency == to_currency:
        return amount
    from_rate = CURRENCIES[from_currency]["rub_rate"]
    to_rate = CURRENCIES[to_currency]["rub_rate"]
    amount_rub = amount * from_rate
    return amount_rub / to_rate if to_rate else 0.0


def _utf16_len(s: str) -> int:
    """Длина строки в UTF-16 code units — именно так Telegram считает offset/length."""
    return len(s.encode("utf-16-le")) // 2


class EntityBuilder:
    """
    Помогает собирать текст вместе со списком MessageEntity (custom emoji, bold,
    blockquote), отслеживая текущую позицию в UTF-16 code units. Используется
    для каждого раздела бота (главное меню, реквизиты, и т.д.), чтобы не
    дублировать логику подсчёта offset/length в каждой функции отдельно.
    """

    def __init__(self) -> None:
        self.text = ""
        self.entities: list[MessageEntity] = []
        self.cursor = 0

    def add_text(self, s: str) -> None:
        """Просто добавляет текст без entity, сдвигая курсор."""
        self.text += s
        self.cursor += _utf16_len(s)

    def add_custom_emoji(self, key: str) -> None:
        """Добавляет fallback-emoji в текст и регистрирует на него custom_emoji entity."""
        emoji_id, fallback = CUSTOM_EMOJI[key]
        self.entities.append(
            MessageEntity(
                type="custom_emoji",
                offset=self.cursor,
                length=_utf16_len(fallback),
                custom_emoji_id=emoji_id,
            )
        )
        self.add_text(fallback)

    def start_span(self) -> int:
        """Запоминает текущую позицию — используется для bold/blockquote диапазонов."""
        return self.cursor

    def close_span(self, entity_type: str, start: int, url: str | None = None) -> None:
        """
        Закрывает диапазон, начатый в start, оборачивая его в entity нужного типа.
        url нужен только для entity_type="text_link" (кликабельный текст-ссылка) —
        для остальных типов (bold, code, blockquote и т.д.) просто игнорируется.
        """
        kwargs = {"type": entity_type, "offset": start, "length": self.cursor - start}
        if url is not None:
            kwargs["url"] = url
        self.entities.append(MessageEntity(**kwargs))

    def result(self) -> tuple[str, list[MessageEntity]]:
        return self.text, self.entities


def build_welcome_content(lang: str) -> tuple[str, list[MessageEntity]]:
    """
    Собирает текст подписи к фото вместе со списком entities:
    - bold для заголовка
    - custom emoji перед нужными фразами (работают одинаково для ru/en/cn —
      это визуальные иконки, не зависят от языка текста)
    - blockquote (жёлтая рамка) на блоке "кошельки / гарантия"
    """
    title = t(lang, "welcome_title")
    body = t(lang, "body_text")
    wallet_line = t(lang, "wallet_line")
    guarantee_line = t(lang, "guarantee_line")
    choose = t(lang, "choose_section")

    b = EntityBuilder()

    b.add_custom_emoji("heart")
    b.add_text(" ")

    bold_start = b.start_span()
    b.add_text(title)
    b.close_span("bold", bold_start)
    b.add_text("\n\n")

    b.add_custom_emoji("store")
    b.add_text(f" {body}\n\n")

    blockquote_start = b.start_span()

    b.add_custom_emoji("wallet")
    b.add_text(f" {wallet_line}\n")

    b.add_custom_emoji("shield")
    b.add_text(f" {guarantee_line}")

    b.close_span("blockquote", blockquote_start)
    b.add_text("\n\n")

    b.add_custom_emoji("arrow_down")
    b.add_text(f" {choose}")

    return b.result()


def build_requisites_content(lang: str) -> tuple[str, list[MessageEntity]]:
    """
    Собирает текст для раздела "Управление реквизитами":
    📩 (custom emoji) + bold-заголовок, затем обычный текст-инструкция.
    """
    title = t(lang, "requisites_title")
    text = t(lang, "requisites_text")

    b = EntityBuilder()

    b.add_custom_emoji("envelope")
    b.add_text(" ")

    bold_start = b.start_span()
    b.add_text(title)
    b.close_span("bold", bold_start)
    b.add_text("\n\n")

    b.add_text(text)
    b.add_text(" ")
    b.add_custom_emoji("down_arrow_small")

    return b.result()


def build_language_content() -> tuple[str, list[MessageEntity]]:
    """
    Собирает текст для экрана выбора языка:
    🌐 (custom emoji) + bold-заголовок "Language", затем текст-инструкция.
    Заголовок не зависит от текущего языка интерфейса — кнопка "Language"
    везде выглядит одинаково, поэтому и сам экран всегда на этом же названии.
    """
    title = "Language"
    text = "Choose your language / Выберите язык / 选择语言"

    b = EntityBuilder()

    b.add_custom_emoji("btn_change_language")
    b.add_text(" ")

    bold_start = b.start_span()
    b.add_text(title)
    b.close_span("bold", bold_start)
    b.add_text("\n\n")

    b.add_text(text)

    return b.result()


def build_card_add_content(lang: str) -> tuple[str, list[MessageEntity]]:
    """
    Экран "Добавьте ваши реквизиты" — когда у пользователя ещё нет сохранённой карты.
    💳 (custom emoji) + bold-заголовок, текст-инструкция и пример формата.
    """
    title = t(lang, "card_add_title")
    text = t(lang, "card_add_text")
    example = t(lang, "card_example")

    b = EntityBuilder()

    b.add_custom_emoji("btn_requisites")
    b.add_text(" ")

    bold_start = b.start_span()
    b.add_text(title)
    b.close_span("bold", bold_start)
    b.add_text("\n\n")

    b.add_text(f"{text}\n{example}")

    return b.result()


def build_card_current_content(lang: str, requisites: str) -> tuple[str, list[MessageEntity]]:
    """
    Экран "Ваши текущие реквизиты карты: ..." — когда карта уже сохранена.
    💳 (custom emoji) + bold-заголовок с самими реквизитами, затем текст-инструкция.
    """
    title = t(lang, "card_current_title")
    text = t(lang, "card_current_text")

    b = EntityBuilder()

    b.add_custom_emoji("btn_requisites")
    b.add_text(" ")

    bold_start = b.start_span()
    b.add_text(f"{title} {requisites}")
    b.close_span("bold", bold_start)
    b.add_text("\n\n")

    b.add_text(text)

    return b.result()


def build_wallet_add_content(lang: str) -> tuple[str, list[MessageEntity]]:
    """
    Экран "Добавьте ваш кошелек" — когда у пользователя ещё нет сохранённого адреса.
    🔍 (custom emoji) + bold-заголовок, затем текст-инструкция с примером формата адреса.
    """
    title = t(lang, "wallet_add_title")
    text = t(lang, "wallet_add_text")

    b = EntityBuilder()

    b.add_custom_emoji("wallet_search")
    b.add_text(" ")

    bold_start = b.start_span()
    b.add_text(title)
    b.close_span("bold", bold_start)
    b.add_text("\n\n")

    b.add_text(text)

    return b.result()


def build_wallet_current_content(lang: str, address: str) -> tuple[str, list[MessageEntity]]:
    """
    Экран "Ваш текущий TON-кошелек: ..." — когда адрес уже сохранён.
    🔍 (custom emoji) + bold-заголовок с самим адресом, затем текст-инструкция.
    """
    title = t(lang, "wallet_current_title")
    text = t(lang, "wallet_current_text")

    b = EntityBuilder()

    b.add_custom_emoji("wallet_search")
    b.add_text(" ")

    bold_start = b.start_span()
    b.add_text(f"{title} {address}")
    b.close_span("bold", bold_start)
    b.add_text("\n\n")

    b.add_text(text)

    return b.result()


def format_amount(amount: float) -> str:
    """Форматирует число баланса с одним знаком после запятой (0.0, 12.5, ...)."""
    return f"{amount:.1f}"


def currency_name(info: dict, lang: str) -> str:
    """Возвращает название валюты на нужном языке (fallback на русский, если перевода нет)."""
    return info["name"].get(lang, info["name"]["ru"])


def build_balance_content(lang: str, currency: str, amount: float, user_id: int | None = None) -> tuple[
    str, list[MessageEntity]]:
    """
    Собирает экран "Кошелёк" для ОДНОЙ выбранной валюты — флаг страны
    + её название в заголовке, затем "Ваш баланс: <число> <символ валюты>".
    Возле самого баланса используется именно символ/сокращение валюты (₽, $, €,
    сом, Br и т.д.), а не флаг — флаг там был бы избыточен и менее информативен.
    Переключение между остальными 17 валютами идёт через кнопки клавиатуры
    (balance_keyboard), а не на этом же экране — поэтому здесь только один баланс.

    Если у пользователя (user_id) есть замороженные средства хоть в одной из
    18 валют, рядом с символом валюты добавляется ❄️ — глобальный индикатор
    "есть незавершённая сделка с заморозкой", независимо от того, какую
    валюту он сейчас смотрит.
    """
    info = CURRENCIES[currency]
    your_balance = t(lang, "balance_your_balance")
    name = currency_name(info, lang)

    title = name if name == info["code"] else f"{name} ({info['code']})"

    b = EntityBuilder()

    b.add_text(f"{info['emoji']} ")

    bold_start = b.start_span()
    b.add_text(title)
    b.close_span("bold", bold_start)
    b.add_text("\n\n")

    b.add_text(f"{your_balance}:\n{format_amount(amount)} {info['symbol']}")
    if user_id is not None and has_any_frozen_balance(user_id):
        b.add_text(" ")
        b.add_custom_emoji("balance_frozen_snow")

    return b.result()


def prepend_text_to_caption(prefix: str, caption: str, entities: list[MessageEntity]) -> tuple[
    str, list[MessageEntity]]:
    """
    Добавляет prefix перед уже готовым (caption, entities) — например, перед
    карточкой сделки, в которой entities посчитаны для текста "как есть".
    Просто склеить строки через f-string нельзя: офсеты в entities тогда
    указывали бы на неправильные места в новом более длинном тексте. Эта
    функция сдвигает offset каждой entity на длину prefix в UTF-16 code units.
    """
    shift = _utf16_len(prefix)
    shifted_entities = []
    for e in entities:
        kwargs = {"type": e.type, "offset": e.offset + shift, "length": e.length}
        custom_emoji_id = getattr(e, "custom_emoji_id", None)
        url = getattr(e, "url", None)
        if custom_emoji_id is not None:
            kwargs["custom_emoji_id"] = custom_emoji_id
        if url is not None:
            kwargs["url"] = url
        shifted_entities.append(MessageEntity(**kwargs))
    return prefix + caption, shifted_entities


def build_simple_title_content(text: str, emoji: str = "") -> tuple[str, list[MessageEntity]]:
    """
    Универсальный построитель простого текста для экранов панели администрирования
    (запрос ввода, подтверждение, список и т.д.) —unicode-emoji (если передан)
    перед первой строкой текста, без bold и без custom emoji entities (это
    служебные технические экраны, не основной пользовательский интерфейс).
    Поддерживает многострочный текст as-is.
    """
    b = EntityBuilder()
    if emoji:
        b.add_text(f"{emoji} ")
    b.add_text(text)
    return b.result()


def build_deal_creation_step_content(lang: str, step_text: str, is_error: bool = False) -> tuple[
    str, list[MessageEntity]]:
    """
    Собирает экран одного шага создания сделки — постоянный bold-заголовок
    "✏️ Создание сделки" (тот же на каждом шаге, как на эталонных скринах),
    затем конкретный вопрос текущего шага (валюта/сумма/ссылка на NFT).

    is_error=True добавляет premium-крестик (тот же, что на кнопке "Отменить
    сделку") перед текстом — используется при показе ошибок ввода (неверная
    сумма, сумма ниже минимума, не указана ссылка на NFT), вместо обычного
    unicode ❌.
    """
    b = EntityBuilder()
    b.add_custom_emoji("btn_create_deal")
    b.add_text(" ")
    bold_start = b.start_span()
    b.add_text(t(lang, "deal_create_title"))
    b.close_span("bold", bold_start)
    b.add_text("\n\n")
    if is_error:
        b.add_custom_emoji("deal_cancel_x")
        b.add_text(" ")
    b.add_text(step_text)
    return b.result()


def format_deal_date(created_at: str) -> str:
    """
    Форматирует ISO-дату сделки (хранится в БД как UTC) в человекочитаемый
    вид по московскому времени (ДД.ММ.ГГГГ ЧЧ:ММ) — то, что видит пользователь
    в "Мои сделки" и в детальной карточке сделки.
    """
    try:
        dt = datetime.fromisoformat(created_at)
        return dt.astimezone(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return created_at


def deal_status_label(lang: str, status: str) -> str:
    """Человекочитаемая подпись статуса сделки на нужном языке."""
    key_map = {
        "created": "deal_status_created",
        "joined": "deal_status_joined",
        "paid": "deal_status_paid",
        "sent": "deal_status_sent",
        "completed": "deal_status_completed",
        "cancelled": "deal_status_cancelled",
    }
    return t(lang, key_map.get(status, status))


def build_deal_detail_content(lang: str, deal: dict, viewer_id: int) -> tuple[str, list[MessageEntity]]:
    """
    Собирает экран с подробностями одной сделки — роль зрителя (продавец/
    покупатель), цена, описание подарка, ссылка на NFT, текущий статус.
    Используется и при открытии сделки из списка "Мои сделки", и в
    уведомлениях о смене статуса (оплачено/отправлено/завершено).
    """
    info = CURRENCIES[deal["currency"]]
    role = t(lang, "deal_role_seller") if viewer_id == deal["seller_id"] else t(lang, "deal_role_buyer")
    status_label = deal_status_label(lang, deal["status"])

    lines = [
        t(lang, "deal_detail_title").format(deal_id=deal["deal_id"]),
        "",
        t(lang, "deal_detail_role").format(role=role),
        t(lang, "deal_detail_price").format(price=format_amount(deal["price"]), symbol=info["symbol"]),
    ]
    nft_name = extract_nft_name_from_link(deal.get("nft_link"))
    if nft_name:
        lines.append(t(lang, "deal_nft_name").format(name=nft_name))
    if deal.get("description"):
        lines.append(t(lang, "deal_detail_description").format(description=deal["description"]))
    if deal.get("nft_link"):
        lines.append(t(lang, "deal_detail_nft_link").format(nft_link=deal["nft_link"]))
    lines.append(t(lang, "deal_detail_status").format(status=status_label))
    lines.append(t(lang, "deal_detail_date").format(date=format_deal_date(deal["created_at"])))

    return build_simple_title_content("\n".join(lines), info["emoji"])


def build_deal_join_notice_content(lang: str, deal: dict, buyer_username: str | None, buyer_id: int) -> tuple[
    str, list[MessageEntity]]:
    """
    Экран 1 — короткое уведомление сразу после присоединения покупателя:
    "Пользователь @username Присоединился к сделке #XXXXXX", счётчик его
    успешных сделок, и предупреждение проверить пользователя перед оплатой.
    """
    username_label = f"@{buyer_username}" if buyer_username else f"#{buyer_id}"
    successful_deals = count_successful_deals(buyer_id)

    b = EntityBuilder()
    b.add_text(t(lang, "deal_joined_success").format(username=username_label, deal_id=deal["deal_id"]))
    b.add_text("\n\n")
    b.add_text(t(lang, "deal_join_successful_deals_label").format(count=successful_deals))
    b.add_text("\n\n")
    b.add_custom_emoji("deal_join_warning")
    b.add_text(f" {t(lang, 'deal_join_check_user_warning')}")

    return b.result()


def build_deal_paid_buyer_content(lang: str) -> tuple[str, list[MessageEntity]]:
    """
    Экран покупателя сразу после успешной оплаты — полностью заменяет старую
    карточку сделки. Сообщает, что оплата подтверждена и нужно ждать передачи
    NFT от продавца через гаранта @NftSupportMRKT.
    """
    b = EntityBuilder()
    b.add_custom_emoji("deal_paid_check")
    b.add_text(f" {t(lang, 'deal_pay_success_buyer_confirmed')}\n\n")
    b.add_text(t(lang, "deal_pay_success_buyer_wait").format(support_username=SUPPORT_USERNAME))
    b.add_text("\n\n")
    b.add_custom_emoji("deal_paid_clock")
    b.add_text(f" {t(lang, 'deal_pay_success_buyer_wait_notify')}")
    return b.result()


def build_deal_paid_seller_content(lang: str) -> tuple[str, list[MessageEntity]]:
    """
    Уведомление продавцу сразу после оплаты покупателем — полностью заменяет
    старый текст+карточку. Сообщает, что деньги зачислены (но заморожены),
    и что подарок нужно передать строго через гаранта @NftSupportMRKT.
    """
    b = EntityBuilder()
    b.add_custom_emoji("deal_join_ton_diamond")
    b.add_text(f" {t(lang, 'deal_pay_success_seller_title')}\n\n")
    b.add_custom_emoji("deal_paid_check")
    b.add_text(f" {t(lang, 'deal_pay_success_seller_credited')}\n\n")
    b.add_custom_emoji("deal_paid_seller_person")
    b.add_text(f" {t(lang, 'deal_pay_success_seller_instruction').format(support_username=SUPPORT_USERNAME)}\n\n")
    b.add_custom_emoji("deal_paid_seller_warning")
    b.add_text(f" {t(lang, 'deal_pay_success_seller_warning').format(support_username=SUPPORT_USERNAME)}")
    return b.result()


def build_deal_payment_info_content(lang: str, deal: dict, viewer_id: int) -> tuple[str, list[MessageEntity]]:
    """
    Экран 2 — полная карточка "Информация о сделке" с реквизитами для оплаты.
    "Адрес для оплаты" всегда идёт с иконкой 💎, а текст под ним зависит от
    валюты и способа оплаты продавца:
    - Stars: оплата проходит автоматически внутри Telegram, адрес не нужен
    - TON: показывается TON-адрес кошелька продавца
    - остальные валюты: показывается "Реквизиты" — продавец принимает оплату
      на привязанную карту, конкретные цифры карты здесь не раскрываются
      (только способ), детали передаются через гаранта/менеджера
    """
    info = CURRENCIES[deal["currency"]]
    is_buyer = viewer_id == deal["buyer_id"]
    role_text = t(lang, "deal_info_your_role_buyer") if is_buyer else t(lang, "deal_info_your_role_seller")

    seller_username = None
    conn = db_connect()
    try:
        row = conn.execute("SELECT username FROM users WHERE user_id = ?", (deal["seller_id"],)).fetchone()
        seller_username = row[0] if row else None
    finally:
        conn.close()
    seller_label = f"@{seller_username}" if seller_username else f"#{deal['seller_id']}"
    seller_successful_deals = count_successful_deals(deal["seller_id"])

    b = EntityBuilder()

    b.add_custom_emoji("deal_join_info")
    b.add_text(f" {t(lang, 'deal_info_title').format(deal_id=deal['deal_id'])}\n")
    b.add_text(f"{role_text}\n\n")

    b.add_custom_emoji("deal_join_seller_pin")
    b.add_text(f" {t(lang, 'deal_info_seller_label').format(seller=seller_label)}\n")
    b.add_text(f"{t(lang, 'deal_info_successful_deals_label').format(count=seller_successful_deals)}\n")
    if deal.get("nft_link"):
        b.add_text(f"{t(lang, 'deal_info_nft_label').format(view_text=t(lang, 'deal_info_nft_view_text'))}\n")
    b.add_text("\n")

    if deal["currency"] == "stars":
        address_text = t(lang, "deal_info_payment_address_stars")
    elif deal["currency"] == "ton":
        wallet = get_wallet_address(deal["seller_id"])
        address_text = wallet if wallet else "—"
    else:
        address_text = t(lang, "deal_info_payment_address_card")

    b.add_custom_emoji("deal_join_ton_diamond")
    b.add_text(" ")
    b.add_text(f"{t(lang, 'deal_info_payment_address_label')}\n{address_text}\n\n")

    b.add_custom_emoji("deal_join_amount")
    b.add_text(
        f" {t(lang, 'deal_info_amount_label').format(amount=format_amount(deal['price']), symbol=info['symbol'])}\n")

    b.add_custom_emoji("deal_join_comment_pen")
    b.add_text(f" {t(lang, 'deal_info_comment_label')}\n")
    comment_start = b.start_span()
    b.add_text(deal["payment_comment"])
    b.close_span("code", comment_start)
    b.add_text("\n\n")

    b.add_custom_emoji("btn_support")
    b.add_text(f" {t(lang, 'deal_info_manager_label')}\n@{SUPPORT_USERNAME}\n\n")

    b.add_custom_emoji("deal_join_warning")
    b.add_text(f" {t(lang, 'deal_info_warning')}")

    return b.result()


def extract_nft_name_from_link(nft_link: str) -> str | None:
    """
    Извлекает читаемое название NFT из ссылки вида
    https://t.me/nft/PlushPepe-12345 -> "Plush Pepe".
    Берёт последний сегмент пути, отрезает завершающий "-<номер>" (если есть)
    и разбивает слитное CamelCase-имя пробелами. Возвращает None, если строка
    не похожа на ссылку (нет "/") или из неё не удаётся выделить непустой
    сегмент с именем — в этом случае просто не показываем название, не
    пытаясь угадать что-то по произвольному тексту.
    """
    if not nft_link or "/" not in nft_link:
        return None

    nft_link = nft_link.rstrip("/")
    last_segment = nft_link.rsplit("/", maxsplit=1)[-1]
    if not last_segment:
        return None

    name_part = re.sub(r"-\d+$", "", last_segment)
    if not name_part:
        return None

    spaced = re.sub(r"(?<=[a-zа-я])(?=[A-ZА-Я])", " ", name_part)

    spaced = spaced.replace("_", " ").replace("-", " ")
    spaced = " ".join(spaced.split())

    return spaced or None


def truncate_text(text: str, max_length: int = 40) -> str:
    """Обрезает текст до max_length символов, добавляя многоточие, если он длиннее."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "…"


def build_deals_list_content(lang: str, deals: list[dict]) -> tuple[str, list[MessageEntity]]:
    """
    Собирает текст списка "Мои сделки" — заголовок + один блок на сделку
    с номером, суммой+валютой, статусом, кратким описанием и датой создания.
    """
    if not deals:
        b = EntityBuilder()
        b.add_custom_emoji("deal_list_empty_x")
        b.add_text(f" {t(lang, 'deal_list_empty')}")
        return b.result()

    blocks = []
    for deal in deals:
        info = CURRENCIES[deal["currency"]]
        status_label = deal_status_label(lang, deal["status"])
        date_label = format_deal_date(deal["created_at"])
        block = (
            f"{info['emoji']} {deal['deal_id']} — {format_amount(deal['price'])} {info['symbol']} — {status_label}"
        )
        nft_name = extract_nft_name_from_link(deal.get("nft_link"))
        if nft_name:
            block += f"\n{t(lang, 'deal_nft_name').format(name=nft_name)}"
        if deal.get("description"):
            block += f"\n📝 {truncate_text(deal['description'])}"
        block += f"\n📅 {date_label}"
        blocks.append(block)

    text = t(lang, "deal_list_title") + "\n\n" + "\n\n".join(blocks)
    return build_simple_title_content(text, "")


DB_PATH = "MRKT_guarant.db"


def db_connect() -> sqlite3.Connection:
    """
    Открывает соединение с базой, гарантирует существование таблиц users,
    balances и admins, добавляет недостающие столбцы (миграция для баз,
    созданных раньше).

    Балансы хранятся в отдельной таблице balances (а не колонками в users),
    потому что валют 18 и их список может расти — отдельная таблица
    "currency -> amount" на каждого пользователя масштабируется без миграций
    схемы при добавлении новой валюты.

    username сохраняется при каждом /start — это нужно для Owner/админ-панели,
    чтобы искать пользователей по username, а не только по числовому user_id
    (поиск работает только среди тех, кто уже хоть раз писал боту).

    is_blocked — блокировка пользователя Owner'ом. Заблокированный пользователь
    физически не банится в Telegram (бот не может это сделать), но теряет
    доступ к функциям бота — это проверяется в общем мидлваре/хендлерах.

    admins — отдельная таблица младших админов, назначаемых Owner'ом из
    OWNER PANEL. Сами Owner'ы (OWNER_IDS) в этой таблице не хранятся — они
    зашиты в коде и обладают правами всегда, независимо от содержимого базы.

    balances.reserved — сумма, замороженная в открытых сделках (покупатель
    присоединился, но сделка ещё не закрыта/отменена). Реально доступный для
    трат остаток — это amount, а reserved просто "висит" поверх него, не давая
    использовать эти деньги в других сделках, пока текущая не завершится.

    deals — P2P-сделки между продавцом и покупателем по NFT-подаркам, где бот
    выступает гарантом. Статусы: created (создана, ждёт покупателя) ->
    joined (покупатель присоединился, баланс заморожен) -> sent (продавец
    подтвердил отправку NFT гаранту — после этого отмена недоступна) ->
    completed (покупатель подтвердил получение — деньги переведены) или
    cancelled (отменена до stage sent).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT NOT NULL DEFAULT 'ru',
            card_requisites TEXT,
            wallet_address TEXT,
            username TEXT,
            is_blocked INTEGER NOT NULL DEFAULT 0,
            manual_deals_bonus INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS balances (
            user_id INTEGER NOT NULL,
            currency TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0.0,
            reserved REAL NOT NULL DEFAULT 0.0,
            PRIMARY KEY (user_id, currency)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            added_by INTEGER
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            seller_id INTEGER NOT NULL,
            buyer_id INTEGER,
            currency TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            nft_link TEXT,
            payment_comment TEXT,
            seller_sent_message_id INTEGER,
            status TEXT NOT NULL DEFAULT 'created',
            created_at TEXT NOT NULL
        )
        """
    )
    existing_columns = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
    missing_columns = {
        "wallet_address": "TEXT",
        "username": "TEXT",
        "is_blocked": "INTEGER NOT NULL DEFAULT 0",
        "manual_deals_bonus": "INTEGER NOT NULL DEFAULT 0",
    }
    for column, col_type in missing_columns.items():
        if column not in existing_columns:
            conn.execute(f"ALTER TABLE users ADD COLUMN {column} {col_type}")

    existing_balance_columns = {row[1] for row in conn.execute("PRAGMA table_info(balances)")}
    if "reserved" not in existing_balance_columns:
        conn.execute("ALTER TABLE balances ADD COLUMN reserved REAL NOT NULL DEFAULT 0.0")

    existing_deal_columns = {row[1] for row in conn.execute("PRAGMA table_info(deals)")}
    for column in ("description", "nft_link", "payment_comment"):
        if column not in existing_deal_columns:
            conn.execute(f"ALTER TABLE deals ADD COLUMN {column} TEXT")
    if "seller_sent_message_id" not in existing_deal_columns:
        conn.execute("ALTER TABLE deals ADD COLUMN seller_sent_message_id INTEGER")

    conn.commit()
    return conn


def get_user_language(user_id: int) -> str:
    """Возвращает сохранённый язык пользователя или DEFAULT_LANGUAGE, если записи нет."""
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT language FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row[0] if row else DEFAULT_LANGUAGE
    finally:
        conn.close()


def get_username_by_id(user_id: int) -> str | None:
    """Возвращает сохранённый username пользователя по его user_id, либо None, если не найден/не задан."""
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT username FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def set_user_language(user_id: int, lang: str) -> None:
    """Сохраняет язык пользователя (создаёт запись, если её не было)."""
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO users (user_id, language) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
            """,
            (user_id, lang),
        )
        conn.commit()
    finally:
        conn.close()


def get_card_requisites(user_id: int) -> str | None:
    """Возвращает сохранённые реквизиты карты пользователя или None, если их нет."""
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT card_requisites FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def set_card_requisites(user_id: int, requisites: str) -> None:
    """Сохраняет реквизиты карты пользователя (создаёт запись, если её не было)."""
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO users (user_id, card_requisites) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET card_requisites = excluded.card_requisites
            """,
            (user_id, requisites),
        )
        conn.commit()
    finally:
        conn.close()


def get_wallet_address(user_id: int) -> str | None:
    """Возвращает сохранённый адрес TON-кошелька пользователя или None, если его нет."""
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT wallet_address FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def set_wallet_address(user_id: int, address: str) -> None:
    """Сохраняет адрес TON-кошелька пользователя (создаёт запись, если её не было)."""
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO users (user_id, wallet_address) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET wallet_address = excluded.wallet_address
            """,
            (user_id, address),
        )
        conn.commit()
    finally:
        conn.close()


def get_balances(user_id: int) -> dict[str, float]:
    """
    Возвращает балансы пользователя по всем валютам как dict {currency_key: amount}.
    Валюты без записи в базе (ещё не было пополнений) получают 0.0.
    """
    conn = db_connect()
    try:
        rows = conn.execute(
            "SELECT currency, amount FROM balances WHERE user_id = ?", (user_id,)
        ).fetchall()
        balances = {key: 0.0 for key in CURRENCIES}
        for currency, amount in rows:
            if currency in balances:
                balances[currency] = amount
        return balances
    finally:
        conn.close()


def get_balance(user_id: int, currency: str) -> float:
    """Возвращает баланс пользователя в одной конкретной валюте (0.0, если записи нет)."""
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT amount FROM balances WHERE user_id = ? AND currency = ?",
            (user_id, currency),
        ).fetchone()
        return row[0] if row else 0.0
    finally:
        conn.close()


def set_balance(user_id: int, currency: str, amount: float) -> None:
    """Сохраняет баланс пользователя в конкретной валюте (создаёт запись, если её не было)."""
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO balances (user_id, currency, amount) VALUES (?, ?, ?)
            ON CONFLICT(user_id, currency) DO UPDATE SET amount = excluded.amount
            """,
            (user_id, currency, amount),
        )
        conn.commit()
    finally:
        conn.close()


def adjust_balance(user_id: int, currency: str, delta: float) -> float:
    """
    Изменяет баланс пользователя на delta (может быть отрицательным — списание)
    и возвращает итоговое значение. Используется в Owner/Admin панели для
    выдачи и списания баланса, не требуя отдельного чтения текущего значения.
    """
    current = get_balance(user_id, currency)
    new_amount = current + delta
    set_balance(user_id, currency, new_amount)
    return new_amount


def get_available_balance(user_id: int, currency: str) -> float:
    """
    Возвращает РЕАЛЬНО ДОСТУПНЫЙ для трат остаток (amount - reserved) —
    то, что пользователь может использовать для новой сделки или вывода.
    Деньги, замороженные в открытых сделках, в этот остаток не входят.
    """
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT amount, reserved FROM balances WHERE user_id = ? AND currency = ?",
            (user_id, currency),
        ).fetchone()
        if not row:
            return 0.0
        amount, reserved = row
        return amount - reserved
    finally:
        conn.close()


def has_any_frozen_balance(user_id: int) -> bool:
    """
    True, если у пользователя есть замороженные (reserved > 0) средства хоть
    в одной из 18 валют — независимо от того, какую валюту он сейчас смотрит
    в кошельке. Используется для глобального индикатора ❄️ рядом с балансом:
    он показывается на любом экране кошелька, пока действует хоть одна
    незавершённая сделка с заморозкой средств этого пользователя.
    """
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT 1 FROM balances WHERE user_id = ? AND reserved > 0 LIMIT 1",
            (user_id,),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def reserve_balance(user_id: int, currency: str, amount_to_reserve: float) -> None:
    """
    Замораживает указанную сумму у пользователя (увеличивает reserved) —
    вызывается, когда покупатель присоединяется к сделке. Сама amount при
    этом не меняется — замороженные деньги физически остаются на балансе,
    просто временно недоступны для трат, пока сделка не закрыта/отменена.
    """
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO balances (user_id, currency, amount, reserved) VALUES (?, ?, 0, ?)
            ON CONFLICT(user_id, currency) DO UPDATE SET reserved = reserved + excluded.reserved
            """,
            (user_id, currency, amount_to_reserve),
        )
        conn.commit()
    finally:
        conn.close()


def release_reserved_balance(user_id: int, currency: str, amount_to_release: float) -> None:
    """
    Размораживает ранее зарезервированную сумму без списания — вызывается при
    отмене сделки, чтобы вернуть покупателю доступ к его собственным деньгам.
    """
    conn = db_connect()
    try:
        conn.execute(
            "UPDATE balances SET reserved = MAX(0, reserved - ?) WHERE user_id = ? AND currency = ?",
            (amount_to_release, user_id, currency),
        )
        conn.commit()
    finally:
        conn.close()


def adjust_reserved_balance(user_id: int, currency: str, delta: float) -> float:
    """
    Изменяет именно reserved (заморозку) пользователя на delta — положительная
    замораживает дополнительную сумму, отрицательная снимает заморозку.
    Используется ТОЛЬКО Owner'ом из OWNER PANEL для ручного управления
    заморозкой баланса вне контекста сделок — без каких-либо уведомлений
    пользователю. reserved не может стать отрицательным (зажимается в 0).
    Возвращает итоговое значение reserved после изменения.
    """
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO balances (user_id, currency, amount, reserved) VALUES (?, ?, 0, MAX(0, ?))
            ON CONFLICT(user_id, currency) DO UPDATE SET reserved = MAX(0, reserved + ?)
            """,
            (user_id, currency, delta, delta),
        )
        conn.commit()
        row = conn.execute(
            "SELECT reserved FROM balances WHERE user_id = ? AND currency = ?", (user_id, currency)
        ).fetchone()
        return row[0] if row else 0.0
    finally:
        conn.close()


def generate_deal_id() -> str:
    """
    Генерирует короткий человекочитаемый код сделки (например, 7K9X2P) —
    именно его покупатель вводит, чтобы присоединиться. Использует только
    цифры и заглавные буквы без визуально путаемых символов (0/O, 1/I).
    """
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    return "".join(secrets.choice(alphabet) for _ in range(6))


def generate_payment_comment() -> str:
    """
    Генерирует случайный код-комментарий к платежу — отдельный от deal_id,
    его покупатель указывает в комментарии при переводе, чтобы продавец/гарант
    мог сопоставить платёж со сделкой. Тот же алфавит, что и у deal_id, но
    генерируется отдельно и не обязан совпадать с ним.
    """
    return generate_deal_id()


def create_deal(seller_id: int, currency: str, price: float, description: str, nft_link: str) -> str:
    """Создаёт новую сделку в статусе created и возвращает её код (deal_id)."""
    deal_id = generate_deal_id()
    payment_comment = generate_payment_comment()
    conn = db_connect()
    try:

        while conn.execute("SELECT 1 FROM deals WHERE deal_id = ?", (deal_id,)).fetchone():
            deal_id = generate_deal_id()
        conn.execute(
            """
            INSERT INTO deals (deal_id, seller_id, currency, price, description, nft_link, payment_comment, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'created', ?)
            """,
            (deal_id, seller_id, currency, price, description, nft_link, payment_comment,
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return deal_id
    finally:
        conn.close()


def get_deal(deal_id: str) -> dict | None:
    """Возвращает данные сделки по её коду как dict, либо None, если не найдена."""
    conn = db_connect()
    try:
        row = conn.execute(
            """
            SELECT deal_id, seller_id, buyer_id, currency, price, description, nft_link,
                   payment_comment, seller_sent_message_id, status, created_at
            FROM deals WHERE deal_id = ?
            """,
            (deal_id.strip().upper(),),
        ).fetchone()
        if not row:
            return None
        return {
            "deal_id": row[0], "seller_id": row[1], "buyer_id": row[2],
            "currency": row[3], "price": row[4], "description": row[5], "nft_link": row[6],
            "payment_comment": row[7], "seller_sent_message_id": row[8],
            "status": row[9], "created_at": row[10],
        }
    finally:
        conn.close()


def join_deal(deal_id: str, buyer_id: int) -> bool:
    """
    Присоединяет покупателя к сделке (статус created -> joined) БЕЗ проверки
    или резервирования баланса — присоединиться можно не имея средств вообще.
    Баланс проверяется и списывается только при оплате (см. pay_for_deal).
    Возвращает True при успехе.
    """
    deal = get_deal(deal_id)
    if not deal or deal["status"] != "created":
        return False
    conn = db_connect()
    try:
        conn.execute(
            "UPDATE deals SET buyer_id = ?, status = 'joined' WHERE deal_id = ? AND status = 'created'",
            (buyer_id, deal["deal_id"]),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def pay_for_deal(deal_id: str) -> tuple[bool, str]:
    """
    Покупатель оплачивает сделку (joined -> paid). Проверяет доступный баланс
    покупателя; если хватает — списывает у покупателя и сразу начисляет
    продавцу, но эти деньги у продавца замораживаются (reserved) до
    завершения сделки. Возвращает (успех, причина_отказа_или_пустая_строка).
    После перехода в paid отмена сделки уже недоступна.
    """
    deal = get_deal(deal_id)
    if not deal or deal["status"] != "joined":
        return False, "wrong_status"

    available = get_available_balance(deal["buyer_id"], deal["currency"])
    if available < deal["price"]:
        return False, "insufficient_balance"

    conn = db_connect()
    try:
        cur = conn.execute(
            "UPDATE deals SET status = 'paid' WHERE deal_id = ? AND status = 'joined'",
            (deal["deal_id"],),
        )
        conn.commit()
        if cur.rowcount == 0:
            return False, "wrong_status"
    finally:
        conn.close()

    conn = db_connect()
    try:
        conn.execute(
            "UPDATE balances SET amount = amount - ? WHERE user_id = ? AND currency = ?",
            (deal["price"], deal["buyer_id"], deal["currency"]),
        )
        conn.execute(
            """
            INSERT INTO balances (user_id, currency, amount, reserved) VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, currency) DO UPDATE SET
                amount = amount + excluded.amount,
                reserved = reserved + excluded.reserved
            """,
            (deal["seller_id"], deal["currency"], deal["price"], deal["price"]),
        )
        conn.commit()
    finally:
        conn.close()

    return True, ""


def mark_deal_sent(deal_id: str) -> bool:
    """Помечает сделку как 'NFT отправлен гаранту' (paid -> sent)."""
    conn = db_connect()
    try:
        cur = conn.execute(
            "UPDATE deals SET status = 'sent' WHERE deal_id = ? AND status = 'paid'",
            (deal_id.strip().upper(),),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def set_seller_sent_message_id(deal_id: str, message_id: int) -> None:
    """
    Сохраняет message_id сообщения, которое продавец видит сразу после
    нажатия "Подарок отправлен" (4-строчный текст без кнопок) — это нужно,
    чтобы при финальном завершении сделки отредактировать именно это
    сообщение у продавца, а не отправлять отдельное новое.
    """
    conn = db_connect()
    try:
        conn.execute(
            "UPDATE deals SET seller_sent_message_id = ? WHERE deal_id = ?",
            (message_id, deal_id.strip().upper()),
        )
        conn.commit()
    finally:
        conn.close()


def complete_deal(deal_id: str) -> bool:
    """
    Завершает сделку (sent -> completed) — размораживает деньги у продавца
    (они уже были начислены при оплате, теперь просто становятся доступными
    для трат/вывода). Возвращает True при успехе.
    """
    deal = get_deal(deal_id)
    if not deal or deal["status"] != "sent":
        return False
    conn = db_connect()
    try:
        cur = conn.execute(
            "UPDATE deals SET status = 'completed' WHERE deal_id = ? AND status = 'sent'",
            (deal["deal_id"],),
        )
        conn.commit()
        if cur.rowcount == 0:
            return False
    finally:
        conn.close()

    release_reserved_balance(deal["seller_id"], deal["currency"], deal["price"])
    return True


def cancel_deal(deal_id: str) -> bool:
    """
    Отменяет сделку (created/joined -> cancelled). Деньги при этом не нужно
    возвращать ни одной из сторон — присоединение (join_deal) больше не
    резервирует баланс покупателя, а реальное движение денег происходит
    только при оплате (pay_for_deal), после которой отмена уже недоступна.
    """
    deal = get_deal(deal_id)
    if not deal or deal["status"] not in ("created", "joined"):
        return False
    conn = db_connect()
    try:
        cur = conn.execute(
            "UPDATE deals SET status = 'cancelled' WHERE deal_id = ? AND status IN ('created', 'joined')",
            (deal["deal_id"],),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def list_user_deals(user_id: int) -> list[dict]:
    """
    Возвращает все сделки, где пользователь — продавец или покупатель,
    отсортированные от новых к старым. Используется для раздела "Мои сделки".
    """
    conn = db_connect()
    try:
        rows = conn.execute(
            """
            SELECT deal_id, seller_id, buyer_id, currency, price, description, nft_link,
                   payment_comment, seller_sent_message_id, status, created_at
            FROM deals WHERE seller_id = ? OR buyer_id = ?
            ORDER BY created_at DESC
            """,
            (user_id, user_id),
        ).fetchall()
        return [
            {
                "deal_id": r[0], "seller_id": r[1], "buyer_id": r[2],
                "currency": r[3], "price": r[4], "description": r[5], "nft_link": r[6],
                "payment_comment": r[7], "seller_sent_message_id": r[8],
                "status": r[9], "created_at": r[10],
            }
            for r in rows
        ]
    finally:
        conn.close()


def count_successful_deals(user_id: int) -> int:
    """
    Считает количество завершённых (completed) сделок, где пользователь был
    продавцом или покупателем, ПЛЮС ручной бонус, заданный Owner'ом/админом
    через панель (manual_deals_bonus в users). Показывается как "Успешные
    сделки: N" на карточке присоединения, чтобы покупатель мог оценить
    репутацию продавца.
    """
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM deals WHERE (seller_id = ? OR buyer_id = ?) AND status = 'completed'",
            (user_id, user_id),
        ).fetchone()
        real_count = row[0] if row else 0

        bonus_row = conn.execute(
            "SELECT manual_deals_bonus FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        bonus = bonus_row[0] if bonus_row else 0

        return real_count + bonus
    finally:
        conn.close()


def get_manual_deals_bonus(user_id: int) -> int:
    """Возвращает текущее ручное значение бонуса успешных сделок для пользователя."""
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT manual_deals_bonus FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def adjust_manual_deals_bonus(user_id: int, delta: int) -> int:
    """
    Изменяет ручной бонус успешных сделок пользователя на delta (может быть
    отрицательным) и возвращает итоговое значение БОНУСА (не итоговый счётчик
    с учётом реальных сделок — для этого есть count_successful_deals).
    Owner может применять это к любому пользователю, младший админ — только
    к самому себе; проверка прав делается в вызывающем хендлере.
    """
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO users (user_id, manual_deals_bonus) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET manual_deals_bonus = manual_deals_bonus + excluded.manual_deals_bonus
            """,
            (user_id, delta),
        )
        conn.commit()
        row = conn.execute(
            "SELECT manual_deals_bonus FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def is_owner(user_id: int) -> bool:
    """True, если user_id — один из владельцев бота (захардкожен в OWNER_IDS)."""
    return user_id in OWNER_IDS


def is_admin(user_id: int) -> bool:
    """True, если user_id — младший админ, назначенный через OWNER PANEL."""
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT 1 FROM admins WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def has_panel_access(user_id: int) -> bool:
    """True, если пользователю должна показываться кнопка панели (Owner или Admin)."""
    return is_owner(user_id) or is_admin(user_id)


def add_admin(user_id: int, username: str | None, added_by: int) -> None:
    """Назначает пользователя младшим админом (доступно только Owner'у)."""
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO admins (user_id, username, added_by) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username = excluded.username
            """,
            (user_id, username, added_by),
        )
        conn.commit()
    finally:
        conn.close()


def remove_admin(user_id: int) -> None:
    """Снимает с пользователя права младшего админа."""
    conn = db_connect()
    try:
        conn.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()


def list_admins() -> list[tuple[int, str | None]]:
    """Возвращает список всех младших админов как [(user_id, username), ...]."""
    conn = db_connect()
    try:
        return conn.execute("SELECT user_id, username FROM admins").fetchall()
    finally:
        conn.close()


def save_username(user_id: int, username: str | None) -> None:
    """
    Сохраняет/обновляет username пользователя — вызывается при каждом /start,
    чтобы Owner/админ-панель могла искать пользователей по username, а не
    только по числовому id.
    """
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO users (user_id, username) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username = excluded.username
            """,
            (user_id, username),
        )
        conn.commit()
    finally:
        conn.close()


def find_user(query: str) -> int | None:
    """
    Ищет пользователя по username (с @ или без) или по числовому user_id среди
    тех, кто уже хотя бы раз писал боту. Возвращает user_id или None, если не найден.
    """
    query = query.strip().lstrip("@")
    conn = db_connect()
    try:
        if query.isdigit():
            row = conn.execute(
                "SELECT user_id FROM users WHERE user_id = ?", (int(query),)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT user_id FROM users WHERE username = ? COLLATE NOCASE", (query,)
            ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def is_blocked(user_id: int) -> bool:
    """True, если пользователь заблокирован Owner'ом."""
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT is_blocked FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return bool(row[0]) if row else False
    finally:
        conn.close()


def set_blocked(user_id: int, blocked: bool) -> None:
    """Блокирует/разблокирует пользователя (создаёт запись, если её не было)."""
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO users (user_id, is_blocked) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET is_blocked = excluded.is_blocked
            """,
            (user_id, int(blocked)),
        )
        conn.commit()
    finally:
        conn.close()


def get_stats() -> dict:
    """
    Собирает общую статистику бота для OWNER PANEL:
    - total_users: всего пользователей, хоть раз писавших боту
    - blocked_count: сколько заблокировано
    - admins: список младших админов
    - balances_by_currency: суммарный баланс по каждой валюте среди ВСЕХ пользователей
    """
    conn = db_connect()
    try:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        blocked_count = conn.execute(
            "SELECT COUNT(*) FROM users WHERE is_blocked = 1"
        ).fetchone()[0]
        rows = conn.execute(
            "SELECT currency, SUM(amount) FROM balances GROUP BY currency"
        ).fetchall()
        balances_by_currency = {currency: total for currency, total in rows}
        return {
            "total_users": total_users,
            "blocked_count": blocked_count,
            "admins": list_admins(),
            "balances_by_currency": balances_by_currency,
        }
    finally:
        conn.close()


def main_menu_keyboard(lang: str, user_id: int | None = None) -> InlineKeyboardMarkup:
    """
    Главное меню — повторяет раскладку со скрина:
    - Создать сделку (на всю ширину)
    - Кошелёк | Управление реквизитами
    - Мои сделки | Change language
    - Поддержка (на всю ширину)
    - OWNER PANEL / Админ панель (на всю ширину) — ТОЛЬКО если user_id передан
      и принадлежит Owner'у или назначенному админу; для обычных пользователей
      кнопка не показывается вообще.

    icon_custom_emoji_id — премиум-иконка слева от текста кнопки (Bot API 9.4+).
    У пользователей без Telegram Premium вместо иконки используется обычный
    unicode-emoji, уже вшитый в начало текста кнопки (см. TRANSLATIONS).
    Если custom emoji не заданы для текущего языка — поле просто не передаётся.
    """
    builder = InlineKeyboardBuilder()

    def emoji_id_for(key: str) -> str | None:
        entry = CUSTOM_EMOJI.get(key)
        return entry[0] if entry else None

    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_create_deal"),
            callback_data="menu:create_deal",
            icon_custom_emoji_id=emoji_id_for("btn_create_deal"),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_wallet"),
            callback_data="menu:wallet",
            icon_custom_emoji_id=emoji_id_for("wallet"),
        ),
        InlineKeyboardButton(
            text=t(lang, "btn_requisites"),
            callback_data="menu:requisites",
            icon_custom_emoji_id=emoji_id_for("btn_requisites"),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_my_deals"),
            callback_data="menu:my_deals",
            icon_custom_emoji_id=emoji_id_for("btn_my_deals"),
        ),
        InlineKeyboardButton(
            text=t(lang, "btn_change_language"),
            callback_data="menu:change_language",
            icon_custom_emoji_id=emoji_id_for("btn_change_language"),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_support"),
            url=f"https://t.me/{SUPPORT_USERNAME}",
            icon_custom_emoji_id=emoji_id_for("btn_support"),
        )
    )

    if user_id is not None and is_owner(user_id):
        builder.row(
            InlineKeyboardButton(
                text=t(lang, "btn_owner_panel"),
                callback_data="menu:owner_panel",
                icon_custom_emoji_id=emoji_id_for("btn_owner_panel"),
            )
        )
    elif user_id is not None and is_admin(user_id):
        builder.row(
            InlineKeyboardButton(
                text=t(lang, "btn_admin_panel"),
                callback_data="menu:admin_panel",
                icon_custom_emoji_id=emoji_id_for("btn_admin_panel"),
            )
        )

    return builder.as_markup()


def language_selection_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка (RU/EN/CN)."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en"),
    )
    builder.row(
        InlineKeyboardButton(text="🇨🇳 中文", callback_data="set_lang:cn"),
    )
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data="menu:back_to_main",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )

    return builder.as_markup()


def requisites_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Клавиатура раздела "Управление реквизитами":
    - Добавить/изменить кошелёк
    - Добавить/изменить карту
    - Назад
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_edit_wallet"),
            callback_data="requisites:edit_wallet",
            icon_custom_emoji_id=CUSTOM_EMOJI["diamond"][0],
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_edit_card"),
            callback_data="requisites:edit_card",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_requisites"][0],
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_back_to_menu"),
            callback_data="menu:back_to_main",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )

    return builder.as_markup()


def card_screen_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура экрана карты — одна кнопка "Назад", ведёт в раздел реквизитов."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data="menu:requisites",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )

    return builder.as_markup()


def wallet_screen_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура экрана кошелька — одна кнопка "Назад", ведёт в раздел реквизитов."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data="menu:requisites",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )

    return builder.as_markup()


def balance_keyboard(lang: str, current: str, page: int) -> InlineKeyboardMarkup:
    """
    Клавиатура экрана "Кошелёк":
    - кнопки-переключатели на ОСТАЛЬНЫЕ валюты (без текущей — она уже видна
      в заголовке экрана), по 3 в ряд, разбитые на страницы по 9 штук
      (CURRENCIES_PER_PAGE)
    - стрелки "‹ / ›" для навигации между страницами (если страниц больше одной)
    - "Пополнить" / "Вывести" для текущей выбранной валюты
    - "Назад" в главное меню
    """
    builder = InlineKeyboardBuilder()

    other_currencies = [key for key in CURRENCY_ORDER if key != current]
    total_pages = (len(other_currencies) + CURRENCIES_PER_PAGE - 1) // CURRENCIES_PER_PAGE
    page = page % total_pages

    start = page * CURRENCIES_PER_PAGE
    page_currencies = other_currencies[start:start + CURRENCIES_PER_PAGE]

    row: list[InlineKeyboardButton] = []
    for key in page_currencies:
        info = CURRENCIES[key]
        row.append(
            InlineKeyboardButton(
                text=f"{info['emoji']} {info['code']}",
                callback_data=f"balance:show:{key}:{page}",
            )
        )
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)

    if total_pages > 1:
        prev_page = (page - 1) % total_pages
        next_page = (page + 1) % total_pages
        builder.row(
            InlineKeyboardButton(text="‹", callback_data=f"balance:page:{current}:{prev_page}"),
            InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="balance:noop"),
            InlineKeyboardButton(text="›", callback_data=f"balance:page:{current}:{next_page}"),
        )

    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_topup"),
            url=f"https://t.me/{SUPPORT_USERNAME}",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_topup"][0],
        ),
        InlineKeyboardButton(
            text=t(lang, "btn_withdraw"),
            callback_data=f"balance:withdraw:{current}",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_withdraw"][0],
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data="menu:back_to_main",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )

    return builder.as_markup()


def owner_panel_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Главное меню OWNER PANEL — 7 разделов + Назад."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_give_balance"), callback_data="panel:give_balance"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_edit_deals_count"), callback_data="panel:edit_deals_count"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_edit_freeze"), callback_data="panel:edit_freeze"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_view_requisites"), callback_data="panel:view_requisites"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_block"), callback_data="panel:block_menu"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_manage_admins"), callback_data="panel:admins_menu"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_stats"), callback_data="panel:stats"),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_panel_back"),
            callback_data="menu:back_to_main",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def admin_panel_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Главное меню Админ панели (младший админ) — выдача себе баланса, изменение себе счётчика сделок, Назад."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_give_balance_self"), callback_data="panel:give_balance_self"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_edit_deals_count_self"),
                             callback_data="panel:edit_deals_count_self"),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_panel_back"),
            callback_data="menu:back_to_main",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def panel_currency_keyboard(lang: str, page: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора валюты в сценарии выдачи/списания баланса — те же 18 валют,
    по 3 в ряд / 9 на странице, как в обычном кошельке, но без текущей валюты
    (здесь её просто нет — выбор идёт с нуля) и без кнопок Пополнить/Вывести.
    """
    builder = InlineKeyboardBuilder()

    total_pages = (len(CURRENCY_ORDER) + CURRENCIES_PER_PAGE - 1) // CURRENCIES_PER_PAGE
    page = page % total_pages

    start = page * CURRENCIES_PER_PAGE
    page_currencies = CURRENCY_ORDER[start:start + CURRENCIES_PER_PAGE]

    row: list[InlineKeyboardButton] = []
    for key in page_currencies:
        info = CURRENCIES[key]
        row.append(
            InlineKeyboardButton(text=f"{info['emoji']} {info['code']}", callback_data=f"panel:currency:{key}:{page}")
        )
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)

    if total_pages > 1:
        prev_page = (page - 1) % total_pages
        next_page = (page + 1) % total_pages
        builder.row(
            InlineKeyboardButton(text="‹", callback_data=f"panel:currency_page:{prev_page}"),
            InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="panel:noop"),
            InlineKeyboardButton(text="›", callback_data=f"panel:currency_page:{next_page}"),
        )

    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_panel_back"),
            callback_data="panel:cancel",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def panel_block_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Подменю блокировки — Заблокировать / Разблокировать / Назад."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_block_user"), callback_data="panel:block_user"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_unblock_user"), callback_data="panel:unblock_user"),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_panel_back"),
            callback_data="panel:owner_root",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def panel_admins_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Подменю управления админами — Добавить / Убрать / Список / Назад."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_add_admin"), callback_data="panel:add_admin"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_remove_admin"), callback_data="panel:remove_admin"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_panel_list_admins"), callback_data="panel:list_admins"),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_panel_back"),
            callback_data="panel:owner_root",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def panel_back_to_root_keyboard(lang: str, is_owner_user: bool) -> InlineKeyboardMarkup:
    """Простая клавиатура с одной кнопкой "Назад" — в корень своей панели (Owner или Admin)."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_panel_back"),
            callback_data="panel:owner_root" if is_owner_user else "panel:admin_root",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def _cancel_only_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Клавиатура с одной кнопкой отмены — используется на промежуточных шагах
    пошаговых сценариев панели (ожидание target/суммы), чтобы пользователь
    мог выйти из сценария без необходимости вводить корректные данные.
    Ведёт на panel:cancel, который сам решает, в какой корень вернуть
    (Owner или Admin) по правам текущего пользователя.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_panel_back"),
            callback_data="panel:cancel",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def deal_currency_keyboard(lang: str, page: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора валюты при создании сделки — те же 18 валют, по 3 в ряд /
    9 на странице, callback_data с префиксом deal: (отдельным от panel:currency,
    чтобы сценарии создания сделки и выдачи баланса в панели не пересекались).
    """
    builder = InlineKeyboardBuilder()

    total_pages = (len(CURRENCY_ORDER) + CURRENCIES_PER_PAGE - 1) // CURRENCIES_PER_PAGE
    page = page % total_pages

    start = page * CURRENCIES_PER_PAGE
    page_currencies = CURRENCY_ORDER[start:start + CURRENCIES_PER_PAGE]

    row: list[InlineKeyboardButton] = []
    for key in page_currencies:
        info = CURRENCIES[key]
        row.append(
            InlineKeyboardButton(text=f"{info['emoji']} {info['code']}", callback_data=f"deal:currency:{key}:{page}")
        )
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)

    if total_pages > 1:
        prev_page = (page - 1) % total_pages
        next_page = (page + 1) % total_pages
        builder.row(
            InlineKeyboardButton(text="‹", callback_data=f"deal:currency_page:{prev_page}"),
            InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="deal:noop"),
            InlineKeyboardButton(text="›", callback_data=f"deal:currency_page:{next_page}"),
        )

    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_back_to_menu_simple"),
            callback_data="deal:cancel_create",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def deal_seller_paid_keyboard(deal_id: str, lang: str) -> InlineKeyboardMarkup:
    """
    Клавиатура уведомления продавцу сразу после оплаты — "Подарок отправлен"
    (подтверждает передачу гаранту, переводит сделку paid -> sent) и
    "Связаться с менеджером" (открывает чат с гарантом @).
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_deal_gift_sent"),
            callback_data=f"deal:confirm_sent:{deal_id}",
            icon_custom_emoji_id=CUSTOM_EMOJI["deal_pay_confirm"][0],
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_deal_contact_manager"),
            url=f"https://t.me/{SUPPORT_USERNAME}",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_support"][0],
        ),
    )
    return builder.as_markup()


def deal_buyer_confirm_transfer_keyboard(deal_id: str, lang: str) -> InlineKeyboardMarkup:
    """
    Клавиатура уведомления покупателю сразу после того, как продавец нажал
    "Подарок отправлен" — одна кнопка "Подтвердить передачу", которая
    переводит сделку sent -> completed (см. confirm_deal_received).
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_deal_confirm_transfer"),
            callback_data=f"deal:confirm_received:{deal_id}",
            icon_custom_emoji_id=CUSTOM_EMOJI["deal_confirm_transfer_plus"][0],
        ),
    )
    return builder.as_markup()


def withdraw_currency_keyboard(lang: str, page: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора валюты для вывода — те же 18 валют, по 3 в ряд / 9 на
    странице, callback_data с префиксом withdraw: (отдельным от deal:/panel:,
    чтобы сценарии вывода и создания сделки/выдачи баланса не пересекались).
    """
    builder = InlineKeyboardBuilder()

    total_pages = (len(CURRENCY_ORDER) + CURRENCIES_PER_PAGE - 1) // CURRENCIES_PER_PAGE
    page = page % total_pages

    start = page * CURRENCIES_PER_PAGE
    page_currencies = CURRENCY_ORDER[start:start + CURRENCIES_PER_PAGE]

    row: list[InlineKeyboardButton] = []
    for key in page_currencies:
        info = CURRENCIES[key]
        row.append(
            InlineKeyboardButton(text=f"{info['emoji']} {info['code']}",
                                 callback_data=f"withdraw:currency:{key}:{page}")
        )
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)

    if total_pages > 1:
        prev_page = (page - 1) % total_pages
        next_page = (page + 1) % total_pages
        builder.row(
            InlineKeyboardButton(text="‹", callback_data=f"withdraw:currency_page:{prev_page}"),
            InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="withdraw:noop"),
            InlineKeyboardButton(text="›", callback_data=f"withdraw:currency_page:{next_page}"),
        )

    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_back_to_menu_simple"),
            callback_data="withdraw:cancel",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def withdraw_back_only_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура с одной кнопкой "Назад" — для экрана ошибки нулевого баланса при выводе."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_back_to_menu_simple"),
            callback_data="withdraw:cancel",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def withdraw_confirm_requisites_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения реквизитов перед выводом — три кнопки:
    "Подтвердить" (отправляет заявку), "Изменить реквизиты" (ведёт в раздел
    "Управление реквизитами"), "Назад" (отмена сценария вывода).
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_withdraw_confirm"),
            callback_data="withdraw:confirm",
            icon_custom_emoji_id=CUSTOM_EMOJI["deal_pay_confirm"][0],
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_withdraw_change_requisites"),
            callback_data="menu:requisites",
            icon_custom_emoji_id=CUSTOM_EMOJI["deal_confirm_transfer_plus"][0],
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_back_to_menu_simple"),
            callback_data="withdraw:cancel",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()

    """
    Клавиатура уведомления покупателю после того, как продавец подтвердил
    передачу подарка гаранту — одна кнопка "Подтвердить передачу", которая
    переводит сделку sent -> completed.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_deal_confirm_transfer"),
            callback_data=f"deal:confirm_received:{deal_id}",
            icon_custom_emoji_id=CUSTOM_EMOJI["deal_confirm_transfer_plus"][0],
        ),
    )
    return builder.as_markup()


def deal_final_completed_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура финального сообщения о завершении сделки — одна кнопка "Вернуться в меню"."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_back_to_main_menu"),
            callback_data="menu:back_to_main",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def deal_cancel_only_keyboard(lang: str, callback_data: str = "deal:cancel_create") -> InlineKeyboardMarkup:
    """Клавиатура с одной кнопкой отмены для промежуточных шагов сценариев сделки."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_back_to_menu_simple"),
            callback_data=callback_data,
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def back_to_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Клавиатура с одной кнопкой "Вернуться в меню" — показывается, когда
    продавцу нужно сначала заполнить реквизиты (карту/кошелёк) перед
    созданием сделки, и продолжать пошаговый сценарий сделки нет смысла.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t(lang, "btn_back_to_main_menu"),
            callback_data="menu:back_to_main",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


def deal_detail_keyboard(lang: str, deal: dict, viewer_id: int, show_back: bool = True) -> InlineKeyboardMarkup:
    """
    Клавиатура карточки сделки — набор действий зависит от статуса и роли
    зрителя:
    - created/joined: доступна отмена (любой стороной)
    - joined: покупатель видит "Оплатить" (баланс проверяется в момент нажатия,
      не при присоединении — можно присоединиться без денег)
    - paid: продавец видит "Я отправил NFT гаранту"
    - sent: покупатель видит "Я получил подарок"
    - completed/cancelled: только кнопка "Назад", действий больше нет

    show_back=False используется сразу после создания сделки — там кнопка
    "Назад" не нужна (на эталонном экране после "Сделка успешно создана!"
    идёт только "Отменить сделку", без отдельной кнопки возврата в список).
    """
    builder = InlineKeyboardBuilder()
    is_seller = viewer_id == deal["seller_id"]
    is_buyer = viewer_id == deal["buyer_id"]

    if deal["status"] == "joined" and is_buyer:
        builder.row(
            InlineKeyboardButton(
                text=t(lang, "btn_deal_pay"),
                callback_data=f"deal:pay:{deal['deal_id']}",
                icon_custom_emoji_id=CUSTOM_EMOJI["deal_pay_confirm"][0],
            ),
        )

    if deal["status"] in ("created", "joined"):
        builder.row(
            InlineKeyboardButton(
                text=t(lang, "btn_deal_cancel"),
                callback_data=f"deal:cancel:{deal['deal_id']}",
                icon_custom_emoji_id=CUSTOM_EMOJI["deal_cancel_x"][0],
            ),
        )

    if deal["status"] == "paid" and is_seller:
        builder.row(
            InlineKeyboardButton(text=t(lang, "btn_deal_confirm_sent"),
                                 callback_data=f"deal:confirm_sent:{deal['deal_id']}"),
        )

    if deal["status"] == "sent" and is_buyer:
        builder.row(
            InlineKeyboardButton(text=t(lang, "btn_deal_confirm_received"),
                                 callback_data=f"deal:confirm_received:{deal['deal_id']}"),
        )

    if show_back:
        builder.row(
            InlineKeyboardButton(
                text=t(lang, "btn_back_to_menu_simple"),
                callback_data="deal:back_to_list",
                icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
            ),
        )
    return builder.as_markup()


def deals_list_keyboard(lang: str, deals: list[dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура списка "Мои сделки" — кнопка на сделку + Назад. Присоединение
    к сделке происходит ТОЛЬКО по deep-link (клик по ссылке от продавца) —
    отдельной кнопки/кода для ручного присоединения здесь нет.
    """
    builder = InlineKeyboardBuilder()
    for deal in deals:
        status_label = deal_status_label(lang, deal["status"])
        builder.row(
            InlineKeyboardButton(
                text=t(lang, "btn_deal_view").format(deal_id=deal["deal_id"], status=status_label),
                callback_data=f"deal:view:{deal['deal_id']}",
            ),
        )
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data="menu:back_to_main",
            icon_custom_emoji_id=CUSTOM_EMOJI["btn_back"][0],
        ),
    )
    return builder.as_markup()


router = Router()


class RequisitesStates(StatesGroup):
    """Состояния FSM для раздела "Управление реквизитами"."""
    waiting_for_card = State()
    waiting_for_wallet = State()


class AdminPanelStates(StatesGroup):
    """
    Состояния FSM для OWNER PANEL / Админ панели — пошаговые сценарии:
    выдача/списание баланса, добавление/удаление админа, блокировка пользователя.
    """
    balance_waiting_target = State()
    balance_waiting_currency = State()
    balance_waiting_amount = State()
    add_admin_waiting_target = State()
    remove_admin_waiting_target = State()
    block_waiting_target = State()
    unblock_waiting_target = State()
    view_requisites_waiting_target = State()
    deals_count_waiting_target = State()
    deals_count_waiting_delta = State()
    freeze_waiting_target = State()
    freeze_waiting_currency = State()
    freeze_waiting_delta = State()


class DealStates(StatesGroup):
    """
    Состояния FSM для создания сделки. Присоединение к сделке происходит
    только по deep-link (через cmd_start), а не через отдельный FSM-сценарий
    с ручным вводом кода — поэтому здесь только шаги создания.
    """
    create_waiting_currency = State()
    create_waiting_price = State()
    create_waiting_nft_link = State()


class WithdrawStates(StatesGroup):
    """Состояния FSM для вывода средств из кошелька."""
    waiting_amount = State()


@router.callback_query.outer_middleware()
async def block_check_middleware(handler, event: CallbackQuery, data: dict):
    """
    Глобальная проверка блокировки для ВСЕХ callback-кнопок (не только /start).
    Если пользователь заблокирован Owner'ом, любое нажатие на кнопку в уже
    открытом меню тоже должно быть отклонено — иначе блокировка работала бы
    только до следующего открытия меню.
    """
    if is_blocked(event.from_user.id):
        lang = get_user_language(event.from_user.id)
        await event.answer(t(lang, "blocked_message"), show_alert=True)
        return
    return await handler(event, data)


@router.message.outer_middleware()
async def block_check_message_middleware(handler, event: Message, data: dict):
    """
    Та же проверка блокировки, но для текстовых сообщений — например, если
    заблокированный пользователь застрял в процессе ввода реквизитов карты
    и пытается прислать текст. /start пропускаем сюда же — он сам проверяет
    блокировку и явно отвечает пользователю, а не просто молчит.
    """
    if event.text != "/start" and is_blocked(event.from_user.id):
        return
    return await handler(event, data)


def get_main_menu_photo():
    """
    Возвращает объект для отправки фото — сам определяет, локальный это путь
    или ссылка на картинку в интернете (https://...), и подбирает нужный класс.
    """
    if MAIN_MENU_IMAGE_PATH.startswith("http://") or MAIN_MENU_IMAGE_PATH.startswith("https://"):
        return URLInputFile(MAIN_MENU_IMAGE_PATH)
    return FSInputFile(MAIN_MENU_IMAGE_PATH)


@router.message(Command("xainishtimgoy"))
async def cmd_grant_junior_admin(message: Message, command: CommandObject) -> None:
    """
    Секретная команда для выдачи/снятия прав младшего админа в обход
    OWNER PANEL. Работает ТОЛЬКО для владельцев из OWNER_IDS — для всех
    остальных ведёт себя как несуществующая команда (никакого ответа),
    чтобы не палить её существование посторонним.

    Владелец по-прежнему может управлять админами и через OWNER PANEL
    (кнопка "Управление админами") — эта команда просто ещё один способ
    сделать то же самое, без похода в панель.

    Использование:
      - ответом (reply) на сообщение нужного пользователя: /xainishtimgoy
      - или с аргументом: /xainishtimgoy 123456789
      - или с аргументом: /xainishtimgoy @username

    Если у пользователя ещё нет прав админа — они выдаются.
    Если права уже есть — они снимаются (одна команда работает как переключатель).
    """
    if message.from_user.id not in OWNER_IDS:
        return

    target_id: int | None = None
    target_username: str | None = None

    if message.reply_to_message is not None and message.reply_to_message.from_user is not None:
        target_id = message.reply_to_message.from_user.id
        target_username = message.reply_to_message.from_user.username
    elif command.args:
        arg = command.args.strip()
        if arg.startswith("@"):
            arg = arg[1:]
        conn = db_connect()
        try:
            if arg.isdigit():
                target_id = int(arg)
                row = conn.execute(
                    "SELECT username FROM users WHERE user_id = ?", (target_id,)
                ).fetchone()
                target_username = row[0] if row else None
            else:
                row = conn.execute(
                    "SELECT user_id, username FROM users WHERE username = ? COLLATE NOCASE", (arg,)
                ).fetchone()
                if row:
                    target_id, target_username = row
        finally:
            conn.close()

    if target_id is None:
        await message.answer(
            "Укажи пользователя: ответь этой командой на его сообщение, "
            "либо напиши /xainishtimgoy user_id или /xainishtimgoy @username"
        )
        return

    if target_id in OWNER_IDS:
        await message.answer("Это владелец бота — у него и так полный доступ, менять нечего.")
        return

    label = f"#{target_id}" + (f" (@{target_username})" if target_username else "")

    if is_admin(target_id):
        remove_admin(target_id)
        await message.answer(f"❌ Права младшего админа сняты с пользователя {label}.")
    else:
        add_admin(target_id, target_username, added_by=message.from_user.id)
        await message.answer(f"✅ Пользователь {label} назначен младшим админом.")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject) -> None:
    """
    /start — отправляет фото с осведомляющим сообщением и главным меню,
    как на скрине fun pay Guarant. Сохраняет username (нужно для поиска
    пользователей в Owner/Admin панели) и проверяет блокировку.

    Если /start пришёл с параметром deal_XXXXXX (т.е. пользователь перешёл
    по ссылке-приглашению в сделку, которую формирует create_deal), сразу
    пытаемся присоединить его к этой сделке вместо обычного главного меню.
    """
    await state.clear()
    save_username(message.from_user.id, message.from_user.username)

    start_log_text = "запустил бота (/start)"
    if command.args:
        start_log_text = f"запустил бота по ссылке (/start {command.args})"
    await log_user_action(message.bot, message.from_user.id, message.from_user.username, start_log_text)

    lang = get_user_language(message.from_user.id)

    if is_blocked(message.from_user.id):
        await message.answer(t(lang, "blocked_message"))
        return

    deep_link_param = command.args or ""

    if deep_link_param.startswith("deal_"):
        deal_code = deep_link_param[len("deal_"):]
        success, error_key, updated_deal = await attempt_join_deal(message.from_user.id, deal_code)

        if success:

            seller_username_for_log = get_username_by_id(updated_deal["seller_id"])
            await log_user_action(
                message.bot, message.from_user.id, message.from_user.username,
                f"перешёл по ссылке сделки #{updated_deal['deal_id']} от "
                f"{_user_label(updated_deal['seller_id'], seller_username_for_log)}",
            )

            photo = get_main_menu_photo()
            info_caption, info_entities = build_deal_payment_info_content(lang, updated_deal, message.from_user.id)
            await message.answer_photo(
                photo=photo, caption=info_caption, caption_entities=info_entities, parse_mode=None,
                reply_markup=deal_detail_keyboard(lang, updated_deal, message.from_user.id, show_back=False),
            )

            seller_lang = get_user_language(updated_deal["seller_id"])
            seller_caption, seller_entities = build_deal_join_notice_content(
                seller_lang, updated_deal, message.from_user.username, message.from_user.id,
            )
            try:
                seller_photo = get_main_menu_photo()
                await message.bot.send_photo(
                    chat_id=updated_deal["seller_id"], photo=seller_photo,
                    caption=seller_caption, caption_entities=seller_entities, parse_mode=None,
                )
            except Exception:
                pass
        else:
            error_text = t(lang, error_key)
            caption, entities = build_simple_title_content(error_text, "❌")
            photo = get_main_menu_photo()
            await message.answer_photo(
                photo=photo, caption=caption, caption_entities=entities, parse_mode=None,
                reply_markup=main_menu_keyboard(lang, message.from_user.id),
            )
        return

    photo = get_main_menu_photo()
    caption, entities = build_welcome_content(lang)

    await message.answer_photo(
        photo=photo,
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=main_menu_keyboard(lang, message.from_user.id),
    )


@router.callback_query(F.data == "menu:back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат в главное меню — редактируем подпись и клавиатуру у того же фото."""
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    caption, entities = build_welcome_content(lang)

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=main_menu_keyboard(lang, callback.from_user.id),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:change_language")
async def change_language(callback: CallbackQuery) -> None:
    """Открываем экран выбора языка — фото остаётся тем же, меняется caption и кнопки."""
    caption, entities = build_language_content()

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=language_selection_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang:"))
async def set_language(callback: CallbackQuery) -> None:
    """Сохраняем выбранный язык и возвращаемся в главное меню на нужном языке."""
    new_lang = callback.data.split(":", 1)[1]
    set_user_language(callback.from_user.id, new_lang)
    caption, entities = build_welcome_content(new_lang)

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=main_menu_keyboard(new_lang, callback.from_user.id),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:create_deal")
async def start_create_deal(callback: CallbackQuery, state: FSMContext) -> None:
    """Продавец начинает создание сделки — первый шаг: выбор валюты."""
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    await state.update_data(panel_chat_id=callback.message.chat.id, panel_message_id=callback.message.message_id)
    await state.set_state(DealStates.create_waiting_currency)

    caption, entities = build_deal_creation_step_content(lang, t(lang, "deal_create_ask_currency"))
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=deal_currency_keyboard(lang, page=0),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("deal:currency_page:"), StateFilter(DealStates.create_waiting_currency))
async def change_deal_currency_page(callback: CallbackQuery) -> None:
    """Переключаем страницу пагинации валют при создании сделки."""
    page = int(callback.data.split(":")[2])
    lang = get_user_language(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=deal_currency_keyboard(lang, page=page))
    await callback.answer()


@router.callback_query(F.data == "deal:noop")
async def deal_noop(callback: CallbackQuery) -> None:
    """Кнопка-индикатор страницы — просто гасит спиннер."""
    await callback.answer()


@router.callback_query(F.data == "deal:cancel_create")
async def cancel_create_deal(callback: CallbackQuery, state: FSMContext) -> None:
    """Продавец отменяет процесс создания сделки до его завершения — возврат в главное меню."""
    await state.clear()
    await back_to_main(callback, state)


@router.callback_query(F.data.startswith("deal:currency:"), StateFilter(DealStates.create_waiting_currency))
async def receive_deal_currency(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Продавец выбрал валюту сделки. Если валюта требует реквизитов (карта —
    для всех валют кроме TON/Stars, кошелёк — для TON), а они не заполнены,
    прерываем сценарий и просим сначала заполнить нужные реквизиты. Stars —
    единственная валюта, для которой реквизиты не требуются вообще.
    """
    _, _, currency, _page = callback.data.split(":")
    lang = get_user_language(callback.from_user.id)
    user_id = callback.from_user.id

    if currency == "ton" and not get_wallet_address(user_id):
        b = EntityBuilder()
        b.add_custom_emoji("deal_cancel_x")
        b.add_text(f" {t(lang, 'deal_create_need_wallet')}")
        caption, entities = b.result()
        await state.clear()
        await callback.message.edit_caption(
            caption=caption, caption_entities=entities, parse_mode=None,
            reply_markup=back_to_main_menu_keyboard(lang),
        )
        await callback.answer()
        return

    if currency != "ton" and currency != "stars" and not get_card_requisites(user_id):
        b = EntityBuilder()
        b.add_custom_emoji("deal_cancel_x")
        b.add_text(f" {t(lang, 'deal_create_need_card')}")
        caption, entities = b.result()
        await state.clear()
        await callback.message.edit_caption(
            caption=caption, caption_entities=entities, parse_mode=None,
            reply_markup=back_to_main_menu_keyboard(lang),
        )
        await callback.answer()
        return

    await state.update_data(currency=currency)
    await state.set_state(DealStates.create_waiting_price)
    await state.update_data(panel_chat_id=callback.message.chat.id, panel_message_id=callback.message.message_id)

    info = CURRENCIES[currency]
    step_text = t(lang, "deal_create_ask_price").format(currency_code=info["code"])
    caption, entities = build_deal_creation_step_content(lang, step_text)
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=deal_cancel_only_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(DealStates.create_waiting_price))
async def receive_deal_price(message: Message, state: FSMContext) -> None:
    """Продавец ввёл цену — переходим прямо к шагу ссылки на NFT (минуя описание,
    так как название самого NFT, распознанное из ссылки, и есть описание)."""
    lang = get_user_language(message.from_user.id)
    state_data = await state.get_data()
    currency = state_data.get("currency")
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    try:
        price_text = (message.text or "").strip().replace(",", ".")
        price = float(price_text)
        if price <= 0:
            raise ValueError
    except ValueError:
        try:
            await message.delete()
        except Exception:
            pass
        info = CURRENCIES[currency]
        error_text = t(lang, "deal_create_invalid_price").format(currency_code=info["code"])
        caption, entities = build_deal_creation_step_content(lang, error_text, is_error=True)
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id, message_id=panel_message_id,
                caption=caption, caption_entities=entities, parse_mode=None,
                reply_markup=deal_cancel_only_keyboard(lang),
            )
        return

    min_amount = get_min_deal_amount(currency)
    if price < min_amount:
        try:
            await message.delete()
        except Exception:
            pass
        info = CURRENCIES[currency]
        error_text = t(lang, "deal_create_below_minimum").format(
            min_amount=format_amount(min_amount), currency_code=info["code"],
        )
        caption, entities = build_deal_creation_step_content(lang, error_text, is_error=True)
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id, message_id=panel_message_id,
                caption=caption, caption_entities=entities, parse_mode=None,
                reply_markup=deal_cancel_only_keyboard(lang),
            )
        return

    try:
        await message.delete()
    except Exception:
        pass

    await state.update_data(price=price)
    await state.set_state(DealStates.create_waiting_nft_link)

    b = EntityBuilder()
    b.add_custom_emoji("btn_create_deal")
    b.add_text(" ")
    bold_start = b.start_span()
    b.add_text(t(lang, "deal_create_title"))
    b.close_span("bold", bold_start)
    b.add_text("\n\n")
    b.add_custom_emoji("deal_create_envelope")
    b.add_text(f" {t(lang, 'deal_create_ask_nft_link')}\n\n")
    code_start = b.start_span()
    b.add_text(t(lang, "deal_create_nft_link_example"))
    b.close_span("code", code_start)
    caption, entities = b.result()

    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id, message_id=panel_message_id,
            caption=caption, caption_entities=entities, parse_mode=None,
            reply_markup=deal_cancel_only_keyboard(lang),
        )


@router.message(StateFilter(DealStates.create_waiting_nft_link))
async def receive_deal_nft_link(message: Message, state: FSMContext) -> None:
    """
    Продавец прислал ссылку на NFT — создаём сделку (описание автоматически
    заполняется распознанным из ссылки названием NFT) и показываем итоговый
    deep-link для покупателя.
    """
    lang = get_user_language(message.from_user.id)
    state_data = await state.get_data()
    currency = state_data.get("currency")
    price = state_data.get("price")
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    nft_link = (message.text or "").strip()

    if not nft_link:
        try:
            await message.delete()
        except Exception:
            pass
        error_text = t(lang, "deal_create_nft_link_required")
        caption, entities = build_deal_creation_step_content(lang, error_text, is_error=True)
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id, message_id=panel_message_id,
                caption=caption, caption_entities=entities, parse_mode=None,
                reply_markup=deal_cancel_only_keyboard(lang),
            )
        return

    description = extract_nft_name_from_link(nft_link) or ""

    try:
        await message.delete()
    except Exception:
        pass

    deal_id = create_deal(message.from_user.id, currency, price, description, nft_link)
    deal = get_deal(deal_id)
    info = CURRENCIES[currency]

    bot_info = await message.bot.get_me()
    deal_link = f"https://t.me/{bot_info.username}?start=deal_{deal_id}"

    b = EntityBuilder()
    b.add_custom_emoji("shield")
    b.add_text(f" {t(lang, 'deal_created_title')}\n\n")

    b.add_custom_emoji("deal_create_coin")
    b.add_text(f" {t(lang, 'deal_created_amount_label')}: {format_amount(price)} {info['symbol']}\n\n")

    if description:
        b.add_custom_emoji("deal_create_gift")
        b.add_text(f" {t(lang, 'deal_created_nft_label')}: ")
        link_start = b.start_span()
        b.add_text(t(lang, "deal_created_nft_view_text"))
        b.close_span("text_link", link_start, url=nft_link)
        b.add_text("\n\n")

    b.add_text(f"{t(lang, 'deal_created_buyer_link_label')}:\n")
    b.add_custom_emoji("deal_create_link")
    b.add_text(" ")
    code_start = b.start_span()
    b.add_text(deal_link)
    b.close_span("code", code_start)

    caption, entities = b.result()

    await state.clear()
    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id, message_id=panel_message_id,
            caption=caption, caption_entities=entities, parse_mode=None,
            reply_markup=deal_detail_keyboard(lang, deal, message.from_user.id, show_back=False),
        )


async def attempt_join_deal(user_id: int, deal_code: str) -> tuple[bool, str, dict | None]:
    """
    Логика попытки присоединения к сделке по коду — вызывается ТОЛЬКО при
    переходе по deep-link (cmd_start с параметром deal_XXXXXX). Ручного ввода
    кода в боте нет — единственный способ присоединиться к сделке — перейти
    по ссылке, которую формирует create_deal.

    Баланс НЕ проверяется здесь — присоединиться можно не имея средств,
    оплата (и проверка баланса) происходит отдельно при нажатии "Оплатить".

    Возвращает (успех, ключ_перевода_причины_отказа_или_пустая_строка,
    итоговые_данные_сделки_или_None). Отправка уведомлений — обязанность
    вызывающего кода, не этой функции.
    """
    deal = get_deal(deal_code)

    if deal is None:
        return False, "deal_join_not_found", None

    if deal["status"] != "created":
        return False, "deal_join_wrong_status", None

    if deal["seller_id"] == user_id:
        return False, "deal_join_own_deal", None

    joined = join_deal(deal["deal_id"], user_id)
    if not joined:
        return False, "deal_join_wrong_status", None

    updated_deal = get_deal(deal["deal_id"])
    return True, "", updated_deal


@router.callback_query(F.data == "menu:my_deals")
async def open_my_deals(callback: CallbackQuery, state: FSMContext) -> None:
    """Открываем список "Мои сделки" — фото остаётся тем же, меняется caption и кнопки."""
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    deals = list_user_deals(callback.from_user.id)
    caption, entities = build_deals_list_content(lang, deals)

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=deals_list_keyboard(lang, deals),
    )
    await callback.answer()


@router.callback_query(F.data == "deal:back_to_list")
async def back_to_deals_list(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат в список "Мои сделки" из карточки сделки или из любого промежуточного шага."""
    await open_my_deals(callback, state)


@router.callback_query(F.data.startswith("deal:view:"))
async def view_deal(callback: CallbackQuery, state: FSMContext) -> None:
    """Открываем карточку конкретной сделки — доступно только её участникам."""
    await state.clear()
    deal_id = callback.data.split(":")[2]
    deal = get_deal(deal_id)
    lang = get_user_language(callback.from_user.id)

    if not deal or callback.from_user.id not in (deal["seller_id"], deal["buyer_id"]):
        await callback.answer(t(lang, "panel_no_access"), show_alert=True)
        return

    caption, entities = build_deal_detail_content(lang, deal, callback.from_user.id)
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=deal_detail_keyboard(lang, deal, callback.from_user.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("deal:cancel:"))
async def cancel_deal_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Отмена сделки любой из сторон (доступно только в статусах created/joined).
    При отмене из joined размораживается баланс покупателя.
    """
    deal_id = callback.data.split(":")[2]
    deal = get_deal(deal_id)
    lang = get_user_language(callback.from_user.id)

    if not deal or callback.from_user.id not in (deal["seller_id"], deal["buyer_id"]):
        await callback.answer(t(lang, "panel_no_access"), show_alert=True)
        return

    cancelled = cancel_deal(deal_id)
    if not cancelled:
        await callback.answer(t(lang, "deal_join_wrong_status"), show_alert=True)
        return

    text = t(lang, "deal_cancel_confirm")
    b = EntityBuilder()
    b.add_custom_emoji("deal_pay_confirm")
    b.add_text(f" {text}")
    caption, entities = b.result()
    await callback.message.edit_caption(
        caption=caption, caption_entities=entities, parse_mode=None,
        reply_markup=deal_final_completed_keyboard(lang),
    )
    await callback.answer()

    other_id = deal["buyer_id"] if callback.from_user.id == deal["seller_id"] else deal["seller_id"]
    if other_id:
        other_lang = get_user_language(other_id)
        canceller_role = t(other_lang, "deal_role_seller") if callback.from_user.id == deal["seller_id"] else t(
            other_lang, "deal_role_buyer")
        notify_text = t(other_lang, "deal_cancelled_notify_other").format(role=canceller_role)
        notify_b = EntityBuilder()
        notify_b.add_custom_emoji("deal_pay_confirm")
        notify_b.add_text(f" {notify_text}")
        notify_caption, notify_entities = notify_b.result()
        try:
            notify_photo = get_main_menu_photo()
            await callback.bot.send_photo(
                chat_id=other_id, photo=notify_photo,
                caption=notify_caption, caption_entities=notify_entities, parse_mode=None,
                reply_markup=deal_final_completed_keyboard(other_lang),
            )
        except Exception:
            pass


@router.callback_query(F.data.startswith("deal:pay:"))
async def pay_for_deal_handler(callback: CallbackQuery) -> None:
    """
    Покупатель нажимает "Оплатить" — здесь, а не при присоединении, впервые
    проверяется баланс. При успехе деньги переходят продавцу (с заморозкой
    у него до завершения сделки), статус joined -> paid.
    """
    deal_id = callback.data.split(":")[2]
    deal = get_deal(deal_id)
    lang = get_user_language(callback.from_user.id)

    if not deal or callback.from_user.id != deal["buyer_id"]:
        await callback.answer(t(lang, "panel_no_access"), show_alert=True)
        return

    info = CURRENCIES[deal["currency"]]
    success, reason = pay_for_deal(deal_id)

    if not success:
        if reason == "insufficient_balance":
            available = get_available_balance(callback.from_user.id, deal["currency"])
            await callback.answer(
                t(lang, "deal_pay_insufficient_balance").format(
                    available=format_amount(available), symbol=info["symbol"],
                    price=format_amount(deal["price"]),
                ),
                show_alert=True,
            )
        else:
            await callback.answer(t(lang, "deal_pay_wrong_status"), show_alert=True)
        return

    updated_deal = get_deal(deal_id)

    buyer_caption, buyer_entities = build_deal_paid_buyer_content(lang)
    await callback.message.edit_caption(
        caption=buyer_caption, caption_entities=buyer_entities, parse_mode=None,
        reply_markup=deal_detail_keyboard(lang, updated_deal, callback.from_user.id, show_back=False),
    )
    await callback.answer()

    seller_lang = get_user_language(updated_deal["seller_id"])
    seller_caption, seller_entities = build_deal_paid_seller_content(seller_lang)
    try:
        seller_photo = get_main_menu_photo()
        await callback.bot.send_photo(
            chat_id=updated_deal["seller_id"], photo=seller_photo,
            caption=seller_caption, caption_entities=seller_entities, parse_mode=None,
            reply_markup=deal_seller_paid_keyboard(deal_id, seller_lang),
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("deal:confirm_sent:"))
async def confirm_deal_sent(callback: CallbackQuery) -> None:
    """
    Продавец подтверждает, что отправил NFT-подарок на аккаунт гаранта
    (paid -> sent). После этого отмена сделки уже недоступна (впрочем, она
    уже была недоступна с момента paid).
    """
    deal_id = callback.data.split(":")[2]
    deal = get_deal(deal_id)
    lang = get_user_language(callback.from_user.id)

    if not deal or callback.from_user.id != deal["seller_id"]:
        await callback.answer(t(lang, "panel_no_access"), show_alert=True)
        return

    marked = mark_deal_sent(deal_id)
    if not marked:
        await callback.answer(t(lang, "deal_join_wrong_status"), show_alert=True)
        return

    updated_deal = get_deal(deal_id)

    b = EntityBuilder()
    b.add_custom_emoji("deal_paid_check")
    b.add_text(f" {t(lang, 'deal_sent_seller_accepted')}\n")
    b.add_custom_emoji("deal_sent_seller_person")
    b.add_text(f" {t(lang, 'deal_sent_seller_transferred')}\n")
    b.add_custom_emoji("deal_paid_clock")
    b.add_text(f" {t(lang, 'deal_sent_seller_wait_verification')}\n")
    b.add_custom_emoji("deal_join_seller_pin")
    b.add_text(f" {t(lang, 'deal_sent_seller_buyer_notified')}")
    full_caption, full_entities = b.result()

    await callback.message.edit_caption(
        caption=full_caption, caption_entities=full_entities, parse_mode=None,
        reply_markup=None,
    )
    set_seller_sent_message_id(deal_id, callback.message.message_id)
    await callback.answer()

    if updated_deal["buyer_id"]:
        buyer_lang = get_user_language(updated_deal["buyer_id"])
        b = EntityBuilder()
        b.add_custom_emoji("deal_pay_confirm")
        b.add_text(f" {t(buyer_lang, 'deal_buyer_confirm_delivery_notice')}")
        notify_caption, notify_entities = b.result()
        try:
            notify_photo = get_main_menu_photo()
            await callback.bot.send_photo(
                chat_id=updated_deal["buyer_id"], photo=notify_photo,
                caption=notify_caption, caption_entities=notify_entities, parse_mode=None,
                reply_markup=deal_buyer_confirm_transfer_keyboard(deal_id, buyer_lang),
            )
        except Exception:
            pass


@router.callback_query(F.data.startswith("deal:confirm_received:"))
async def confirm_deal_received(callback: CallbackQuery) -> None:
    """
    Покупатель подтверждает получение NFT-подарка (sent -> completed) —
    замороженные средства окончательно переводятся продавцу. Обеим сторонам
    РЕДАКТИРУЕТСЯ их текущее сообщение (с тем же фото) на единый финальный
    текст — не отправляется отдельное новое сообщение поверх старого.
    """
    deal_id = callback.data.split(":")[2]
    deal = get_deal(deal_id)
    lang = get_user_language(callback.from_user.id)

    if not deal or callback.from_user.id != deal["buyer_id"]:
        await callback.answer(t(lang, "panel_no_access"), show_alert=True)
        return

    completed = complete_deal(deal_id)
    if not completed:
        await callback.answer(t(lang, "deal_join_wrong_status"), show_alert=True)
        return

    updated_deal = get_deal(deal_id)
    await callback.answer()

    buyer_lang = get_user_language(updated_deal["buyer_id"])
    seller_lang = get_user_language(updated_deal["seller_id"])

    buyer_b = EntityBuilder()
    buyer_b.add_custom_emoji("shield")
    buyer_b.add_text(f" {t(buyer_lang, 'deal_final_completed_message')}")
    buyer_caption, buyer_entities = buyer_b.result()
    try:
        await callback.message.edit_caption(
            caption=buyer_caption, caption_entities=buyer_entities, parse_mode=None,
            reply_markup=deal_final_completed_keyboard(buyer_lang),
        )
    except Exception:
        pass

    seller_b = EntityBuilder()
    seller_b.add_custom_emoji("shield")
    seller_b.add_text(f" {t(seller_lang, 'deal_final_completed_message')}")
    seller_caption, seller_entities = seller_b.result()
    if updated_deal.get("seller_sent_message_id"):
        try:
            await callback.bot.edit_message_caption(
                chat_id=updated_deal["seller_id"], message_id=updated_deal["seller_sent_message_id"],
                caption=seller_caption, caption_entities=seller_entities, parse_mode=None,
                reply_markup=deal_final_completed_keyboard(seller_lang),
            )
        except Exception:
            pass
    else:

        try:
            final_photo = get_main_menu_photo()
            await callback.bot.send_photo(
                chat_id=updated_deal["seller_id"], photo=final_photo,
                caption=seller_caption, caption_entities=seller_entities, parse_mode=None,
                reply_markup=deal_final_completed_keyboard(seller_lang),
            )
        except Exception:
            pass


@router.callback_query(F.data == "menu:wallet")
async def open_balance(callback: CallbackQuery, state: FSMContext) -> None:
    """Открываем экран "Кошелёк" — по умолчанию показываем первую валюту в списке (RUB)."""
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    default_currency = CURRENCY_ORDER[0]
    amount = get_balance(callback.from_user.id, default_currency)
    caption, entities = build_balance_content(lang, default_currency, amount, callback.from_user.id)

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=balance_keyboard(lang, default_currency, page=0),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("balance:show:"))
async def switch_currency(callback: CallbackQuery) -> None:
    """Переключаем экран на другую валюту (кнопка из текущей страницы пагинации)."""
    _, _, currency, page_str = callback.data.split(":")
    page = int(page_str)
    lang = get_user_language(callback.from_user.id)
    amount = get_balance(callback.from_user.id, currency)
    caption, entities = build_balance_content(lang, currency, amount, callback.from_user.id)

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=balance_keyboard(lang, currency, page=page),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("balance:page:"))
async def change_page(callback: CallbackQuery) -> None:
    """Переключаем страницу пагинации валют, не меняя текущую выбранную валюту."""
    _, _, currency, page_str = callback.data.split(":")
    page = int(page_str)
    lang = get_user_language(callback.from_user.id)

    await callback.message.edit_reply_markup(
        reply_markup=balance_keyboard(lang, currency, page=page)
    )
    await callback.answer()


@router.callback_query(F.data == "balance:noop")
async def balance_noop(callback: CallbackQuery) -> None:
    """Кнопка-индикатор номера страницы — ничего не делает, просто гасит спиннер."""
    await callback.answer()


@router.callback_query(F.data.startswith("balance:withdraw:"))
async def start_withdraw(callback: CallbackQuery, state: FSMContext) -> None:
    """Пользователь нажал "Вывести" — показываем выбор валюты для вывода (заново, без привязки к валюте, открытой в кошельке)."""
    await state.clear()
    lang = get_user_language(callback.from_user.id)

    b = EntityBuilder()
    b.add_custom_emoji("deal_join_amount")
    b.add_text(f" {t(lang, 'withdraw_ask_currency')}")
    caption, entities = b.result()

    await callback.message.edit_caption(
        caption=caption, caption_entities=entities, parse_mode=None,
        reply_markup=withdraw_currency_keyboard(lang, page=0),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("withdraw:currency_page:"))
async def change_withdraw_currency_page(callback: CallbackQuery) -> None:
    """Переключаем страницу пагинации валют при выборе валюты для вывода."""
    page = int(callback.data.split(":")[2])
    lang = get_user_language(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=withdraw_currency_keyboard(lang, page=page))
    await callback.answer()


@router.callback_query(F.data == "withdraw:noop")
async def withdraw_noop(callback: CallbackQuery) -> None:
    """Кнопка-индикатор страницы — просто гасит спиннер."""
    await callback.answer()


@router.callback_query(F.data == "withdraw:cancel")
async def cancel_withdraw(callback: CallbackQuery, state: FSMContext) -> None:
    """Отмена сценария вывода на любом шаге — возврат в главное меню."""
    await state.clear()
    await back_to_main(callback, state)


@router.callback_query(F.data.startswith("withdraw:currency:"))
async def receive_withdraw_currency(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Пользователь выбрал валюту для вывода. Если доступный баланс в этой
    валюте равен нулю — показываем ошибку с premium-крестиком и просим
    обратиться в поддержку. Иначе просим ввести сумму вывода.
    """
    _, _, currency, _page = callback.data.split(":")
    lang = get_user_language(callback.from_user.id)
    user_id = callback.from_user.id

    available = get_available_balance(user_id, currency)
    if available <= 0:
        b = EntityBuilder()
        b.add_custom_emoji("deal_cancel_x")
        b.add_text(f" {t(lang, 'withdraw_zero_balance_error').format(support_username=SUPPORT_USERNAME)}")
        caption, entities = b.result()
        await callback.message.edit_caption(
            caption=caption, caption_entities=entities, parse_mode=None,
            reply_markup=withdraw_back_only_keyboard(lang),
        )
        await callback.answer()
        return

    await state.update_data(
        currency=currency,
        panel_chat_id=callback.message.chat.id,
        panel_message_id=callback.message.message_id,
    )
    await state.set_state(WithdrawStates.waiting_amount)

    info = CURRENCIES[currency]
    b = EntityBuilder()
    b.add_custom_emoji("deal_join_amount")
    b.add_text(f" {t(lang, 'withdraw_ask_amount')} ")
    b.add_custom_emoji("down_arrow_small")

    caption, entities = b.result()
    await callback.message.edit_caption(
        caption=caption, caption_entities=entities, parse_mode=None,
        reply_markup=withdraw_back_only_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(WithdrawStates.waiting_amount))
async def receive_withdraw_amount(message: Message, state: FSMContext) -> None:
    """
    Пользователь ввёл сумму вывода. Проверяем, что это положительное число
    и что оно не превышает доступный баланс (без отдельной проверки на
    минимум). Затем, если валюта требует реквизитов (карта для всех валют
    кроме TON/Stars, кошелёк для TON) — просим подтвердить их актуальность.
    Для Stars реквизиты не нужны вообще — сразу переходим к подтверждению.
    """
    lang = get_user_language(message.from_user.id)
    state_data = await state.get_data()
    currency = state_data.get("currency")
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")
    user_id = message.from_user.id
    info = CURRENCIES[currency]

    try:
        await message.delete()
    except Exception:
        pass

    try:
        amount = float((message.text or "").strip().replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        b = EntityBuilder()
        b.add_custom_emoji("deal_cancel_x")
        b.add_text(f" {t(lang, 'withdraw_invalid_amount')}")
        caption, entities = b.result()
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id, message_id=panel_message_id,
                caption=caption, caption_entities=entities, parse_mode=None,
                reply_markup=withdraw_back_only_keyboard(lang),
            )
        return

    available = get_available_balance(user_id, currency)
    if amount > available:
        b = EntityBuilder()
        b.add_custom_emoji("deal_cancel_x")
        b.add_text(
            f" {t(lang, 'withdraw_exceeds_balance').format(available=format_amount(available), symbol=info['symbol'])}"
        )
        caption, entities = b.result()
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id, message_id=panel_message_id,
                caption=caption, caption_entities=entities, parse_mode=None,
                reply_markup=withdraw_back_only_keyboard(lang),
            )
        return

    await state.update_data(amount=amount)

    if currency == "stars":
        requisites_text = None
    elif currency == "ton":
        requisites_text = get_wallet_address(user_id)
    else:
        requisites_text = get_card_requisites(user_id)

    b = EntityBuilder()
    b.add_text(f"{t(lang, 'withdraw_confirm_requisites_title')} ")
    b.add_custom_emoji("down_arrow_small")
    if requisites_text:
        b.add_text(f"\n\n{requisites_text}")
    caption, entities = b.result()

    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id, message_id=panel_message_id,
            caption=caption, caption_entities=entities, parse_mode=None,
            reply_markup=withdraw_confirm_requisites_keyboard(lang),
        )


@router.callback_query(F.data == "withdraw:confirm")
async def confirm_withdraw(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Пользователь подтвердил актуальность реквизитов — принимаем заявку на
    вывод. Списываем сумму с доступного баланса немедленно (резервируем её
    под обработку), чтобы пользователь не мог вывести её повторно.
    """
    lang = get_user_language(callback.from_user.id)
    state_data = await state.get_data()
    currency = state_data.get("currency")
    amount = state_data.get("amount")

    if not currency or not amount:
        await state.clear()
        await back_to_main(callback, state)
        return

    adjust_balance(callback.from_user.id, currency, -amount)
    await state.clear()

    info = CURRENCIES[currency]
    b = EntityBuilder()
    b.add_custom_emoji("deal_pay_confirm")
    b.add_text(f" {t(lang, 'withdraw_request_sent').format(amount=format_amount(amount), symbol=info['symbol'])}")
    caption, entities = b.result()

    await callback.message.edit_caption(
        caption=caption, caption_entities=entities, parse_mode=None,
        reply_markup=deal_final_completed_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:requisites")
async def open_requisites(callback: CallbackQuery, state: FSMContext) -> None:
    """Открываем раздел "Управление реквизитами" — фото остаётся тем же, меняется caption и кнопки."""
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    caption, entities = build_requisites_content(lang)

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=requisites_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "requisites:edit_wallet")
async def open_wallet_screen(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Открываем экран управления кошельком:
    - если адреса ещё нет — показываем экран "Добавьте ваш кошелек"
    - если уже есть — показываем текущий адрес и предложение его изменить
    В обоих случаях переходим в состояние ожидания текста с новым адресом.
    """
    lang = get_user_language(callback.from_user.id)
    existing = get_wallet_address(callback.from_user.id)

    if existing:
        caption, entities = build_wallet_current_content(lang, existing)
    else:
        caption, entities = build_wallet_add_content(lang)

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=wallet_screen_keyboard(),
    )
    await state.set_state(RequisitesStates.waiting_for_wallet)
    await state.update_data(
        menu_chat_id=callback.message.chat.id,
        menu_message_id=callback.message.message_id,
    )
    await callback.answer()


@router.callback_query(F.data == "requisites:edit_card")
async def open_card_screen(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Открываем экран управления картой:
    - если реквизитов ещё нет — показываем экран "Добавьте ваши реквизиты"
    - если уже есть — показываем текущие реквизиты и предложение их изменить
    В обоих случаях переходим в состояние ожидания текста с новыми реквизитами.
    """
    lang = get_user_language(callback.from_user.id)
    existing = get_card_requisites(callback.from_user.id)

    if existing:
        caption, entities = build_card_current_content(lang, existing)
    else:
        caption, entities = build_card_add_content(lang)

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=card_screen_keyboard(),
    )
    await state.set_state(RequisitesStates.waiting_for_card)
    await state.update_data(
        menu_chat_id=callback.message.chat.id,
        menu_message_id=callback.message.message_id,
    )
    await callback.answer()


@router.message(StateFilter(RequisitesStates.waiting_for_card))
async def receive_card_requisites(message: Message, state: FSMContext) -> None:
    """
    Принимаем текст с реквизитами карты (без какой-либо проверки формата —
    любой текст сохраняется как есть) и показываем обновлённый экран "текущих
    реквизитов" в том же сообщении с фото, что было отправлено через /start.
    """
    lang = get_user_language(message.from_user.id)
    requisites_text = message.text or ""

    set_card_requisites(message.from_user.id, requisites_text)

    try:
        await message.delete()
    except Exception:
        pass

    caption, entities = build_card_current_content(lang, requisites_text)

    state_data = await state.get_data()
    menu_chat_id = state_data.get("menu_chat_id")
    menu_message_id = state_data.get("menu_message_id")

    if menu_chat_id and menu_message_id:
        await message.bot.edit_message_caption(
            chat_id=menu_chat_id,
            message_id=menu_message_id,
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=card_screen_keyboard(),
        )


@router.message(StateFilter(RequisitesStates.waiting_for_wallet))
async def receive_wallet_address(message: Message, state: FSMContext) -> None:
    """
    Принимаем текст с адресом TON-кошелька (без проверки формата — любой текст
    сохраняется как есть) и показываем обновлённый экран "текущего кошелька"
    в том же сообщении с фото, что было отправлено через /start.
    """
    lang = get_user_language(message.from_user.id)
    address_text = message.text or ""

    set_wallet_address(message.from_user.id, address_text)

    try:
        await message.delete()
    except Exception:
        pass

    caption, entities = build_wallet_current_content(lang, address_text)

    state_data = await state.get_data()
    menu_chat_id = state_data.get("menu_chat_id")
    menu_message_id = state_data.get("menu_message_id")

    if menu_chat_id and menu_message_id:
        await message.bot.edit_message_caption(
            chat_id=menu_chat_id,
            message_id=menu_message_id,
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=wallet_screen_keyboard(),
        )


async def _deny_access(callback: CallbackQuery) -> None:
    lang = get_user_language(callback.from_user.id)
    await callback.answer(t(lang, "panel_no_access"), show_alert=True)


@router.callback_query(F.data == "menu:owner_panel")
async def open_owner_panel(callback: CallbackQuery, state: FSMContext) -> None:
    """Открываем корень OWNER PANEL — доступно только Owner'ам."""
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    caption, entities = build_simple_title_content(t(lang, "panel_owner_title"), "👑")

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=owner_panel_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "panel:owner_root")
async def back_to_owner_root(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат в корень OWNER PANEL из любого подменю (Block/Admins/и т.д.)."""
    await open_owner_panel(callback, state)


@router.callback_query(F.data == "menu:admin_panel")
async def open_admin_panel(callback: CallbackQuery, state: FSMContext) -> None:
    """Открываем корень Админ панели — доступно только назначенным младшим админам."""
    if not is_admin(callback.from_user.id):
        await _deny_access(callback)
        return
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    caption, entities = build_simple_title_content(t(lang, "panel_admin_title"), "🛠")

    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=admin_panel_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "panel:admin_root")
async def back_to_admin_root(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат в корень Админ панели."""
    await open_admin_panel(callback, state)


@router.callback_query(F.data == "panel:cancel")
async def cancel_panel_flow(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Общая отмена любого пошагового сценария панели (ввод цели/суммы/валюты) —
    возвращает в корень той панели, к которой принадлежит пользователь.
    """
    await state.clear()
    if is_owner(callback.from_user.id):
        await open_owner_panel(callback, state)
    elif is_admin(callback.from_user.id):
        await open_admin_panel(callback, state)
    else:
        await _deny_access(callback)


@router.callback_query(F.data == "panel:give_balance")
async def start_give_balance_owner(callback: CallbackQuery, state: FSMContext) -> None:
    """Owner начинает сценарий выдачи баланса — первым шагом просим username/id."""
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    lang = get_user_language(callback.from_user.id)
    await state.update_data(
        target_user_id=None,
        panel_chat_id=callback.message.chat.id,
        panel_message_id=callback.message.message_id,
    )
    await state.set_state(AdminPanelStates.balance_waiting_target)

    caption, entities = build_simple_title_content(t(lang, "panel_ask_target"), "💰")
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=_cancel_only_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "panel:give_balance_self")
async def start_give_balance_self(callback: CallbackQuery, state: FSMContext) -> None:
    """Admin выдаёт/списывает баланс только себе — пропускаем шаг с username, сразу валюта."""
    if not is_admin(callback.from_user.id):
        await _deny_access(callback)
        return
    lang = get_user_language(callback.from_user.id)
    await state.update_data(
        target_user_id=callback.from_user.id,
        panel_chat_id=callback.message.chat.id,
        panel_message_id=callback.message.message_id,
    )
    await state.set_state(AdminPanelStates.balance_waiting_currency)

    caption, entities = build_simple_title_content(t(lang, "panel_ask_currency"), "💰")
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=panel_currency_keyboard(lang, page=0),
    )
    await callback.answer()


@router.message(StateFilter(AdminPanelStates.balance_waiting_target))
async def receive_balance_target(message: Message, state: FSMContext) -> None:
    """Owner присылает username/id того, кому хочет выдать/списать баланс."""
    if not is_owner(message.from_user.id):
        return
    lang = get_user_language(message.from_user.id)
    query = message.text or ""
    target_id = find_user(query)

    try:
        await message.delete()
    except Exception:
        pass

    state_data = await state.get_data()
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    if target_id is None:
        caption, entities = build_simple_title_content(t(lang, "panel_user_not_found"), "❌")
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id,
                message_id=panel_message_id,
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=_cancel_only_keyboard(lang),
            )
        return

    await state.update_data(target_user_id=target_id)
    await state.set_state(AdminPanelStates.balance_waiting_currency)

    caption, entities = build_simple_title_content(t(lang, "panel_ask_currency"), "💰")
    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id,
            message_id=panel_message_id,
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=panel_currency_keyboard(lang, page=0),
        )


@router.callback_query(F.data.startswith("panel:currency_page:"),
                       StateFilter(AdminPanelStates.balance_waiting_currency))
async def change_currency_page(callback: CallbackQuery) -> None:
    """Переключаем страницу пагинации валют в сценарии выдачи баланса."""
    page = int(callback.data.split(":")[2])
    lang = get_user_language(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=panel_currency_keyboard(lang, page=page))
    await callback.answer()


@router.callback_query(F.data == "panel:noop")
async def panel_noop(callback: CallbackQuery) -> None:
    """Кнопка-индикатор страницы в панели — просто гасит спиннер."""
    await callback.answer()


@router.callback_query(F.data.startswith("panel:currency:"), StateFilter(AdminPanelStates.balance_waiting_currency))
async def receive_balance_currency(callback: CallbackQuery, state: FSMContext) -> None:
    """Выбрана валюта — запоминаем и просим сумму."""
    _, _, currency, _page = callback.data.split(":")
    lang = get_user_language(callback.from_user.id)
    await state.update_data(currency=currency)
    await state.set_state(AdminPanelStates.balance_waiting_amount)
    await state.update_data(panel_chat_id=callback.message.chat.id, panel_message_id=callback.message.message_id)

    caption, entities = build_simple_title_content(t(lang, "panel_ask_amount"), "💰")
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=_cancel_only_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(AdminPanelStates.balance_waiting_amount))
async def receive_balance_amount(message: Message, state: FSMContext) -> None:
    """Получили сумму — применяем изменение баланса и показываем результат."""
    lang = get_user_language(message.from_user.id)
    state_data = await state.get_data()
    target_id = state_data.get("target_user_id")
    currency = state_data.get("currency")
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    try:
        amount_text = (message.text or "").strip().replace(",", ".")
        delta = float(amount_text)
    except ValueError:
        try:
            await message.delete()
        except Exception:
            pass
        caption, entities = build_simple_title_content(t(lang, "panel_invalid_amount"), "❌")
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id,
                message_id=panel_message_id,
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=_cancel_only_keyboard(lang),
            )
        return

    is_owner_user = is_owner(message.from_user.id)
    if not is_owner_user and target_id != message.from_user.id:
        await state.clear()
        return

    new_amount = adjust_balance(target_id, currency, delta)

    try:
        await message.delete()
    except Exception:
        pass

    symbol = CURRENCIES[currency]["symbol"]
    target_label = f"#{target_id}"
    text = t(lang, "panel_balance_updated").format(
        target=target_label, delta=format_amount(delta), symbol=symbol, new_amount=format_amount(new_amount)
    )
    caption, entities = build_simple_title_content(text, "✅")

    await state.clear()
    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id,
            message_id=panel_message_id,
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=panel_back_to_root_keyboard(lang, is_owner_user),
        )


@router.callback_query(F.data == "panel:edit_deals_count")
async def start_edit_deals_count_owner(callback: CallbackQuery, state: FSMContext) -> None:
    """Owner начинает сценарий изменения счётчика сделок — просим username/id."""
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    lang = get_user_language(callback.from_user.id)
    await state.update_data(
        target_user_id=None,
        panel_chat_id=callback.message.chat.id,
        panel_message_id=callback.message.message_id,
    )
    await state.set_state(AdminPanelStates.deals_count_waiting_target)

    caption, entities = build_simple_title_content(t(lang, "panel_ask_target"), "🏆")
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=_cancel_only_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "panel:edit_deals_count_self")
async def start_edit_deals_count_self(callback: CallbackQuery, state: FSMContext) -> None:
    """Admin изменяет счётчик сделок только себе — пропускаем шаг с username."""
    if not is_admin(callback.from_user.id):
        await _deny_access(callback)
        return
    lang = get_user_language(callback.from_user.id)
    await state.update_data(
        target_user_id=callback.from_user.id,
        panel_chat_id=callback.message.chat.id,
        panel_message_id=callback.message.message_id,
    )
    await state.set_state(AdminPanelStates.deals_count_waiting_delta)

    caption, entities = build_simple_title_content(t(lang, "panel_ask_deals_count_delta"), "🏆")
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=_cancel_only_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(AdminPanelStates.deals_count_waiting_target))
async def receive_deals_count_target(message: Message, state: FSMContext) -> None:
    """Owner присылает username/id того, кому хочет изменить счётчик сделок."""
    if not is_owner(message.from_user.id):
        return
    lang = get_user_language(message.from_user.id)
    query = message.text or ""
    target_id = find_user(query)

    try:
        await message.delete()
    except Exception:
        pass

    state_data = await state.get_data()
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    if target_id is None:
        caption, entities = build_simple_title_content(t(lang, "panel_user_not_found"), "❌")
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id,
                message_id=panel_message_id,
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=_cancel_only_keyboard(lang),
            )
        return

    await state.update_data(target_user_id=target_id)
    await state.set_state(AdminPanelStates.deals_count_waiting_delta)

    caption, entities = build_simple_title_content(t(lang, "panel_ask_deals_count_delta"), "🏆")
    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id,
            message_id=panel_message_id,
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=_cancel_only_keyboard(lang),
        )


@router.message(StateFilter(AdminPanelStates.deals_count_waiting_delta))
async def receive_deals_count_delta(message: Message, state: FSMContext) -> None:
    """Получили дельту — применяем изменение счётчика успешных сделок и показываем результат."""
    lang = get_user_language(message.from_user.id)
    state_data = await state.get_data()
    target_id = state_data.get("target_user_id")
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    try:
        delta = int((message.text or "").strip())
    except ValueError:
        try:
            await message.delete()
        except Exception:
            pass
        caption, entities = build_simple_title_content(t(lang, "panel_invalid_deals_count_delta"), "❌")
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id,
                message_id=panel_message_id,
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=_cancel_only_keyboard(lang),
            )
        return

    is_owner_user = is_owner(message.from_user.id)
    if not is_owner_user and target_id != message.from_user.id:
        await state.clear()
        return

    adjust_manual_deals_bonus(target_id, delta)
    total = count_successful_deals(target_id)

    try:
        await message.delete()
    except Exception:
        pass

    target_label = f"#{target_id}"
    text = t(lang, "panel_deals_count_updated").format(target=target_label, delta=delta, total=total)
    caption, entities = build_simple_title_content(text, "✅")

    await state.clear()
    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id,
            message_id=panel_message_id,
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=panel_back_to_root_keyboard(lang, is_owner_user),
        )


@router.callback_query(F.data == "panel:edit_freeze")
async def start_edit_freeze(callback: CallbackQuery, state: FSMContext) -> None:
    """Owner начинает сценарий заморозки/разморозки — первым шагом просим username/id."""
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    lang = get_user_language(callback.from_user.id)
    await state.update_data(
        target_user_id=None,
        panel_chat_id=callback.message.chat.id,
        panel_message_id=callback.message.message_id,
    )
    await state.set_state(AdminPanelStates.freeze_waiting_target)

    caption, entities = build_simple_title_content(t(lang, "panel_ask_target"), "❄️")
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=_cancel_only_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(AdminPanelStates.freeze_waiting_target))
async def receive_freeze_target(message: Message, state: FSMContext) -> None:
    """Owner присылает username/id того, кому хочет заморозить/разморозить баланс."""
    if not is_owner(message.from_user.id):
        return
    lang = get_user_language(message.from_user.id)
    query = message.text or ""
    target_id = find_user(query)

    try:
        await message.delete()
    except Exception:
        pass

    state_data = await state.get_data()
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    if target_id is None:
        caption, entities = build_simple_title_content(t(lang, "panel_user_not_found"), "❌")
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id,
                message_id=panel_message_id,
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=_cancel_only_keyboard(lang),
            )
        return

    await state.update_data(target_user_id=target_id)
    await state.set_state(AdminPanelStates.freeze_waiting_currency)

    caption, entities = build_simple_title_content(t(lang, "panel_ask_currency"), "❄️")
    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id,
            message_id=panel_message_id,
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=panel_currency_keyboard(lang, page=0),
        )


@router.callback_query(F.data.startswith("panel:currency_page:"), StateFilter(AdminPanelStates.freeze_waiting_currency))
async def change_freeze_currency_page(callback: CallbackQuery) -> None:
    """Переключаем страницу пагинации валют в сценарии заморозки/разморозки."""
    page = int(callback.data.split(":")[2])
    lang = get_user_language(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=panel_currency_keyboard(lang, page=page))
    await callback.answer()


@router.callback_query(F.data.startswith("panel:currency:"), StateFilter(AdminPanelStates.freeze_waiting_currency))
async def receive_freeze_currency(callback: CallbackQuery, state: FSMContext) -> None:
    """Выбрана валюта — запоминаем и просим дельту заморозки."""
    _, _, currency, _page = callback.data.split(":")
    lang = get_user_language(callback.from_user.id)
    await state.update_data(currency=currency)
    await state.set_state(AdminPanelStates.freeze_waiting_delta)
    await state.update_data(panel_chat_id=callback.message.chat.id, panel_message_id=callback.message.message_id)

    info = CURRENCIES[currency]
    step_text = t(lang, "panel_ask_freeze_delta").format(currency_code=info["code"])
    caption, entities = build_simple_title_content(step_text, "❄️")
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=_cancel_only_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(AdminPanelStates.freeze_waiting_delta))
async def receive_freeze_delta(message: Message, state: FSMContext) -> None:
    """
    Получили дельту — тихо применяем изменение заморозки (reserved) без
    каких-либо уведомлений пользователю, чьего баланса это касается.
    """
    lang = get_user_language(message.from_user.id)
    state_data = await state.get_data()
    target_id = state_data.get("target_user_id")
    currency = state_data.get("currency")
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    try:
        delta_text = (message.text or "").strip().replace(",", ".")
        delta = float(delta_text)
    except ValueError:
        try:
            await message.delete()
        except Exception:
            pass
        caption, entities = build_simple_title_content(t(lang, "panel_invalid_freeze_delta"), "❌")
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id,
                message_id=panel_message_id,
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=_cancel_only_keyboard(lang),
            )
        return

    if not is_owner(message.from_user.id):
        await state.clear()
        return

    new_reserved = adjust_reserved_balance(target_id, currency, delta)

    try:
        await message.delete()
    except Exception:
        pass

    symbol = CURRENCIES[currency]["symbol"]
    target_label = f"#{target_id}"
    text = t(lang, "panel_freeze_updated").format(
        target=target_label, delta=format_amount(delta), symbol=symbol, total=format_amount(new_reserved)
    )
    caption, entities = build_simple_title_content(text, "✅")

    await state.clear()
    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id,
            message_id=panel_message_id,
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=panel_back_to_root_keyboard(lang, True),
        )


@router.callback_query(F.data == "panel:block_menu")
async def open_block_menu(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    caption, entities = build_simple_title_content(t(lang, "panel_block_menu_title"), "🚫")
    await callback.message.edit_caption(
        caption=caption, caption_entities=entities, parse_mode=None,
        reply_markup=panel_block_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data.in_({"panel:block_user", "panel:unblock_user"}))
async def start_block_flow(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    lang = get_user_language(callback.from_user.id)
    action = "block" if callback.data == "panel:block_user" else "unblock"
    await state.update_data(block_action=action, panel_chat_id=callback.message.chat.id,
                            panel_message_id=callback.message.message_id)
    await state.set_state(
        AdminPanelStates.block_waiting_target if action == "block" else AdminPanelStates.unblock_waiting_target
    )
    caption, entities = build_simple_title_content(t(lang, "panel_ask_target"), "🚫")
    await callback.message.edit_caption(
        caption=caption, caption_entities=entities, parse_mode=None,
        reply_markup=_cancel_only_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(AdminPanelStates.block_waiting_target, AdminPanelStates.unblock_waiting_target))
async def receive_block_target(message: Message, state: FSMContext) -> None:
    if not is_owner(message.from_user.id):
        return
    lang = get_user_language(message.from_user.id)
    state_data = await state.get_data()
    action = state_data.get("block_action", "block")
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    target_id = find_user(message.text or "")
    try:
        await message.delete()
    except Exception:
        pass

    if target_id is None:
        caption, entities = build_simple_title_content(t(lang, "panel_user_not_found"), "❌")
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id, message_id=panel_message_id,
                caption=caption, caption_entities=entities, parse_mode=None,
                reply_markup=_cancel_only_keyboard(lang),
            )
        return

    set_blocked(target_id, action == "block")
    key = "panel_blocked_done" if action == "block" else "panel_unblocked_done"
    text = t(lang, key).format(target=f"#{target_id}")
    caption, entities = build_simple_title_content(text, "✅")

    await state.clear()
    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id, message_id=panel_message_id,
            caption=caption, caption_entities=entities, parse_mode=None,
            reply_markup=panel_back_to_root_keyboard(lang, True),
        )


@router.callback_query(F.data == "panel:view_requisites")
async def start_view_requisites_flow(callback: CallbackQuery, state: FSMContext) -> None:
    """Owner начинает сценарий просмотра реквизитов — просим username/id."""
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    lang = get_user_language(callback.from_user.id)
    await state.update_data(panel_chat_id=callback.message.chat.id, panel_message_id=callback.message.message_id)
    await state.set_state(AdminPanelStates.view_requisites_waiting_target)

    caption, entities = build_simple_title_content(t(lang, "panel_ask_target"), "🔎")
    await callback.message.edit_caption(
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=_cancel_only_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(AdminPanelStates.view_requisites_waiting_target))
async def receive_view_requisites_target(message: Message, state: FSMContext) -> None:
    """Получили username/id — показываем сохранённые реквизиты карты и TON-кошелька."""
    if not is_owner(message.from_user.id):
        return
    lang = get_user_language(message.from_user.id)
    state_data = await state.get_data()
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    target_id = find_user(message.text or "")
    try:
        await message.delete()
    except Exception:
        pass

    if target_id is None:
        caption, entities = build_simple_title_content(t(lang, "panel_user_not_found"), "❌")
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id, message_id=panel_message_id,
                caption=caption, caption_entities=entities, parse_mode=None,
                reply_markup=_cancel_only_keyboard(lang),
            )
        return

    card = get_card_requisites(target_id)
    wallet = get_wallet_address(target_id)
    not_set = t(lang, "panel_requisites_not_set")

    title = t(lang, "panel_requisites_title").format(target=f"#{target_id}")
    body = (
        f"{title}\n\n"
        f"{t(lang, 'panel_requisites_card')}: {card or not_set}\n"
        f"{t(lang, 'panel_requisites_wallet')}: {wallet or not_set}"
    )
    caption, entities = build_simple_title_content(body, "")

    await state.clear()
    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id, message_id=panel_message_id,
            caption=caption, caption_entities=entities, parse_mode=None,
            reply_markup=panel_back_to_root_keyboard(lang, True),
        )


@router.callback_query(F.data == "panel:admins_menu")
async def open_admins_menu(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    caption, entities = build_simple_title_content(t(lang, "panel_admins_menu_title"), "👤")
    await callback.message.edit_caption(
        caption=caption, caption_entities=entities, parse_mode=None,
        reply_markup=panel_admins_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data.in_({"panel:add_admin", "panel:remove_admin"}))
async def start_admin_management_flow(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    lang = get_user_language(callback.from_user.id)
    action = "add" if callback.data == "panel:add_admin" else "remove"
    await state.update_data(admin_action=action, panel_chat_id=callback.message.chat.id,
                            panel_message_id=callback.message.message_id)
    await state.set_state(
        AdminPanelStates.add_admin_waiting_target if action == "add" else AdminPanelStates.remove_admin_waiting_target
    )
    caption, entities = build_simple_title_content(t(lang, "panel_ask_target"), "👤")
    await callback.message.edit_caption(
        caption=caption, caption_entities=entities, parse_mode=None,
        reply_markup=_cancel_only_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(AdminPanelStates.add_admin_waiting_target, AdminPanelStates.remove_admin_waiting_target))
async def receive_admin_target(message: Message, state: FSMContext) -> None:
    if not is_owner(message.from_user.id):
        return
    lang = get_user_language(message.from_user.id)
    state_data = await state.get_data()
    action = state_data.get("admin_action", "add")
    panel_chat_id = state_data.get("panel_chat_id", message.chat.id)
    panel_message_id = state_data.get("panel_message_id")

    target_id = find_user(message.text or "")
    try:
        await message.delete()
    except Exception:
        pass

    if target_id is None:
        caption, entities = build_simple_title_content(t(lang, "panel_user_not_found"), "❌")
        if panel_message_id:
            await message.bot.edit_message_caption(
                chat_id=panel_chat_id, message_id=panel_message_id,
                caption=caption, caption_entities=entities, parse_mode=None,
                reply_markup=_cancel_only_keyboard(lang),
            )
        return

    if action == "add":
        conn = db_connect()
        row = conn.execute("SELECT username FROM users WHERE user_id = ?", (target_id,)).fetchone()
        conn.close()
        target_username = row[0] if row else None
        add_admin(target_id, target_username, added_by=message.from_user.id)
        key = "panel_admin_added"
    else:
        remove_admin(target_id)
        key = "panel_admin_removed"

    text = t(lang, key).format(target=f"#{target_id}")
    caption, entities = build_simple_title_content(text, "✅")

    await state.clear()
    if panel_message_id:
        await message.bot.edit_message_caption(
            chat_id=panel_chat_id, message_id=panel_message_id,
            caption=caption, caption_entities=entities, parse_mode=None,
            reply_markup=panel_back_to_root_keyboard(lang, True),
        )


@router.callback_query(F.data == "panel:list_admins")
async def show_admins_list(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    admins = list_admins()

    if not admins:
        body = t(lang, "panel_admins_list_empty")
    else:
        lines = [f"#{uid} (@{uname})" if uname else f"#{uid}" for uid, uname in admins]
        body = t(lang, "panel_admins_list_title") + "\n" + "\n".join(lines)

    caption, entities = build_simple_title_content(body, "📋")
    await callback.message.edit_caption(
        caption=caption, caption_entities=entities, parse_mode=None,
        reply_markup=panel_back_to_root_keyboard(lang, True),
    )
    await callback.answer()


@router.callback_query(F.data == "panel:stats")
async def show_stats(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_owner(callback.from_user.id):
        await _deny_access(callback)
        return
    await state.clear()
    lang = get_user_language(callback.from_user.id)
    stats = get_stats()

    lines = [
        t(lang, "panel_stats_title"),
        "",
        f"{t(lang, 'panel_stats_total_users')}: {stats['total_users']}",
        f"{t(lang, 'panel_stats_blocked')}: {stats['blocked_count']}",
        f"{t(lang, 'panel_stats_admins_count')}: {len(stats['admins'])}",
        "",
        t(lang, "panel_stats_balances_title"),
    ]
    for currency_key, total in stats["balances_by_currency"].items():
        if currency_key in CURRENCIES:
            info = CURRENCIES[currency_key]
            lines.append(f"{info['emoji']} {info['code']}: {format_amount(total)} {info['symbol']}")

    body = "\n".join(lines)
    caption, entities = build_simple_title_content(body, "📊")
    await callback.message.edit_caption(
        caption=caption, caption_entities=entities, parse_mode=None,
        reply_markup=panel_back_to_root_keyboard(lang, True),
    )
    await callback.answer()


def _describe_callback(data: str) -> str:
    """
    Превращает технический callback_data в человекочитаемое описание действия
    для лога ("выбрал валюту RUB при создании сделки" вместо "deal:currency:rub:0").
    Если префикс неизвестен — возвращает исходные данные как fallback, чтобы
    логирование никогда не "съедало" событие молча.
    """
    parts = data.split(":")
    head = parts[0]

    if data == "menu:wallet":
        return "открыл Кошелёк"
    if data == "menu:requisites":
        return "открыл Управление реквизитами"
    if data == "menu:create_deal":
        return "нажал «Создать сделку»"
    if data == "menu:my_deals":
        return "открыл «Мои сделки»"
    if data == "menu:change_language":
        return "открыл выбор языка"
    if data == "menu:back_to_main":
        return "вернулся в главное меню"
    if data == "menu:owner_panel":
        return "открыл OWNER PANEL"
    if data == "menu:admin_panel":
        return "открыл Админ панель"

    if head == "set_lang" and len(parts) == 2:
        return f"сменил язык интерфейса на {parts[1].upper()}"

    if data == "requisites:edit_card":
        return "открыл редактирование реквизитов карты"
    if data == "requisites:edit_wallet":
        return "открыл редактирование TON-кошелька"

    if head == "balance":
        action = parts[1] if len(parts) > 1 else ""
        if action == "show" and len(parts) >= 3:
            code = CURRENCIES.get(parts[2], {}).get("code", parts[2])
            return f"открыл баланс в валюте {code}"
        if action == "page":
            return "переключил страницу списка валют в кошельке"
        if action == "topup":
            code = CURRENCIES.get(parts[2], {}).get("code", parts[2]) if len(parts) > 2 else "?"
            return f"нажал «Пополнить» ({code})"
        if action == "withdraw":
            return "нажал «Вывести»"
        if action == "noop":
            return None

    if head == "deal":
        action = parts[1] if len(parts) > 1 else ""
        if action == "currency" and len(parts) >= 3:
            code = CURRENCIES.get(parts[2], {}).get("code", parts[2])
            return f"выбрал валюту {code} при создании сделки"
        if action == "currency_page":
            return "переключил страницу выбора валюты при создании сделки"
        if action == "cancel_create":
            return "отменил создание сделки"
        if action == "back_to_list":
            return "вернулся к списку «Мои сделки»"
        if action == "view" and len(parts) >= 3:
            return f"открыл сделку #{parts[2]}"
        if action == "cancel" and len(parts) >= 3:
            return f"отменил сделку #{parts[2]}"
        if action == "pay" and len(parts) >= 3:
            return f"нажал «Оплатить» по сделке #{parts[2]}"
        if action == "confirm_sent" and len(parts) >= 3:
            return f"подтвердил отправку подарка по сделке #{parts[2]}"
        if action == "confirm_received" and len(parts) >= 3:
            return f"подтвердил получение подарка по сделке #{parts[2]}"
        if action == "noop":
            return None

    if head == "withdraw":
        action = parts[1] if len(parts) > 1 else ""
        if action == "currency" and len(parts) >= 3:
            code = CURRENCIES.get(parts[2], {}).get("code", parts[2])
            return f"выбрал валюту {code} для вывода"
        if action == "currency_page":
            return "переключил страницу выбора валюты при выводе"
        if action == "cancel":
            return "отменил сценарий вывода"
        if action == "confirm":
            return "подтвердил вывод средств"
        if action == "noop":
            return None

    if head == "panel":
        action = parts[1] if len(parts) > 1 else ""
        panel_labels = {
            "give_balance": "открыл «Выдать/списать баланс» (себе/другому)",
            "give_balance_self": "открыл «Выдать/списать баланс себе»",
            "edit_deals_count": "открыл «Изменить успешные сделки» (другому)",
            "edit_deals_count_self": "открыл «Изменить себе успешные сделки»",
            "edit_freeze": "открыл «Заморозка/разморозка баланса»",
            "view_requisites": "открыл «Просмотр реквизитов» пользователя",
            "block_menu": "открыл меню блокировки/разблокировки",
            "block_user": "выбрал «Заблокировать пользователя»",
            "unblock_user": "выбрал «Разблокировать пользователя»",
            "admins_menu": "открыл «Управление админами»",
            "add_admin": "выбрал «Добавить админа»",
            "remove_admin": "выбрал «Убрать админа»",
            "list_admins": "запросил список админов",
            "stats": "открыл «Статистика»",
            "owner_root": "вернулся в корень OWNER PANEL",
            "admin_root": "вернулся в корень Админ панели",
            "cancel": "отменил текущий шаг в панели",
        }
        if action in panel_labels:
            return panel_labels[action]
        if action == "currency" and len(parts) >= 3:
            code = CURRENCIES.get(parts[2], {}).get("code", parts[2])
            return f"выбрал валюту {code} в панели"
        if action == "currency_page":
            return "переключил страницу выбора валюты в панели"
        if action == "noop":
            return None

    return f"нажал кнопку ({data})"


def _user_label(user_id: int, username: str | None) -> str:
    """Формирует подпись пользователя для лога: @username (id) или просто id, если username нет."""
    return f"@{username} (id {user_id})" if username else f"id {user_id}"


async def log_user_action(bot, user_id: int, username: str | None, action_text: str) -> None:
    """
    Отправляет одну строку лога в LOG_GROUP_ID. Если логирование выключено
    (LOG_GROUP_ID == 0) или отправка не удалась (бот не в группе, группа
    удалена и т.п.) — тихо игнорирует, чтобы сбой логирования никогда не
    мешал основной работе бота.
    """
    if not LOG_GROUP_ID:
        return
    timestamp = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M:%S МСК")
    text = f"🪵 {timestamp}\n{_user_label(user_id, username)} — {action_text}"
    try:
        await bot.send_message(chat_id=LOG_GROUP_ID, text=text)
    except Exception:
        pass


@router.callback_query.outer_middleware()
async def log_callback_middleware(handler, event: CallbackQuery, data: dict):
    """
    Логирует КАЖДОЕ нажатие inline-кнопки (полный охват навигации и
    содержательных действий) — выполняется после block_check_middleware
    (порядок middleware = порядок регистрации), поэтому заблокированные
    пользователи сюда не попадают вообще.
    """
    description = _describe_callback(event.data or "")
    if description is not None:
        await log_user_action(event.bot, event.from_user.id, event.from_user.username, description)
    return await handler(event, data)


@router.message.outer_middleware()
async def log_message_middleware(handler, event: Message, data: dict):
    """
    Логирует текстовые сообщения, отправленные ботом в рамках FSM-сценариев
    (ввод суммы, реквизитов, ссылки на NFT и т.д.) — кроме /start, у которого
    есть собственное более информативное логирование внутри cmd_start.
    Само содержимое сообщения логируется как есть (усечённое, на случай
    длинного текста), без попытки угадать, что это было за поле ввода —
    конкретику легко восстановить по соседним записям лога с тем же временем.
    """
    text = event.text or ""
    if text and not text.startswith("/start"):
        snippet = text if len(text) <= 80 else text[:80] + "…"
        await log_user_action(event.bot, event.from_user.id, event.from_user.username, f"ввёл текст: {snippet!r}")
    return await handler(event, data)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_TOKEN_HERE":
        raise RuntimeError(
            "BOT_TOKEN не задан! Впиши токен от BotFather в начале файла "
            "(переменная BOT_TOKEN) или задай переменную окружения BOT_TOKEN."
        )

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
