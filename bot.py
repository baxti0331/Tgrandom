import telebot, sqlite3, random, threading, time, os
from telebot import types

# --- Конфигурация ---
^[BOT_TOKEN = os.getenv('BOT_TOKEN')]({"attribution":{"attributableIndex":"0-7"}})
^[OWNER_ID = int(os.getenv('OWNER_ID', '0'))]({"attribution":{"attributableIndex":"0-8"}})
^[bot = telebot.TeleBot(BOT_TOKEN)]({"attribution":{"attributableIndex":"0-9"}})

# --- Инициализация БД ---
^[conn = sqlite3.connect("giveaway.db", check_same_thread=False)]({"attribution":{"attributableIndex":"0-10"}})
^[cur = conn.cursor()]({"attribution":{"attributableIndex":"0-11"}})
cur.executescript("""
^[CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);]({"attribution":{"attributableIndex":"0-12"}})
^[CREATE TABLE IF NOT EXISTS giveaways (]({"attribution":{"attributableIndex":"0-13"}})
  ^[id INTEGER PRIMARY KEY AUTOINCREMENT,]({"attribution":{"attributableIndex":"0-14"}})
  ^[prize TEXT, photo_url TEXT, max_participants INTEGER, duration INTEGER,]({"attribution":{"attributableIndex":"0-15"}})
  ^[created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, finished INTEGER DEFAULT 0]({"attribution":{"attributableIndex":"0-16"}})
);
^[CREATE TABLE IF NOT EXISTS giveaway_participants (]({"attribution":{"attributableIndex":"0-17"}})
  ^[giveaway_id INTEGER, user_id INTEGER,]({"attribution":{"attributableIndex":"0-18"}})
  ^[PRIMARY KEY (giveaway_id, user_id)]({"attribution":{"attributableIndex":"0-19"}})
);
^[CREATE TABLE IF NOT EXISTS winners (]({"attribution":{"attributableIndex":"0-20"}})
  ^[giveaway_id INTEGER, user_id INTEGER, prize TEXT, photo_url TEXT,]({"attribution":{"attributableIndex":"0-21"}})
  ^[won_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP]({"attribution":{"attributableIndex":"0-22"}})
);
""")
conn.commit()

# --- Функции БД ---
^[def set_channel(c): cur.execute("REPLACE INTO settings VALUES(?,?)", ('channel', c)); conn.commit()]({"attribution":{"attributableIndex":"0-23"}})
^[def get_channel(): cur.execute("SELECT value FROM settings WHERE key='channel'"); r=cur.fetchone(); return r[0] if r else None]({"attribution":{"attributableIndex":"0-24"}})
^[def create_giveaway(prize, photo_url, max_p, duration): cur.execute("INSERT INTO giveaways(prize,photo_url,max_participants,duration) VALUES(?,?,?,?)",(prize,photo_url,max_p,duration)); conn.commit(); return cur.lastrowid]({"attribution":{"attributableIndex":"0-25"}})
^[def get_active(): cur.execute("SELECT id,prize,photo_url,max_participants FROM giveaways WHERE finished=0"); return cur.fetchall()]({"attribution":{"attributableIndex":"0-26"}})
^[def get_participants(gid): cur.execute("SELECT user_id FROM giveaway_participants WHERE giveaway_id=?", (gid,)); return [r[0] for r in cur.fetchall()]]({"attribution":{"attributableIndex":"0-27"}})
^[def add_participant(gid, uid): cur.execute("INSERT OR IGNORE INTO giveaway_participants(giveaway_id,user_id) VALUES(?,?)",(gid,uid)); conn.commit()]({"attribution":{"attributableIndex":"0-28"}})
^[def finish(gid): cur.execute("UPDATE giveaways SET finished=1 WHERE id=?", (gid,)); conn.commit()]({"attribution":{"attributableIndex":"0-29"}})
^[def get_info(gid): cur.execute("SELECT prize,photo_url,max_participants FROM giveaways WHERE id=?", (gid,)); return cur.fetchone()]({"attribution":{"attributableIndex":"0-30"}})
^[def record_winner(gid, uid, prize, photo_url): cur.execute("INSERT INTO winners VALUES(?,?,?,?)",(gid,uid,prize,photo_url)); conn.commit()]({"attribution":{"attributableIndex":"0-31"}})
^[def get_winners(limit=10): cur.execute("SELECT user_id,prize,photo_url,won_at FROM winners ORDER BY won_at DESC LIMIT ?", (limit,)); return cur.fetchall()]({"attribution":{"attributableIndex":"0-32"}})
^[def get_stats(): cur.execute("SELECT COUNT(*) FROM giveaways"); g=cur.fetchone()[0]; cur.execute("SELECT COUNT(*) FROM giveaway_participants"); p=cur.fetchone()[0]; cur.execute("SELECT COUNT(*) FROM winners"); w=cur.fetchone()[0]; return g,p,w]({"attribution":{"attributableIndex":"0-33"}})

