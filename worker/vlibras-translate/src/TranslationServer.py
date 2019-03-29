#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request, abort, send_from_directory
from flask.ext.cors import CORS
from functools import wraps
from PortGlosa import traduzir
from subprocess import check_output, Popen
from threading import Lock
from time import sleep
from logging.handlers import RotatingFileHandler
import Trie, os, argparse, json, _thread, logging, sys

MySQLdb=None
RUN_MODE=None
DICT_VERSION=None
BUNDLES_PATH=None
BUNDLES_LIST={}
TRIE=None
conn=None
lock = Lock()
app=Flask(__name__, static_url_path="", static_folder="/var/www/")
CORS(app)

def check_run_mode(func):
	@wraps(func)
	def decorated_function(*args, **kwargs):
		if (RUN_MODE == "translate" or (RUN_MODE == "dict" and request.path == "/statistics")):
			abort(404)
		return func(*args, **kwargs)
	return decorated_function

def dict_mode():
	global BUNDLES_PATH
	try:
		SIGNS_PATH=os.environ['SIGNS_VLIBRAS']
	except KeyError:
		raise EnvironmentError("Environment variable 'SIGNS_VLIBRAS' not found.")
	IOS_SIGNS_PATH=os.path.join(SIGNS_PATH, "IOS")
	ANDROID_SIGNS_PATH=os.path.join(SIGNS_PATH, "ANDROID")
	STANDALONE_SIGNS_PATH=os.path.join(SIGNS_PATH, "STANDALONE")
	WEBGL_SIGNS_PATH=os.path.join(SIGNS_PATH, "WEBGL")
	BUNDLES_PATH={"IOS":IOS_SIGNS_PATH, "ANDROID":ANDROID_SIGNS_PATH, "STANDALONE":STANDALONE_SIGNS_PATH, "WEBGL":WEBGL_SIGNS_PATH}
	check_version()
	list_bundles()
	generate_trie()

def connect_database():
	import MySQLdb as mysql
	import warnings
	MySQLdb = mysql
	global conn
	warnings.filterwarnings('ignore', category=MySQLdb.Warning)
	while True:
		try:
			conn = MySQLdb.connect(user="root", db="signsdb")
		except:
			print("Trying to connect to the database...\n")
			sleep(5)
			continue
		break
	check_database()

def full_mode():
	dict_mode()
	connect_database()

def logger():
	global app
	logfile = os.path.join(os.environ['HOME'], "translate.log")
	print(' * Running...\n # See the log in: ' + logfile)
	handler = RotatingFileHandler(logfile, maxBytes=10000, backupCount=10)
	handler.setLevel(logging.DEBUG)
	app.logger.addHandler(handler)
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.DEBUG)
	log.addHandler(handler)

def check_version():
	global DICT_VERSION
	DICT_VERSION = check_output(["aptitude", "search", "dicionario-vlibras", "-F", "%V"])
	
def init_mode(args):
	global RUN_MODE
	if args.logfile: logger()
	RUN_MODE = args.mode.lower()
	if RUN_MODE == "dict":
		dict_mode()
		print("# Server started in dictionary mode. Requests will be accepted for translation of texts and download bundles.\n# Endpoints '/translate' and '/<PLATFORM>/<SIGN>' are available.")
	elif RUN_MODE == "full":
		full_mode()
		print("# Server started in full mode. Requests will be accepted for translation of texts, download bundles. All bundles requests will be stored in a database.\n# Endpoints '/translate', '/<PLATFORM>/<SIGN>' and '/statistics' are available.")
	elif RUN_MODE == "translate":
		print("# Server started in translation mode.\n# Only endpoint '/translate' available.")
	
def list_bundles():
	global BUNDLES_LIST
	states = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
	BUNDLES_LIST["DEFAULT"] = check_platform_files()
	for platform, path in BUNDLES_PATH.items():
		BUNDLES_LIST[platform] = {}
		for state in states:
			try:
				BUNDLES_LIST[platform].update({state:set(os.listdir(os.path.join(path, state)))})
			except OSError:
				BUNDLES_LIST[platform].update({state:set([])})

