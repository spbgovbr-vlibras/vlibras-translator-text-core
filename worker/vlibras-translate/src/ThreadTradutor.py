#!/usr/bin/python
# -*- coding: utf-8 -*-

#Autor: Erickson Silva 
#Email: <erickson.silva@lavid.ufpb.br> <ericksonsilva@live.com>

#LAViD - Laboratório de Aplicações de Vídeo Digital

from TraduzSentencas import * 
from threading import Thread

class ThreadTradutor(Thread):
	'''Thread que inicia uma tradução'''

	def __init__(self, sentenca, taxa, lang="pt_br"):
		''' Recebe o texto a ser traduzido e o atribui a uma variável.
		Além disso, instancia variável que será armazenada a glosa e a classe responsável pelo processo de tradução.
		'''
		Thread.__init__(self)
		self.sentenca = sentenca
		self.glosa = ""
		self.tradutor = TraduzSentencas(lang)
		self.taxa_qualidade = taxa
		
	def run(self):
		''' Metódo executado ao 'startar' a Thread. É responsável por iniciar a tradução passando o texto como parâmetro.
		'''
		self.glosa = self.tradutor.iniciar_traducao(self.sentenca, self.taxa_qualidade)

	def obter_glosa(self):
		''' Obtém a glosa após o processo de tradução.
		'''
		return self.glosa