# --- Подписка ---
^[def check_sub(uid):]({"attribution":{"attributableIndex":"0-34"}})
    channel = get_channel()
    ^[if not channel: return True]({"attribution":{"attributableIndex":"0-35"}})
    ^[try: return bot.get_chat_member(channel, uid).status in ['member','creator','administrator']]({"attribution":{"attributableIndex":"0-36"}})
    ^[except: return False]({"attribution":{"attributableIndex":"0-37"}})

# --- Авто‑завершение ---
^[def auto_finish(gid, prize, photo_url, delay):]({"attribution":{"attributableIndex":"0-38"}})
    ^[time.sleep(delay*60)]({"attribution":{"attributableIndex":"0-39"}})
    ^[users = get_participants(gid)]({"attribution":{"attributableIndex":"0-40"}})
    finish(gid)
    channel = get_channel()
    ^[if not users:]({"attribution":{"attributableIndex":"0-41"}})
        ^[bot.send_message(channel, f"⛔ Розыгрыш «{prize}» завершён: участников нет.")]({"attribution":{"attributableIndex":"0-42"}})
        return
    ^[winner = random.choice(users)]({"attribution":{"attributableIndex":"0-43"}})
    ^[record_winner(gid, winner, prize, photo_url)]({"attribution":{"attributableIndex":"0-44"}})
    if photo_url:
        ^[bot.send_photo(channel, photo=photo_url, caption=f"🎉 Завершён! 🏆 {prize}]({"attribution":{"attributableIndex":"0-45"}})\n^[👑 Победитель: [user](tg://user?id={winner})", parse_mode='Markdown')]({"attribution":{"attributableIndex":"0-46"}})
    else:
        ^[bot.send_message(channel, f"🎉 Завершён! 🏆 {prize}]({"attribution":{"attributableIndex":"0-47"}})\n^[👑 Победитель: [user](tg://user?id={winner})", parse_mode='Markdown')]({"attribution":{"attributableIndex":"0-48"}})

