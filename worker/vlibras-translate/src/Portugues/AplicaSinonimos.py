#!/usr/bin/python
# -*- coding: utf-8 -*-

#Autor: Erickson Silva 
#Email: <erickson.silva@lavid.ufpb.br> <ericksonsilva@live.com>

#LAViD - Laboratório de Aplicações de Vídeo Digital

import os
import re
import csv
import sys
from nltk.tree import Tree
from LerDicionarios import *
from os.path import expanduser
from os import environ, path


class AplicaSinonimos(object):
	'''Aplica sinonimos após aplicação de regras morfológicas/sintática
	'''

	def __init__(self):
		self.dicionarios = LerDicionarios()
		self.ordinais = {'8ª': 'oitava', '3º': 'terceiro', '9ª': 'nona', '5º': 'quinto', '6ª': 'sexta',
							'1º': 'primeiro', '7ª': 'sétima', '2º': 'segundo', '8º': 'oitavo', '3ª': 'terceira',
								'9º': 'nono', '5ª': 'quinta', '6º': 'sexto', '1ª': 'primeira', '7º': 'sétimo', '2ª': 'segunda'}

	# Itera sobre os tokens obtendo os sinonimos
	def aplicar_sinonimos(self, lista_anotada):
		'''Percorre a lista fazendo a substituição pelos sinonimos.
		'''
		lista_corrigida = []
		# print('AplicaSinonimos aplicar_sinonimos l34:\n', lista_anotada)
		for tupla in lista_anotada:
			sinonimo = tupla[0].upper()
			#sinonimo = self.verificar_sinonimo(tupla[0].upper())
			if tupla[1] == "NUM" or tupla[1] == "NUM-R":
				if self.verificar_ordinal(sinonimo):
					ordinal = self.get_ordinal_extenso(sinonimo)
					lista_corrigida.append(ordinal)
					continue
				else:
					cardinal = self.converter_ordinal_para_cardinal(sinonimo)
					lista_corrigida.append(cardinal)
					# print('AplicaSinonimos aplicar_sinonimos l46:\n', cardinal)
					continue
			lista_corrigida.append(sinonimo)
		# print(lista_corrigida)
		return self.verificar_palavra_composta(lista_corrigida)

	# Verifica se há sinonimo do token  
	def verificar_sinonimo(self, token):
		'''Verifica se há sinonimo do token.
		'''
		if self.dicionarios.has_sinonimo(token):
			return self.dicionarios.get_sinonimo(token)
		return token

	def verificar_palavra_composta(self, lista):
		palavras_compostas = self.carregar_palavras_compostas()
		try:
			sentenca_corrigida = "_".join(lista).upper()
		except:
			sentenca_corrigida = "_".join([str(x[0]) for x in lista]).upper()
		for p in palavras_compostas:
			for m in re.finditer(p, sentenca_corrigida):
				first = "_" if m.start() == 0 else sentenca_corrigida[m.start()-1]
				last = "_" if m.end() == len(sentenca_corrigida) else sentenca_corrigida[m.end()-1]
				if first == "_" and last == "_":
					sentenca_corrigida = sentenca_corrigida.replace(p, p.replace("_", "#*#"))
		return sentenca_corrigida.replace("_", " ").replace("#*#", "_")

	def carregar_palavras_compostas(self):
		path = self.localizar_arquivo_palavras_compostas()
		return set(open(path).read().split())

	def localizar_arquivo_palavras_compostas(self):
		if "TRANSLATE_DATA" in environ:
			return path.join(environ.get("TRANSLATE_DATA"), "palavras_compostas.csv")
		return expanduser("~")+'/vlibras-translate/data/palavras_compostas.csv'

	def get_ordinal_extenso(self, token):
			return self.ordinais[token]

	def verificar_ordinal(self, token):
		return token in self.ordinais

	def converter_ordinal_para_cardinal(self, token):
		return token.replace("ª", "").replace("º", "")