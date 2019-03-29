#!/usr/bin/python
# -*- coding: utf-8 -*-

#LerDicionarios para Inglês

from TemplateLerDicionarios import TemplateLerDicionarios
import csv
from nltk.stem import WordNetLemmatizer

class LerDicionarios(TemplateLerDicionarios):
	"""Ler dos dicionários necessários pra o Inglês"""
	def __init__(self):
		TemplateLerDicionarios.__init__(self)
		self.set_art = []
		self.lemmatizer = None
		self.verb_aux = []
		self.pron_poss = {}
		self.plural_irr= {}
		self.tagsFileName = "Ingles/enToaelius.csv"

	def carregar_dicionarios(self):
		'''Realiza a leitura dos arquivos e atribui à estruturas de dicionários e sets.
		'''
		self.carregar_artigos()
		self.carregar_verbo_infinitivo()
		self.carregar_verbos_auxiliares()
		self.carregar_pronomes_possessivos()
		self.carregar_plurais_irregulares()

   	def carregar_artigos(self):
		'''Carrega arquivo de artigos a serem removidos.
		'''
		try:
			self.file = csv.reader(open(self.montar_diretorio("Ingles/artigos_Ingles.csv")))
		except IOError as xxx_todo_changeme:
			(errno, strerror) = xxx_todo_changeme.args
			print("I/O error(%s): %s" % (errno, strerror))
			print("carregar_artigos")

		rows = []
		for row in self.file:
			rows.append(row[0].decode("utf-8"))
		self.set_art = set(rows)

	def carregar_verbo_infinitivo(self):
		'''Prepara o objeto para o lematizador, usando a base WordNet'''
		from nltk.stem import WordNetLemmatizer

		self.lemmatizer = WordNetLemmatizer()

	def carregar_verbos_auxiliares(self):
		'''Carrega arquivo de verbos auxíliares a serem removidos.
		'''
		try:
			self.file = csv.reader(open(self.montar_diretorio("Ingles/verbos_auxiliares.csv")))
		except IOError as xxx_todo_changeme1:
			(errno, strerror) = xxx_todo_changeme1.args
			print("I/O error(%s): %s" % (errno, strerror))
			print("carregar_artigos")

		rows = []
		for row in self.file:
			rows.append(row[0].decode("utf-8"))
		self.verb_aux = set(rows)

	def carregar_pronomes_possessivos(self):
		'''Carrega arquivo pronomes possessivos com os pronomes pessoais correspondentes
		'''
		try:
			self.file = csv.reader(open(self.montar_diretorio("Ingles/pronomes_possessivos.csv")), delimiter=",")
		except IOError as xxx_todo_changeme2:
			(errno, strerror) = xxx_todo_changeme2.args
			print("I/O error(%s): %s" % (errno, strerror))
			print("pronomes_possessivos")

		for row in self.file:
			if row[1] != "-":
				try:
					self.pron_poss[row[0].decode("utf-8")] = row[1].decode("utf-8")
				except UnicodeDecodeError:
					self.pron_poss[row[0].decode('iso8859-1').encode('utf-8').decode('utf-8')] = row[1].decode('iso8859-1').encode('utf-8').decode('utf-8')

	def carregar_plurais_irregulares(self):
		'''Carrega arquivo de plurais irregulares
		'''
		try:
			self.file = csv.reader(open(self.montar_diretorio("Ingles/plurais_irregulares.csv")), delimiter=",")
		except IOError as xxx_todo_changeme3:
			(errno, strerror) = xxx_todo_changeme3.args
			print("I/O error(%s): %s" % (errno, strerror))
			print("pronomes_irregulares")

		for row in self.file:
			try:
				self.plural_irr[row[0].decode("utf-8")] = row[1].decode("utf-8")
			except UnicodeDecodeError:
				self.plural_irr[row[0].decode('iso8859-1').encode('utf-8').decode('utf-8')] = row[1].decode('iso8859-1').encode('utf-8').decode('utf-8')


	def has_artigo(self, token):
		'''Verifica se o token recebido consta no arquivo de artigos a serem removidos.
		'''
		if not self.set_art:
			self.carregar_artigos()
		return token in self.set_art

	def has_verbo_auxiliar(self, token):
		'''Verifica se o token recebido consta no arquivo verbos auxiliares a serem removidos.
		'''
		if not self.verb_aux:
			self.carregar_verbos_auxiliares()
		return token in self.verb_aux

	def has_pronome_possessivo(self,token):
		'''Verifica se o token recebido consta no arquivo pronomes possessivos.
		'''
		if not self.pron_poss:
			self.carregar_pronomes_possessivos()
		return token in self.pron_poss

	def has_plural_irregular(self,token):
		'''Verifica se o token recebido consta no arquivo plurais irregulares.
		'''
		if not self.plural_irr:
			self.carregar_plurais_irregulares()
		return token in self.plural_irr

	def get_pronome_possessivo(self,token):
		'''Pega o pronome pessoal correspondente ao pronome poessessivo passado como parâmetro.
		'''
		if not self.pron_poss:
			self.carregar_pronomes_possessivos()
		if self.has_pronome_possessivo(token):
			return self.pron_poss[token]

		return token

	def get_verbo_infinitivo(self, token):
		'''Pega o infinitivo dos verbos utilizando o lematizador'''
		return self.lemmatizer.lemmatize(token,'v')

	def get_plural_irregular(self,token):
		'''Pega o singular da palavra passada como parâmetro.
		'''
		if not self.plural_irr:
			self.carregar_plurais_irregulares()
		if self.has_plural_irregular(token):
			return self.plural_irr[token]

		return token
