#!/usr/bin/python
# -*- coding: utf-8 -*-

# Autor: Erickson Silva
# Email: <erickson.silva@lavid.ufpb.br> <ericksonsilva@live.com>

# LAViD - Laboratório de Aplicações de Vídeo Digital

#from ClassificaSentencas import *
#from AplicaRegras import *
#from AplicaSinonimos import *
#from Factory import *
import subprocess
import re
import string
import sys


class TraduzSentencas(object):
    '''Realiza a tradução do texto em português para glosa
    '''

    def __init__(self, lang="pt_br"):
        '''Instancia os aplicadores de regras e sinônimos.
        '''
        #self.classificador = ClassificaSentencas()
        #self.aplic_regras = AplicaRegras()
        #self.aplic_sin = AplicaSinonimos()

        #fact = Factory(lang)
        #self.classificador = fact.get_Classificador()
        #self.aplic_regras = fact.get_AplicaRegras()
        #self.aplic_sin = fact.get_AplicaSinonimos()
        # fact.define_class()

        self.dic_lang = {"pt_br": ["ClassificaSentencas", "AplicaRegras", "AplicaSinonimos"],
                         "en": ["ClassificaSentencas_Ingles", "AplicaRegras_Ingles", "AplicaSinonimos_Ingles"],
                         "es": ["ClassificaSentencas_Espanhol", "AplicaRegras_Espanhol", "AplicaSinonimos_Espanhol"]}

        self.classificador = __import__(self.dic_lang[lang][0]).ClassificaSentencas()
        self.aplic_regras = __import__(self.dic_lang[lang][1]).AplicaRegras()
        self.aplic_sin = __import__(self.dic_lang[lang][2]).AplicaSinonimos()

    def iniciar_traducao(self, sentenca, taxa=False):
        '''Metódo responsável por executar todos componentes necessários para a geração da glosa.
        '''
        try:
            has_sintatica = True
            analise_sintatica = self.classificador.iniciar_classificacao(sentenca)
        except Exception as ex:
            analise_sintatica = None
            has_sintatica = False

        analise_morfologica = self.classificador.obter_classificacao_morfologica()

        # print('analise_morfologica', analise_morfologica)

        if (isinstance(analise_sintatica, type(None))):
            regras_aplicadas = self.aplic_regras.aplicar_regras_morfo(analise_morfologica)
            # print('1regras_aplicadas', regras_aplicadas)
        else:
            try:
                regras_aplicadas = self.aplic_regras.aplicar_regras_sint(analise_morfologica, analise_sintatica)
                # print('2regras_aplicadas', regras_aplicadas)
            except:
                regras_aplicadas = self.aplic_regras.aplicar_regras_morfo(analise_morfologica)
                # print('3regras_aplicadas', regras_aplicadas)

        sentenca_corrigida = self.aplic_regras.simplificar_sentenca(regras_aplicadas)

        # print('sentenca_corrigida', sentenca_corrigida)

        #glosa = " ".join([x[0] for x in sentenca_corrigida])

        if sentenca_corrigida:
            texto_com_sinonimos = self.aplic_sin.aplicar_sinonimos(sentenca_corrigida)
            if taxa:
                taxa_qualidade = self.gerar_metrica_qualidade(texto_com_sinonimos)
                return {'glosa': texto_com_sinonimos.upper(), 'taxa': taxa_qualidade, 'sintatica': has_sintatica}
            return texto_com_sinonimos.upper()
        return "TEXTO ERRADO ESCOLHER OUTRO"

    def gerar_metrica_qualidade(self, lista):
        # TODO: resolver path do arquivo
        arqSinais = open("sinais.txt", "r").read().split()
        quantSinaisTotal = len(lista)
        quantSinaisEncontradas = 0
        for x in lista:
            if x[0].upper() + ".anim" in arqSinais:
                quantSinaisEncontradas += 1
            else:
                if x[1] == "NPR":
                    quantSinaisTotal -= 1
        return float(quantSinaisEncontradas) / quantSinaisTotal
