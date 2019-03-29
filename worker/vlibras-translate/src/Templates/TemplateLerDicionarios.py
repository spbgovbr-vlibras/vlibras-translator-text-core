#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import csv

class TemplateLerDicionarios():
	def __init__(self):
		self.path = self.get_path()
		self.file = ""
		self.dic_tags = {}
		#self.list_langs = {"pt":0,"en":1,"es":2}

	def get_path(self):
		'''Verifica qual o SO e gera o path de onde se encontra o diretório data.
		'''
		if "TRANSLATE_DATA" in os.environ:
			return os.environ.get("TRANSLATE_DATA")
		return os.path.expanduser("~") + "/vlibras-translate/data" 

   	def montar_diretorio(self, arquivo):
   		return os.path.join(self.path, arquivo)

	def carregar_tags(self):
		'''Carrega arquivo corresondência de tags
		'''
		try:
			self.file = csv.reader(open(self.montar_diretorio(self.tagsFileName)), delimiter=",")
		except IOError as xxx_todo_changeme: 
			(errno, strerror) = xxx_todo_changeme.args 
			print("I/O error(%s): %s" % (errno, strerror))
			print("carregar_tags")

		for row in self.file:
			if row[1] != "-": 
				try:
					self.dic_tags[row[1].decode("utf-8")] = row[0].decode("utf-8") 
				except UnicodeDecodeError:
					self.dic_tags[row[1].decode('iso8859-1').encode('utf-8').decode('utf-8')] = row[0].decode('iso8859-1').encode('utf-8').decode('utf-8')


	def has_tags(self, token):
		'''Verifica se a tag recebida consta no arquivo de Tags
		'''

		if not self.dic_tags:
			self.carregar_tags()
		return token in self.dic_tags

	def get_tags(self, token):
		'''Obtém a tag correspondente no Aelius, se houver
		'''
		if not self.dic_tags:
			self.carregar_tags()
		return self.dic_tags[token]