#! /user/bin/evn python2.6
# -*- coding: utf-8 -*-
from TemplateClassificaSentencas import TemplateClassificaSentencas

class ClassificaSentencas(TemplateClassificaSentencas):

	def __init__(self):
		TemplateClassificaSentencas.__init__(self)
		self.sentenca_anotada = ""
		#self.lang = "es"

	def toqueniza(self,texto):
		#Toquenização usando uma classe padrão do NLTK
		from nltk.tokenize import word_tokenize as tok

		try:
			table = str.maketrans(dict.fromkeys("“”«»–’‘º"))
			decodificada = s.translate(table)
		except UnicodeDecodeError:
			decodificada = texto.replace("“","").replace("”","").replace("«","").replace("»","").replace("’","").replace("‘","").replace("º","")
		except:
			decodificada = texto

		return tok(decodificada)

	def anota(self,toquenizada):
		#Anota a sentença toquenizada usando um arquivo treinado com a base CONLL-2007
		from pickle import load

		txt_in = open('../data/Espanhol/esp_pos.pkl','rb')
		tagger = load(txt_in)
		txt_in.close()

		tg = tagger.tag(toquenizada)

		for i in range(len(tg)):
			if tg[i][1]:
				tg[i] = (tg[i][0],tg[i][1].upper())

		return tg

	def lerDicionarios(self):
		from LerDicionarios_Espanhol import LerDicionarios

		return LerDicionarios()

	def get_pontuacao(self):
		return {".":"ponto","?":"interrogação","!":"exclamação"}

	"""def anotar(self,texto):
					return etiquetar(toquenizar(texto))

				def iniciar_classificacao(self,sentenca):
					tok = self.toquenizada = self.toquenizar(sentenca)

					anot = self.anotada = self.etiquetar(tok)
					return None

				def obter_classificacao_morfologica(self):
					return self.anotada"""
