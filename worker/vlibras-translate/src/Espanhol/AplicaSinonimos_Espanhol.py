#!/usr/bin/python
# -*- coding: utf-8 -*-

class AplicaSinonimos():
	def aplicar_sinonimos(self,sentenca_corrigida):
		sent = []

		for tupla in sentenca_corrigida:
			sent.append(tupla[0].upper())

		return " ".join(sent)