# --- Хендлеры ---
^[@bot.message_handler(commands=['start'])]({"attribution":{"attributableIndex":"0-49"}})
^[def cmd_start(m): bot.reply_to(m, "🤖 Giveaway Bot]({"attribution":{"attributableIndex":"0-50"}})\nКоманды:\n^[/create <приз> <макс> <минут> [photo_url]]({"attribution":{"attributableIndex":"0-51"}})\n/status\n/winners\n/stats\n/setchannel @channel")

^[@bot.message_handler(commands=['setchannel'])]({"attribution":{"attributableIndex":"0-52"}})
^[def cmd_set(m):]({"attribution":{"attributableIndex":"0-53"}})
    ^[if m.from_user.id!=OWNER_ID: return bot.reply_to(m, "❌ Только админ")]({"attribution":{"attributableIndex":"0-54"}})
    ^[p=m.text.split()]({"attribution":{"attributableIndex":"0-55"}})
    ^[if len(p)!=2 or not p[1].startswith('@'): return bot.reply_to(m, "Пример: /setchannel @mychan")]({"attribution":{"attributableIndex":"0-56"}})
    ^[set_channel(p[1]); bot.reply_to(m, f"✅ Канал {p[1]}")]({"attribution":{"attributableIndex":"0-57"}})

^[@bot.message_handler(commands=['create'])]({"attribution":{"attributableIndex":"0-58"}})
^[def cmd_create(m):]({"attribution":{"attributableIndex":"0-59"}})
    ^[if m.from_user.id!=OWNER_ID: return bot.reply_to(m, "❌ Только админ")]({"attribution":{"attributableIndex":"0-60"}})
    try:
        ^[parts = m.text.split()]({"attribution":{"attributableIndex":"0-61"}})
        ^[prize, max_p, mins = parts[1], int(parts[2]), int(parts[3])]({"attribution":{"attributableIndex":"0-62"}})
        ^[photo_url = parts[4] if len(parts)>4 else None]({"attribution":{"attributableIndex":"0-63"}})
    ^[except: return bot.reply_to(m, "Пример: /create Телефон 100 60 https://link.to/photo.jpg")]({"attribution":{"attributableIndex":"0-64"}})
    ^[gid = create_giveaway(prize, photo_url, max_p, mins)]({"attribution":{"attributableIndex":"0-65"}})
    ^[kb = types.InlineKeyboardMarkup(); kb.add(types.InlineKeyboardButton("🎟 Участвовать",callback_data=f"join_{gid}"))]({"attribution":{"attributableIndex":"0-66"}})
    ^[sent = bot.send_message(get_channel() or m.chat.id, f"🎉 Новый розыгрыш!]({"attribution":{"attributableIndex":"0-67"}})\n🏆 {prize}\n👥 {max_p} мест\n^[⌛ {mins} минут", reply_markup=kb)]({"attribution":{"attributableIndex":"0-68"}})
    ^[if photo_url: bot.send_photo(sent.chat.id, photo=photo_url)]({"attribution":{"attributableIndex":"0-69"}})
    ^[threading.Thread(target=auto_finish, args=(gid,prize,photo_url,mins),daemon=True).start()]({"attribution":{"attributableIndex":"0-70"}})
    ^[bot.reply_to(m, f"✅ Создан, ID {gid}")]({"attribution":{"attributableIndex":"0-71"}})

^[@bot.message_handler(commands=['status'])]({"attribution":{"attributableIndex":"0-72"}})
^[def cmd_status(m):]({"attribution":{"attributableIndex":"0-73"}})
    active = get_active()
    ^[if not active: return bot.reply_to(m, "Нет активных")]({"attribution":{"attributableIndex":"0-74"}})
    txt="🎁 Активные:\n"
    ^[for gid,pr,ph,max_p in active:]({"attribution":{"attributableIndex":"0-75"}})
        ^[txt+=f"• ID{gid}: {pr} — {len(get_participants(gid))}/{max_p}]({"attribution":{"attributableIndex":"0-76"}})\n"
    ^[bot.reply_to(m, txt)]({"attribution":{"attributableIndex":"0-77"}})

^[@bot.message_handler(commands=['winners'])]({"attribution":{"attributableIndex":"0-78"}})
^[def cmd_winners(m):]({"attribution":{"attributableIndex":"0-79"}})
    rec=get_winners()
    ^[if not rec: return bot.reply_to(m,"Пока нет")]({"attribution":{"attributableIndex":"0-80"}})
    txt="🏆 Победители:\n"
    ^[for uid,pr,ph,wh in rec: txt+=f"{wh[:16]} — [user](tg://user?id={uid}) — {pr}]({"attribution":{"attributableIndex":"0-81"}})\n"
    ^[bot.reply_to(m,txt, parse_mode='Markdown')]({"attribution":{"attributableIndex":"0-82"}})

^[@bot.message_handler(commands=['stats'])]({"attribution":{"attributableIndex":"0-83"}})
^[def cmd_stats(m):]({"attribution":{"attributableIndex":"0-84"}})
    ^[g,p,w = get_stats(); bot.reply_to(m, f"📊: розыгрыши {g}, участия {p}, победы {w}")]({"attribution":{"attributableIndex":"0-85"}})

^[@bot.callback_query_handler(lambda c:c.data.startswith('join_'))]({"attribution":{"attributableIndex":"0-86"}})
^[def cb_join(c):]({"attribution":{"attributableIndex":"0-87"}})
    ^[uid, gid = c.from_user.id, int(c.data.split('_')[1])]({"attribution":{"attributableIndex":"0-88"}})
    ^[if not check_sub(uid): return bot.answer_callback_query(c.id, f"Подпишитесь на {get_channel()}", show_alert=True)]({"attribution":{"attributableIndex":"0-89"}})
    ^[users = get_participants(gid)]({"attribution":{"attributableIndex":"0-90"}})
    ^[prize, photo_url, max_p = get_info(gid)]({"attribution":{"attributableIndex":"0-91"}})
    ^[if uid in users: return bot.answer_callback_query(c.id, "✅ Уже участник")]({"attribution":{"attributableIndex":"0-92"}})
    ^[if len(users)>=max_p: return bot.answer_callback_query(c.id, "⚠ Мест нет")]({"attribution":{"attributableIndex":"0-93"}})
    ^[add_participant(gid, uid); bot.answer_callback_query(c.id, "🎉 Вы участвуете")]({"attribution":{"attributableIndex":"0-94"}})
    ^[if len(users)+1>=max_p:]({"attribution":{"attributableIndex":"0-95"}})
        ^[threading.Thread(target=auto_finish, args=(gid,prize,photo_url,0),daemon=True).start()]({"attribution":{"attributableIndex":"0-96"}})
