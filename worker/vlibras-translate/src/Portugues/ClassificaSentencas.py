#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

#---------------------------------

# Editado:

#Autor: Erickson Silva
#Email: <erickson.silva@lavid.ufpb.br> <ericksonsilva@live.com>

#LAViD - Laboratório de Aplicações de Vídeo Digital

#---------------------------------


# Donatus Brazilian Portuguese Parser
#
# Copyright (C) 2010-2013 Leonel F. de Alencar
#
# Author: Leonel F. de Alencar <leonel.de.alencar@ufc.br>
# Homepage: <http://www.leonel.profusehost.net/>
#
# Project's URL: <http://sourceforge.net/projects/donatus/>
# For license information, see LICENSE.TXT
#
# $Id: alexp.py $

"""Este módulo contém funções que permitem utilizar o Aelius para etiquetar uma sentença, construindo entradas lexicais com base nas etiquetas atribuídas às palavras da sentença. Essas entradas lexicais são integradas em uma gramática CFG dada, que é transformada em um parser, utilizado para gerar uma árvore de estrutura sintagmática da sentença.
"""
import re,nltk, time, random
from os.path import expanduser
from os import environ, path
from Aelius.Extras import carrega
from Aelius import AnotaCorpus, Toqueniza
from unicodedata import normalize
from unidecode import unidecode
from TemplateClassificaSentencas import TemplateClassificaSentencas

class ClassificaSentencas(TemplateClassificaSentencas):

	def __init__(self):
		self.sentenca_anotada = ""
		self.sleep_times = [0.1,0.2]

	def toqueniza(self, s):
		"""Decodifica string utilizando utf-8, retornando uma lista de tokens em unicode.
		"""
		try:
			table = str.maketrans(dict.fromkeys("“”«»–’‘º"))
			decodificada = s.translate(table)
		except UnicodeDecodeError:
			decodificada = s.replace("“","").replace("”","").replace("«","").replace("»","").replace("’","").replace("‘","").replace("º","")
		except Exception as e:
			decodificada = s
		return Toqueniza.TOK_PORT_LX.tokenize(decodificada)

	def obter_classificacao_morfologica(self):
		return self.sentenca_anotada

	def etiqueta_sentenca(self, s):
		"""Aplica um dos etiquetadores do Aelius na etiquetagem da sentença dada como lista de tokens.
		"""
		etiquetador = carrega("AeliusHunPos")
		# print('ClassificaSentencas etiqueta_sentenca l62:\n', s)
		anotada = AnotaCorpus.anota_sentencas([s],etiquetador,"hunpos")[0]
		# print('ClassificaSentencas etiqueta_sentenca l66:\n', anotada)
		
		while (anotada[0][1] is None):
			time.sleep(random.choice(self.sleep_times))
			anotada = AnotaCorpus.anota_sentencas([s],etiquetador,"hunpos")[0]
		# print('ClassificaSentencas etiqueta_sentenca l71:\n', anotada)
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

				tupla = [regex.sub('',x[0]).lower(),x[1]]
				if tupla[0] != "": anotada_corrigida.append(tupla)
			else:
				if x[0] == ".":
					anotada_corrigida.append(["[ponto]","SPT"])
				elif x[0] == "?":
					anotada_corrigida.append(["[interrogação]","SPT"])
				elif x[0] == "!":
					anotada_corrigida.append(["[exclamação]","SPT"])

		# print('ClassificaSentencas etiqueta_sentenca l97:\n', anotada_corrigida)
		return anotada_corrigida

	def gera_entradas_lexicais(self, lista):
		"""Gera entradas lexicais no formato CFG do NLTK a partir de lista de pares constituídos de tokens e suas etiquetas.
		"""
		# print('ClassificaSentencas gera_entradas_lexicais l100\n:', lista)
		entradas=[]
		for e in lista:
			# é necessário substituir símbolos como "-" e "+" do CHPTB
			# que não são aceitos pelo NLTK como símbolos não terminais
			c=re.sub(r"[-+]","_",e[1])
			c=re.sub(r"\$","_S",c)
			entradas.append("%s -> '%s'" % (c, self.remove_acento(e[0])))
		# print('ClassificaSentencas gera_entradas_lexicais l109\n:', entradas)
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
		# print('ClassificaSentencas analisa_sentenca l142:\n', sentenca)
		parser = self.constroi_analisador(sentenca)
		codificada=[]
		# print('ClassificaSentencas analisa_sentenca l145:\n', self.sentenca_anotada)
		for t in self.sentenca_anotada:
			if t[1] != "SPT":
				codificada.append(self.remove_acento(t[0]))
		trees=parser.parse_one(codificada)

		return trees

	def constroi_analisador(self, s):
		"""Constrói analisador a partir de uma única sentença não anotada, dada como lista de tokens, e uma lista de regras sintáticas no formato CFG, armazenadas em arquivo. Esta função tem um bug, causado pela maneira como o Aelius etiqueta sentenças usando o módulo ProcessaNomesProprios: quando a sentença se inicia por paravra com inicial minúscula, essa palavra não é incorporada ao léxico, mas a versão com inicial maiúscula.
		"""
		self.sentenca_anotada = self.etiqueta_sentenca(s)
		# print('ClassificaSentenças l155:\n', self.sentenca_anotada)
		self.corrige_anotacao(self.sentenca_anotada)
		# print('ClassificaSentenças l155:\n', self.sentenca_anotada)
		entradas = self.gera_entradas_lexicais(self.sentenca_anotada)
		lexico="\n".join(entradas)
		gramatica="%s\n%s" % (self.extrai_sintaxe().strip(),lexico)
		cfg=nltk.CFG.fromstring(gramatica)
		return nltk.ChartParser(cfg)

	def remove_acento(self, texto):
		try:
			return unidecode.unidecode(texto)
		except:
			return normalize('NFKD', texto.encode('iso-8859-1').decode('iso-8859-1')).encode('ASCII','ignore').decode()

	def exibe_arvores(self, arvores):
		"""Função 'wrapper' para a função de exibição de árvores do NLTK"""
		nltk.draw.draw_trees(*arvores)

	def iniciar_classificacao(self, sentenca):
		tokens = self.toqueniza(sentenca)
		tree = self.analisa_sentenca(tokens)
		return tree
