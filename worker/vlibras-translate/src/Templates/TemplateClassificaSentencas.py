#!/usr/bin/python
# -*- coding: utf-8 -*-

import re,nltk, time, random
from os.path import expanduser
from os import environ, path
from unicodedata import normalize
from LerDicionarios import *

class TemplateClassificaSentencas():
	def __init__(self):
		self.sentenca_anotada = ""
		self.puntuacao = {}

	def iniciar_classificacao(self,sentenca):
		tok = self.toqueniza(sentenca)
		tree = self.analisa_sentenca(tok)
		#print tree
		return tree

	def toqueniza(self,sentenca):
		'''Método para fazer a toquenização do sentenca'''
		raise NotImplementedError

	def anota(self,tokens):
		'''Método para fazer a etiquetação do sentenca'''
		raise NotImplementedError

	def lerDicionarios(self):
		'''Método para retornar o objeto da classe de dicionarios auxiliares'''
		raise NotImplementedError

	def obter_classificacao_morfologica(self):
		'''Método para obter a classificação mofológica da sentenca'''
		return self.sentenca_anotada

	def etiqueta_sentenca(self, s):
		"""Etiqueta uma lista de tokens.
		"""
		anotada = self.anota(s)

		#print anotada

		dic = self.lerDicionarios()
		self.pontuacao = self.get_pontuacao()

		if not dic:
			print("Instacie o dicionario")
			raise AttributeError

		regex = re.compile('[%s]' % re.escape('\u2022''!"#&\'()*+,./:;<=>?@[\\]^_`{|}~'))
		tag_punctuation = [".",",","QT","("]
		anotada_corrigida = []

		for x in anotada:
			if x[1] not in tag_punctuation:

				if x[1] == "NUM":
					try:
						float(x[0].replace(',', '.'))
						anotada_corrigida.append(x)
						continue
					except:
						pass

				#Correspondência de tags
				tag = x[1]
				try:
					if dic.has_tags(tag):
						tag_result = dic.get_tags(tag)
						tag_result = tag_result.encode("utf-8")
						if tag_result != "-":
							tag = tag_result
				except AttributeError as e:
					pass
				#################

				tupla = [regex.sub('',x[0]).lower(),tag]
				if tupla[0] != "": anotada_corrigida.append(tupla)
			else:
				if x[0] in self.pontuacao:
					anotada_corrigida.append([self.pontuacao[x[0]].decode("utf-8"),"SPT"])
				# if x[0] == ".":
				# 	anotada_corrigida.append(["[ponto]".decode("utf-8"),"SPT"])
				# elif x[0] == "?":
				# 	anotada_corrigida.append(["[interrogação]".decode("utf-8"),"SPT"])
				# elif x[0] == "!":
				# 	anotada_corrigida.append(["[exclamação]".decode("utf-8"),"SPT"])
		return anotada_corrigida

	def gera_entradas_lexicais(self, lista):
		"""Gera entradas lexicais no formato CFG do NLTK a partir de lista de pares constituídos de tokens e suas etiquetas.
		"""
		entradas=[]
		for e in lista:
			# é necessário substituir símbolos como "-" e "+" do CHPTB
			# que não são aceitos pelo NLTK como símbolos não terminais
			c=re.sub(r"[-+]","_",e[1])
			c=re.sub(r"\$","_S",c)
			entradas.append("%s -> '%s'" % (c, self.remove_acento(e[0])))
		return entradas

	def corrige_anotacao(self, lista):
		"""Esta função deverá corrigir alguns dos erros de anotação mais comuns do Aelius. No momento, apenas é corrigida VB-AN depois de TR.
		"""
		i=1
		while i < len(lista):
			if lista[i][1] == "VB-AN" and lista[i-1][1].startswith("TR"):
				lista[i]=(lista[i][0],"VB-PP")
			i+=1

	def encontra_arquivo(self):
		"""Encontra arquivo na pasta vlibras-translate.
		"""
		if "TRANSLATE_DATA" in environ:
			return path.join(environ.get("TRANSLATE_DATA"), "cfg.syn.nltk")
		return expanduser("~") + "/vlibras-translate/data/cfg.syn.nltk"

	def extrai_sintaxe(self):
		"""Extrai gramática armazenada em arquivo cujo caminho é definido relativamente ao diretório nltk_data.
		"""
		arquivo = self.encontra_arquivo()
		if arquivo:
			f=open(arquivo,"rU")
			sintaxe=f.read()
			f.close()
			return sintaxe
		else:
			print("Arquivo %s não encontrado em nenhum dos diretórios de dados do NLTK:\n%s" % (caminho,"\n".join(nltk.data.path)))

	def analisa_sentenca(self, sentenca):
		"""Retorna lista de árvores de estrutura sintagmática para a sentença dada sob a forma de uma lista de tokens, com base na gramática CFG cujo caminho é especificado como segundo argumento da função. Esse caminho é relativo à pasta nltk_data da instalação local do NLTK. A partir da etiquetagem morfossintática da sentença são geradas entradas lexicais que passam a integrar a gramática CFG. O caminho da gramática e o parser gerado são armazenados como tupla na variável ANALISADORES.
		"""
		parser = self.constroi_analisador(sentenca)
		codificada=[]
		for t in self.sentenca_anotada:
			if t[1] != "SPT":
				codificada.append(self.remove_acento(t[0]).encode("utf-8"))

		trees=parser.parse_one(codificada)
		return trees

	def constroi_analisador(self, s):
		"""Constrói analisador a partir de uma única sentença não anotada, dada como lista de tokens, e uma lista de regras sintáticas no formato CFG, armazenadas em arquivo. Esta função tem um bug, causado pela maneira como o Aelius etiqueta sentenças usando o módulo ProcessaNomesProprios: quando a sentença se inicia por paravra com inicial minúscula, essa palavra não é incorporada ao léxico, mas a versão com inicial maiúscula.
		"""
		self.sentenca_anotada = self.etiqueta_sentenca(s)
		self.corrige_anotacao(self.sentenca_anotada)
		entradas = self.gera_entradas_lexicais(self.sentenca_anotada)
		lexico="\n".join(entradas)
		gramatica="%s\n%s" % (self.extrai_sintaxe().strip(),lexico)
		cfg=nltk.CFG.fromstring(gramatica)
		return nltk.ChartParser(cfg)

	def remove_acento(self, texto):
		try:
			return normalize('NFKD', texto.encode('utf-8').decode('utf-8')).encode('ASCII', 'ignore')
		except:
			return normalize('NFKD', texto.encode('iso-8859-1').decode('iso-8859-1')).encode('ASCII','ignore')

	def exibe_arvores(self, arvores):
		"""Função 'wrapper' para a função de exibição de árvores do NLTK"""
		nltk.draw.draw_trees(*arvores)
