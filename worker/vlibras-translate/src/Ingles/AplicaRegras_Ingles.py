#!/usr/bin/python
# -*- coding: utf-8 -*-

#AplicaRegras para Inglês

from TemplateAplicaRegras import TemplateAplicaRegras

class AplicaRegras(TemplateAplicaRegras):
	def __init__(self):

		# Dicionário de funcões do campo specific do arquivo de regras
		self.especificos = {"a":self.verifica_artigo,"aux_verb":self.verifica_verbo_auxiliar,"is_what":self.verifica_what}
		# Dicionário das açoes tratadas
		self.acoes = {"change_vb":self.get_vb_infinitivo,"change_pro$":self.get_pro_pessoal,"change_adv":self.get_adv_to_adj}
		#Lista das pontuações
		self.pontuacoes = ["[interrogation]","[dot]","[exclamation]"]

		#Faz a instância dos dicionarios auxíliares
		self.dicionarios = self.lerDicionarios()
		#Faz a leitura dos dicionários
		self.dicionarios.carregar_dicionarios()

		TemplateAplicaRegras.__init__(self,"Ingles/regras_Ingles.xml",self.especificos, self.acoes, self.pontuacoes)

	def lerDicionarios(self):
		"""Lê os dicionários auxíliares"""
		from LerDicionarios_Ingles import LerDicionarios

		return LerDicionarios()

	def get_vb_infinitivo(self,token):
		"""Retorna o verbo infinitivo equivalente ao verbo passado como parâmetro"""
		if(self.dicionarios.has_verbo_auxiliar(token)):
			return token
		return self.dicionarios.get_verbo_infinitivo(token)

	def get_pro_pessoal(self,token):
		"""Acessa o dicionário e pega o pronome pessoal correspondente ao pronome possessivo passado como parâmetro (token)"""
		return self.dicionarios.get_pronome_possessivo(token)

	def get_adv_to_adj(self,token):
		"""Utiliza a base de dados WordNet para trocar o advérbio por seu adjetivo correspondente"""
		from nltk.corpus import wordnet
		ret = token
		exc = [line.replace("\n","") for line in open("../data/Ingles/excecao.txt","r").readlines()]
		if token.lower().encode('utf-8') not in exc:
			try:
				ret = wordnet.synset(token.lower().encode('utf-8')+".r.1").lemmas()[0].pertainyms()[0].name().encode('utf-8').decode('utf-8')
				#print token+" "+ret
			except:
				#ret = token
				pass
		return ret

	def verifica_artigo(self, token):
		"""Acessa o dicionário de artigos e verifica se o token está nele"""
		return self.dicionarios.has_artigo(token)

	def verifica_verbo_auxiliar(self, token):
		"""Acessa o dicionário de verbos axiliares e vê se o token está no dicionário"""
		return self.dicionarios.has_verbo_auxiliar(token)

	def verifica_what(self,token):
		"""Verificar se a plavra é 'what'"""
		return token.lower().encode('utf-8') == "what"

	def verificar_excecao_plural(self,token):
		"""Acessa o dicionário de palavras que não possuem plural"""
		#TODO
		return False

	def verificar_plural_irregular(self,token):
		"""Acessa o dicionário de plurais irregulares da lingua inglesa"""
		return self.dicionarios.has_plural_irregular(token)

	def simplificar_sentenca(self,lista):
		"""Faz um pós-processamento do texto, tratando palavras que passaram pelas regras"""
		lista_simplificada = list(lista)

		for tupla in lista_simplificada:
			tag = tupla[1]
			word = tupla[0]

			if "VB" in tag and self.verifica_verbo_auxiliar(word.encode('utf-8')):
				lista_simplificada.remove(tupla)

			if tag != "NPR-P" and (tag[-2:] == "-P" or tag[-2:] == "_P") and not (self.verificar_excecao_plural(word)):
				singular = self.analisar_plural(word)
				tupla[0] = singular

		return lista_simplificada

	def analisar_plural(self,token):
		"""A análise de plural é feita usando o modulo SonowballStemmer do NLTK"""
		if self.verificar_plural_irregular(token):
			return self.dicionarios.get_plural_irregular(token)

		from nltk.stem import SnowballStemmer

		st = SnowballStemmer("english")

		return st.stem(token)


	"""def aplicar_regras_morfo(self,analise_morfologica):
					return analise_morfologica

				def aplicar_regras_sint(self,analise_morfologica, analise_sintatica):
					return analise_morfologica

				def simplificar_sentenca(self,regras_aplicadas):
					return regras_aplicadas"""
