#!/usr/bin/python3

import sys
import cgi
import time
import os

ROOT_DIR   = "/home/www/delfin.kyiv.ua"
SEND_EMAIL = 0

SMTPSERV = 'mail.delfin.kyiv.ua'
TOADDR   = 'info@delfin.kyiv.ua'
USERNAME = 'noreply@delfin.kyiv.ua'

MIN_AGE = 2020
MAX_AGE = 2011

GENDER_NAMES = {
    'M': 'хлопчик',
    'W': 'дівчинка',
}

SWIM_NAMES = {
    'rank': 'має спортивний розряд',
    'good': 'впевнено тримається на воді',
    'soso': 'може проплисти декілька метрів',
    'dnot': 'не вміє плавати',
}

RELATION_NAMES = {
    'mama': 'мама',
    'tato': 'тато',
    'baba': 'бабуся',
    'dida': 'дідусь',
    'brat': 'брат',
    'sest': 'сестра',
}


# ---------------------------
def load_env_file(filepath=".env"):
    """
    Проста функція для завантаження .env файлу без сторонніх модулів

    """
    if not os.path.exists(filepath):
        return

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Пропускаємо коментарі та порожні рядки
            if not line or line.startswith("#"):
                continue

            # Розділяємо ключ і значення по першому знаку '='
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'\"")  # прибираємо зайві лапки, якщо є
                # Зберігаємо пароль у змінній середовища
                os.environ[key] = value
#def


# ---------------------------
def now():
    """
    Get current date & time
    like YYYY-MM-DD HH:MM:SS

    """
    lt = time.localtime()
    return (f'{lt.tm_year}-{lt.tm_mon:0>2}-{lt.tm_mday:0>2} '
            f'{lt.tm_hour:0>2}:{lt.tm_min:0>2}:{lt.tm_sec:0>2}')
#def


# ---------------------------
def redirect(url):
    print(f"Location: {url}")
    print()  # обов'язковий порожній рядок
    sys.exit(0)
#def


# ---------------------------
def goto_error():
    redirect("/error/")
#def


# ---------------------------
def format_parent(form, who_field, name_field, mail_field, pho_field):
    """
    Формує рядок опису одного з батьків/родичів на основі полів форми.
    Повертає None, якщо не вказано жодного контактного поля.

    """
    relation = RELATION_NAMES.get(form.getvalue(who_field), 'родич')
    parts = []

    for field in (name_field, mail_field, pho_field):
        value = form.getvalue(field)
        if value:
            parts.append(value)

    if not parts:
        return None

    return relation + ': ' + ', '.join(parts)
#def


# ---------------------------
def send_email(reply_name, reply_mail, subject, body):
    """
    """
    import smtplib
    from email.message import EmailMessage

    # Отримуємо пароль із змінної середовища
    password = os.getenv('SMTP_PASSWORD')  # value from load_env_file() -> os.environ[key] = value
    if not password:
        raise RuntimeError("SMTP_PASSWORD не заданий (перевірте .env файл)")

    msg = EmailMessage()
    msg.set_content(body)

    msg['Subject'] = subject
    msg['From']    = f'FromSite <{USERNAME}>'
    msg['To']      = TOADDR

    if reply_mail:
        if reply_name:
            msg['Reply-to'] = f"{reply_name} <{reply_mail}>"
        else:
            msg['Reply-to'] = f"{reply_mail}"

    smtpObj = smtplib.SMTP(SMTPSERV, 465) # 587
    smtpObj.starttls()
    smtpObj.login(USERNAME, password)
    smtpObj.send_message(msg)           # або smtpObj.sendmail(from, [to], body)
    smtpObj.quit()
#def


# ============== MAIN ======================

load_env_file(os.path.join(ROOT_DIR, ".env"))

data = '\nвід ' + now() + '\n' + '-' * 20 + '\n\n'
form = cgi.FieldStorage()

if form.getvalue('se_bot') != '7':
    goto_error()

child = form.getvalue("tx_child")
if not child:
    goto_error()

year = form.getvalue('se_year')
if   year == 'older':    year = f"старше {MAX_AGE}"
elif year == 'younger':  year = f"молодше {MIN_AGE}"
elif year == '0':        goto_error()
# інакше залишаємо як є (сире значення поля) - навмисно, на випадок
# нового варіанту в формі, якого тут ще не описано

gender = GENDER_NAMES.get(form.getvalue('ra_gender'), "стать дитини не вказано")
swim   = SWIM_NAMES.get(form.getvalue('ra_swim'), "як плаває - не вказали")

preferred_time = form.getvalue('ra_time')  # best time
if preferred_time is None:
    preferred_time = 'не вказано'
else:
    preferred_time = preferred_time + ':00'

subject = child + ' (' + year + ')'
data += gender + ': ' + subject + '\n' + swim + '\n'
data += 'час тренування: ' + preferred_time + '\n'

par1 = format_parent(form, 'se_par1who', 'tx_par1name', 'tx_par1mail', 'tx_par1pho')
if par1:
    data += par1 + '\n'

par2 = format_parent(form, 'se_par2who', 'tx_par2name', 'tx_par2mail', 'tx_par2pho')
if par2:
    data += par2 + '\n'

if form.getvalue('ta_desc'):
    data += 'додатково: ' + form.getvalue('ta_desc') + '\n'

# save to file
try:
    with open("_saved.txt", "a", encoding="utf-8") as fh:
        fh.write(data)
except OSError:
    goto_error()

# send via mail
reply_name = ''
reply_mail = ''
if form.getvalue('tx_par1mail'):
    reply_mail = form.getvalue('tx_par1mail')
    reply_name = form.getvalue('tx_par1name') or ""
elif form.getvalue('tx_par2mail'):
    reply_mail = form.getvalue('tx_par2mail')
    reply_name = form.getvalue('tx_par2name') or ""

if SEND_EMAIL:
    try:
        send_email(reply_name, reply_mail, subject, data)
    except Exception:
        # заявка вже збережена у файл - лист не пройшов, але не валимо
        # весь запит через це; варто додати логування помилки
        pass

redirect("/success/")