def list_files(path):
	files = []
	for fname in os.listdir(path):
		path_mount = os.path.join(path, fname)
		if not os.path.isdir(path_mount):
			files.append(fname)
	return files

def generate_trie():
	global TRIE
	signs = list(BUNDLES_LIST["DEFAULT"])
	TRIE = json.dumps(Trie.gen(signs))

def check_platform_files():
	android = set(list_files(BUNDLES_PATH["ANDROID"]))
	ios = set(list_files(BUNDLES_PATH["IOS"]))
	webgl = set(list_files(BUNDLES_PATH["WEBGL"]))
	standalone = set(list_files(BUNDLES_PATH["STANDALONE"]))
	if android == ios and ios == webgl and webgl == standalone:
		return standalone
	raise RuntimeError("Inconsistent signs. Check files.")

def check_database():
	cursor = conn.cursor()
	cursor.execute('CREATE DATABASE IF NOT EXISTS signsdb;')
	create_signs_table = """CREATE TABLE IF NOT EXISTS signs (
			 id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
			 sign_name VARCHAR(255) NOT NULL,
			 amount int NOT NULL,
			 has CHAR(3) )"""
	create_translations_table = """CREATE TABLE IF NOT EXISTS translations (
			 id int NOT NULL PRIMARY KEY AUTO_INCREMENT,
			 text LONGTEXT NOT NULL,
			 gloss LONGTEXT NOT NULL,
			 amount int NOT NULL )"""
	create_platforms_table = """CREATE TABLE IF NOT EXISTS platforms (
			 platform_name VARCHAR(255) NOT NULL PRIMARY KEY,
			 amount int NOT NULL )"""
	insert_platforms_default = "INSERT IGNORE INTO platforms (platform_name, amount)  VALUES (%s, %s)"
	cursor.execute(create_signs_table)
	cursor.execute(create_translations_table)
	cursor.execute(create_platforms_table)
	cursor.execute(insert_platforms_default, ("ANDROID", 0))
	cursor.execute(insert_platforms_default, ("IOS", 0))
	cursor.execute(insert_platforms_default, ("WEBGL", 0))
	cursor.execute(insert_platforms_default, ("STANDALONE", 0))
	conn.commit()
	cursor.close()

def insert_sign_db(sign_name, value, has):
	try:
		cursor = conn.cursor()
		query_string = "INSERT INTO signs (sign_name, amount, has) VALUES (%s, %s, %s)"
		cursor.execute(query_string, (sign_name, value, has));
		conn.commit()
	except MySQLdb.OperationalError:
		connect_database()
		print("Reconnecting...")
		insert_sign_db(sign_name, value, has)

def update_sign_db(sign_name, amount, has):
	try:
		cursor = conn.cursor()
		query_string = "UPDATE signs SET amount=%s, has=%s WHERE sign_name=%s"
		cursor.execute(query_string, (amount, has, sign_name));
		conn.commit()
	except MySQLdb.OperationalError:
		connect_database()
		print("Reconnecting...")
		update_sign_db(sign_name, amount, has)

def select_sign_db(sign_name):
	try:
		cursor = conn.cursor()
		query_string = "SELECT amount FROM signs WHERE sign_name=%s"
		cursor.execute(query_string, (sign_name));
		try:
			amount = cursor.fetchone()[0]
		except TypeError:
			return None
		return amount
	except MySQLdb.OperationalError:
		connect_database()
		print("Reconnecting...")
		return select_sign_db(sign_name)

def insert_translation_db(text, gloss):
	try:
		cursor = conn.cursor()
		query_string = "INSERT INTO translations (text, gloss, amount) VALUES (%s, %s, %s)"
		cursor.execute(query_string, (text, gloss, 1));
		conn.commit()
	except MySQLdb.OperationalError:
		connect_database()
		print("Reconnecting...")
		insert_translation_db(text, gloss)

def update_translation_db(text, gloss):
	try:
		cursor = conn.cursor()
		query_string = "UPDATE translations SET amount=amount+1 WHERE text=%s AND gloss=%s"
		cursor.execute(query_string, (text, gloss));
		conn.commit()
	except MySQLdb.OperationalError:
		connect_database()
		print("Reconnecting...")
		update_translation_db(text, gloss)

