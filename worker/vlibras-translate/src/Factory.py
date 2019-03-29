#! /user/bin/evn python2.6
# -*- coding: utf-8 -*-

class Factory(object):

	def __init__(self, lang="pt"):
		self.classificador = None
		self.aplicaRegras = None
		self.aplicaSinonimos = None
		self.lang = lang
		self.define_class()

	def define_class(self):

		dic_lang = {"pt_br":["ClassificaSentencas","AplicaRegras","AplicaSinonimos"],
					"en":["ClassificaSentencas_Ingles","AplicaRegras_Ingles","AplicaSinonimos_Ingles"],
					"es":["ClassificaSentencas_Espanhol","AplicaRegras_Espanhol","AplicaSinonimos_Espanhol"]}


		self.classificador = __import__(dic_lang[self.lang][0]).ClassificaSentencas()
		self.aplicaRegras = __import__(dic_lang[self.lang][1]).AplicaRegras()
		self.aplicaSinonimos = __import__(dic_lang[self.lang][2]).AplicaSinonimos()


	def get_Classificador(self):
		return self.classificador

	def get_AplicaRegras(self):
		return self.aplicaRegras

	def get_AplicaSinonimos(self):
		return self.aplicaSinonimos