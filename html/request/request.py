#!/usr/bin/python3

import sys
import cgi
import time
import os

ROOT_DIR  = "/home/www/delfin.kyiv.ua"

# import cgitb
# cgitb.enable(display=0, logdir=ROOT_DIR + '/logs', format="text")  # AJAX
# cgitb.enable(display=1, format="html")  # AJAX , logdir=ROOT_DIR + '/logs'

load_env_file(os.path.join(ROOT_DIR, ".env"))

# ---------------------------
def load_env_file(filepath=".env"):
	"""Проста функція для завантаження .env файлу без сторонніх модулів"""
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
				value = value.strip().strip("'\"") # прибираємо зайві лапки, якщо є
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
	print("Content-type: text/html\n")
	print("<html><head>")
	print(f"<meta http-equiv='Refresh' content='0; URL={url}'>")
	print("<title></title></head><body></body></html>")
	sys.exit(0)
#def


# ---------------------------
def goto_error():
	redirect("/error/")
#def

# ---------------------------
def send_email(reply_name, reply_mail, subject, body):
	"""
	"""
	import smtplib
	from email.message import EmailMessage

	smtpserv = 'mail.delfin.kyiv.ua'
	toaddr   = 'info@delfin.kyiv.ua'
	username = 'noreply@delfin.kyiv.ua'

	# Отримуємо пароль із змінної середовища
	password = os.getenv('SMTP_PASSWORD')  # value from load_env_file() -> os.environ[key] = value
	if not password:
		# На випадок, якщо змінна не задана, щоб скрипт не падав «мовчки»
		pass

	msg = EmailMessage()
	msg.set_content(body)

	msg['Subject'] = subject
	msg['From']    = f'Заявка <{username}>'
	msg['To']      = toaddr

	if reply_mail:
		if reply_name:
			msg['Reply-to'] = f"{reply_name} <{reply_mail}>"
		else:
			msg['Reply-to'] = f"{reply_mail}"

	smtpObj = smtplib.SMTP(smtpserv, 587)
	smtpObj.starttls()
	smtpObj.login(username, password) # якщо вимагає сервер
	smtpObj.send_message(msg)  # або smtpObj.sendmail(from, [to], body)
	smtpObj.quit()
#def




# ============== MAIN ======================

data = '\nвід ' + now() + '\n' + '-' * 20 + '\n\n'
form = cgi.FieldStorage()

if form.getvalue('se_bot') == '7':

	child = form.getvalue("tx_child")
	if not child:
		goto_error()

	year = form.getvalue('se_year')
	if    year == 'elder':  year = "старше 2010"
	elif year == 'little': year = "молодше 2018"
	elif year == '0':      goto_error()

	if   form.getvalue('ra_gender') == 'M': gender = "хлопчик"
	elif form.getvalue('ra_gender') == 'W': gender = "дівчинка"
	else:                                  gender = "стать дитини не вказано"

	if   form.getvalue('ra_swim') == 'rank': swim = "має спортивний розряд"
	elif form.getvalue('ra_swim') == 'good': swim = "впевнено тримається на воді"
	elif form.getvalue('ra_swim') == 'soso': swim = "може проплисти декілька метрів"
	elif form.getvalue('ra_swim') == 'dnot': swim = "не вміє плавати"
	else:                                   swim = "як плаває - не вказали"

	preferred_time = form.getvalue('ra_time')  # best time
	if preferred_time == None:
		preferred_time = 'не вказано'
	else:
		preferred_time = preferred_time + ':00'

	subject = child + ' (' + year + ')'
	data += gender + ': ' + subject + '\n' + swim + '\n'
	data += 'час тренування: ' + preferred_time + '\n'


	if   form.getvalue('se_par1who') == 'mama': par1 = "мама"
	elif form.getvalue('se_par1who') == 'tato': par1 = "тато"
	elif form.getvalue('se_par1who') == 'baba': par1 = "бабуся"
	elif form.getvalue('se_par1who') == 'dida': par1 = "дідусь"
	elif form.getvalue('se_par1who') == 'brat': par1 = "брат"
	elif form.getvalue('se_par1who') == 'sest': par1 = "сестра"
	else:                                       par1 = "родич"
	par1 += ': '

	if form.getvalue('tx_par1name'): par1 += form.getvalue('tx_par1name') + ', '
	if form.getvalue('tx_par1mail'): par1 += form.getvalue('tx_par1mail') + ', '
	if form.getvalue('tx_par1pho'):  par1 += form.getvalue('tx_par1pho')
	if par1:
		data += par1 + '\n'

	if   form.getvalue('se_par2who') == 'mama': par2 = "мама"
	elif form.getvalue('se_par2who') == 'tato': par2 = "тато"
	elif form.getvalue('se_par2who') == 'baba': par2 = "бабуся"
	elif form.getvalue('se_par2who') == 'dida': par2 = "дідусь"
	elif form.getvalue('se_par2who') == 'brat': par2 = "брат"
	elif form.getvalue('se_par2who') == 'sest': par2 = "сестра"
	else:                                       par2 = "родич"
	par2 += ': '

	if form.getvalue('tx_par2name'): par2 += form.getvalue('tx_par2name') + ', '
	if form.getvalue('tx_par2mail'): par2 += form.getvalue('tx_par2mail') + ', '
	if form.getvalue('tx_par2pho'):  par2 += form.getvalue('tx_par2pho')
	if par2:
		data += par2 + '\n'

	if form.getvalue('ta_desc'):
		data += 'додатково: ' + form.getvalue('ta_desc') + '\n'

	# save to file
	fh = open("_saved.txt", "a")
	fh.write(data)
	fh.close


	# send via mail
	reply_name = ''
	reply_mail = ''
	if form.getvalue('tx_par1mail'):
		reply_mail = form.getvalue('tx_par1mail')
		if form.getvalue('tx_par1name'): reply_name = form.getvalue('tx_par1name')
		else:                            reply_name = ""
	elif form.getvalue('tx_par2mail'):
		reply_mail = form.getvalue('tx_par2mail')
		if form.getvalue('tx_par2name'): reply_name = form.getvalue('tx_par2name')
		else:                            reply_name = ""

	send_email(reply_name, reply_mail, subject, data)

	#data = re.sub('\n','<br />',data)
	redirect("/success/")
else:
	goto_error()
