#! /user/bin/evn python2.6
# -*- coding: utf-8 -*-

from TemplateClassificaSentencas import TemplateClassificaSentencas

class ClassificaSentencas(TemplateClassificaSentencas):

	def __init__(self):
		TemplateClassificaSentencas.__init__(self)
		#self.lang = "en"
		#self.sentenca_anotada = ""

	def toqueniza(self,texto):
		'''Toqueniza usando uma classe padrão do NLTK'''
		from nltk.tokenize import word_tokenize as tok

		try:
			table = str.maketrans(dict.fromkeys("“”«»–’‘º"))
			decodificada = s.translate(table)
		except UnicodeDecodeError:
			decodificada = texto.replace("“","").replace("”","").replace("«","").replace("»","").replace("’","").replace("‘","").replace("º","")
		except:
			decodificada = texto

		return tok(decodificada)

	def anota(self,tokenizada):
		'''Anota a sentença toquenizada usando uma classe padrão do NLTK'''
		from nltk.tag import pos_tag

		return pos_tag(tokenizada)

	def lerDicionarios(self):
		'''Lê objeto para a leitura dos dicionarios auxíliares'''
		from LerDicionarios_Ingles import LerDicionarios

		return LerDicionarios()

	def get_pontuacao(self):
		return {".":"[DOT]","?":"[INTERROGATION]","!":"[EXCLAMATION]"}

	#def anotar(texto):
		#return etiquetar(toquenizar(texto))

	#def iniciar_classificacao(self,sentenca):
		#tok = self.toquenizada = self.toquenizar(sentenca)
		#anot = self.anotada = self.etiquetar(tok)
		#return none

	#def obter_classificacao_morfologica(self):
		#return self.anotada