def select_translation_db(text, gloss):
	try:
		cursor = conn.cursor()
		query_string = "SELECT amount FROM translations WHERE text=%s AND gloss=%s"
		cursor.execute(query_string, (text, gloss));
		try:
			amount = cursor.fetchone()[0]
		except TypeError:
			return None
		return amount
	except MySQLdb.OperationalError:
		connect_database()
		print("Reconnecting...")
		return select_translation_db(text, gloss)

def update_platform_db(platform_name):
	try:
		cursor = conn.cursor()
		query_string = "UPDATE platforms SET amount=amount+1 WHERE platform_name=%s"
		cursor.execute(query_string, (platform_name));
		conn.commit()
	except MySQLdb.OperationalError:
		connect_database()
		print("Reconnecting...")
		update_platform_db(platform_name)

def update_database_statistic(sign_name, platform_name, file_exists):
	if RUN_MODE == "full":
		with lock:
			has = "YES" if file_exists else "NO" 
			value_sign_name = select_sign_db(sign_name)
			if value_sign_name is None:
				insert_sign_db(sign_name, 1, has)
			else:
				update_sign_db(sign_name, value_sign_name+1, has)
			update_platform_db(platform_name)

def update_database_translation(text, gloss):
	if RUN_MODE == "full":
		with lock:
			gloss_selected = select_translation_db(text, gloss)
			if gloss_selected is None:
				insert_translation_db(text, gloss)
			else:
				update_translation_db(text, gloss)

@app.route("/translate", methods=['GET'])
def translate():
	print(request.args.get('text'))
	text = request.args.get('text').encode("UTF-8")
	gloss = traduzir(text)
	_thread.start_new_thread(update_database_translation, (text, gloss))
	return gloss

@app.route("/statistics")
@check_run_mode
def load_statistics_page():
	page_path = os.path.join(app.static_folder, "statistics")
	php_output = check_output(["php", page_path])
	return php_output

@app.route("/update", methods=['GET'])
def update():
	list_bundles()
	generate_trie()
	return "Successfully updated list.", 200

@app.route("/version", methods=['GET'])
def get_version():
	return DICT_VERSION, 200

@app.route("/signs", methods=['GET'])
def get_signs_list():
	return TRIE, 200

@app.route("/<platform>/<sign>", methods=['GET'])
@check_run_mode
def get_sign(platform, sign):
	platform = platform.encode("UTF-8")
	sign = sign.encode("UTF-8")
	if " " in sign or platform not in BUNDLES_PATH: abort(400)
	file_exists = sign in BUNDLES_LIST["DEFAULT"]
	_thread.start_new_thread(update_database_statistic, (sign, platform, file_exists))
	if file_exists:
		return send_from_directory(BUNDLES_PATH[platform], sign)
	abort(404)

@app.route("/<platform>/<state>/<sign>", methods=['GET'])
@check_run_mode
def get_sign_state(platform, state, sign):
	platform = platform.encode("UTF-8")
	sign = sign.encode("UTF-8")
	state = state.encode("UTF-8")
	if " " in sign or platform not in BUNDLES_PATH: abort(400)
	file_exists = sign in BUNDLES_LIST[platform][state]
	if file_exists:
		_thread.start_new_thread(update_database_statistic, (sign, platform, file_exists))
		return send_from_directory(os.path.join(BUNDLES_PATH[platform], state), sign)
	return get_sign(platform.decode("UTF-8"), sign.decode("UTF-8"))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Translation server and signs download for VLibras.')
	parser.add_argument('--port', help='Port where the server will be available.', default=3000)
	parser.add_argument("--mode", help="So that the server will work.", choices=['translate','dict','full'], default="translate")
	parser.add_argument("--logfile", action="store_true", help="So that the server will work.")
	args = parser.parse_args()
	init_mode(args)
	app.run(host="0.0.0.0", port=int(args.port), threaded=True, debug=False)
