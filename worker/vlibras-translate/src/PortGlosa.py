#!/usr/bin/python
# -*- coding: utf-8 -*-

#Autor: Erickson Silva 
#Email: <erickson.silva@lavid.ufpb.br> <ericksonsilva@live.com>

#LAViD - Laboratório de Aplicações de Vídeo Digital

import sys, inspect
from ThreadTradutor import *
from LerDicionarios import *

taxas = []
dicionario = LerDicionarios()
try:
	classe_pai = inspect.getframeinfo(inspect.getouterframes(inspect.currentframe())[1][0])[0]
	if classe_pai == "TranslationServer.py":
		dicionario.carregar_dicionarios()
except:
	pass

def traduzir(texto, lang="pt_br",threads=False, taxa_qualidade=False):
	if texto.isspace() or texto == "":
		return "ESCOLHER TEXTO CERTO"
	elif threads:
		return iniciar_com_threads(texto, taxa_qualidade,lang)
	return iniciar_sem_threads(texto, taxa_qualidade,lang)
	
def iniciar_com_threads(texto, taxa_qualidade,lang="pt_br"):
	texto_quebrado = quebrar_texto(texto)
	num_threads = len(texto_quebrado)
	saidas = []
	threads = []
	
	for i in range(num_threads):
		if texto_quebrado[i] > 0 and texto_quebrado[i] != " ":
			threads.insert(i, ThreadTradutor(texto_quebrado[i],taxa_qualidade,lang))
			threads[i].start()
	for i in range(num_threads):
		threads[i].join()
		saidas.append(threads[i].obter_glosa())

	if taxa_qualidade:
		return gerar_taxa_qualidade(saidas)

	try:
		return " ".join(saidas)
	except:
		return None

def iniciar_sem_threads(texto, taxa_qualidade,lang):
	texto_quebrado = quebrar_texto(texto)
	saidas = []
	for texto in texto_quebrado:
		thread_tradutor = ThreadTradutor(texto,taxa_qualidade,lang)
		thread_tradutor.start()
		thread_tradutor.join()
		glosa = thread_tradutor.obter_glosa()
		if type(glosa) == bytes:
			glosa = glosa.decode()
		saidas.append(glosa)
	if taxa_qualidade:
		return gerar_taxa_qualidade(saidas)
	return " ".join(saidas)
	
def quebrar_texto(texto):
	global dicionario

	if '.' not in texto:
		return [texto]
	texto_quebrado = texto.split()
	tamanho_texto_quebrado = len(texto_quebrado)
	sentencas = []
	lista_texto = []
	for i in range(tamanho_texto_quebrado):
		lista_texto.append(texto_quebrado[i])
		if '.' in texto_quebrado[i]:
			if not dicionario.has_pron_tratam(texto_quebrado[i].lower()) and i < tamanho_texto_quebrado-1 and texto_quebrado[i+1][0].isupper():
				sentenca = " ".join(lista_texto)
				if not sentenca[-1].isdigit():
					sentenca = sentenca[:-1]+"."
				sentencas.append(verificar_texto_maiusculo(sentenca))
				lista_texto = []
				continue
	if lista_texto:
		sentencas.append(verificar_texto_maiusculo(" ".join(lista_texto)))
	return sentencas

def verificar_texto_maiusculo(texto):
	if texto.isupper:
		texto_lower = texto.lower()
		return texto_lower.capitalize()
	return texto

def gerar_taxa_qualidade(lista_saidas):
	soma_taxas = 0
	quant_analise_sintatica = 0
	glosas = []
	for saida in lista_saidas:
		glosas.append(saida['glosa'])
		soma_taxas += saida['taxa']
		if saida['sintatica'] is True:
			quant_analise_sintatica += 1

	taxa_sintatica = (float(quant_analise_sintatica)/len(lista_saidas)) * 0.20
	taxa_sentenca = (float(soma_taxas)/len(lista_saidas)) * 0.80
	return {'glosa':" ".join(glosas), 'taxa_qualidade': float("%.2f" % (taxa_sintatica+taxa_sentenca))}

if __name__ == '__main__':
	texto = sys.argv[1]
	try:
		lang = sys.argv[2]
		glosa = traduzir(texto,lang)
	except IndexError:
		glosa = traduzir(texto)

	print(glosa)