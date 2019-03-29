#!/usr/bin/python
# -*- coding: utf-8 -*-

#Autor: Erickson Silva 
#Email: <erickson.silva@lavid.ufpb.br> <ericksonsilva@live.com>

#LAViD - Laboratório de Aplicações de Vídeo Digital

import os
import csv

class Singleton(type):
   ''' Permite a criação de apenas uma instância da classe
   '''
   _instances = {}
   def __call__(cls, *args, **kwargs):
      if cls not in cls._instances:
         cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
      return cls._instances[cls]

class LerDicionarios(object, metaclass=Singleton):
   '''Carrega todos os arquivos (dicionários) necessários para auxiliar durante o processo de tradução.
   '''

   def __init__(self):
      self.path = self.get_path()
      self.set_exc_plural = []
      self.dic_adv_intensidade = {}
      self.set_adv_tempo = []
      self.set_art = []
      self.set_prep = []
      self.dic_sin = {}
      self.set_sb_2_gen = []
      self.set_pron_trat = []     
      self.dic_vb_infinitivo = {}
      self.set_vb_ligacao = []
      self.dic_vb_muda_negacao = []
      self.file = ''


   def get_path(self):
      '''Verifica qual o SO e gera o path de onde se encontra o diretório data.
      '''
      if "TRANSLATE_DATA" in os.environ:
         return os.environ.get("TRANSLATE_DATA")
      return os.path.expanduser("~") + "/vlibras-translate/data"      

   def montar_diretorio(self, arquivo):
      return os.path.join(self.path, arquivo)

   def carregar_dicionarios(self):
      '''Realiza a leitura dos arquivos e atribui à estruturas de dicionários e sets.
      '''
      self.carregar_excecoes_plural()
      self.carregar_adverbios_intensidade()
      self.carregar_adverbios_tempo()
      self.carregar_artigos()
      self.carregar_preposicoes()
      self.carregar_sinonimos()
      self.carregar_subs_2_generos()
      self.carregar_pronomes_tratamento()
      self.carregar_verbos_infinitivo()
      self.carregar_verbos_ligacao()
      self.carregar_verbos_muda_negacao

   def carregar_excecoes_plural(self):
      '''Carrega arquivo de exceções de plural.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("excecoesPlural.csv")))
      except IOError as xxx_todo_changeme:
         (errno, strerror) = xxx_todo_changeme.args
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_excecoes_plural")
   
      rows = []
      for row in self.file:
         rows.append(row[0])
      self.set_exc_plural = set(rows)

   def carregar_adverbios_intensidade(self):
      '''Carrega arquivo de adverbios de intensidade.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("adverbiosIntensidade.csv")), delimiter=";")
      except IOError as xxx_todo_changeme1:
         (errno, strerror) = xxx_todo_changeme1.args
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_adverbios_intensidade")
   
      for row in self.file:
         if row[1] != "":
            self.dic_adv_intensidade[row[0]] = row[1]

   def carregar_adverbios_tempo(self):
      '''Carrega arquivo de advérbios de tempo.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("adverbiosTempo.csv")))
      except IOError as xxx_todo_changeme2:
         (errno, strerror) = xxx_todo_changeme2.args
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_adverbios_tempo")
         
      rows = []
      for row in self.file:
         rows.append(row[0])
      self.set_adv_tempo = set(rows)

   def carregar_artigos(self):
      '''Carrega arquivo de artigos a serem removidos.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("artigos.csv")))
      except IOError as xxx_todo_changeme3:
         (errno, strerror) = xxx_todo_changeme3.args
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_artigos")

      rows = []
      for row in self.file:
         rows.append(row[0])
      self.set_art = set(rows)

   def carregar_preposicoes(self):
      '''Carrega arquivo de preposições a serem removidas.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("preposicoes.csv")))
      except IOError as xxx_todo_changeme4:
         (errno, strerror) = xxx_todo_changeme4.args
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_preposicoes")

      rows = []
      for row in self.file:
         rows.append(row[0])
      self.set_prep = set(rows)        

   def carregar_sinonimos(self):
      '''Carrega arquivo de sinônimos.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("sinonimos.csv")), delimiter=";")
      except IOError as xxx_todo_changeme5:
         (errno, strerror) = xxx_todo_changeme5.args
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_sinonimos")
   
      for row in self.file:
         if row[1] != "":
            try:
               self.dic_sin[row[0]] = row[1]
            except UnicodeDecodeError:
               self.dic_sin[row[0]] = row[1]

   def carregar_subs_2_generos(self):
      '''Carrega arquivo dos substantivos comuns de 2 generos.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("subs2Generos.csv")))
      except IOError as xxx_todo_changeme6:
         (errno, strerror) = xxx_todo_changeme6.args
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_subs_2_generos") 

      rows = []
      for row in self.file:
         rows.append(row[0])
      self.set_sb_2_gen = set(rows)    

   def carregar_verbos_infinitivo(self):
      '''Carrega arquivo de verbos no infinitivo.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("verbosInfinitivo.csv")), delimiter=";")
      except IOError as xxx_todo_changeme7: 
         (errno, strerror) = xxx_todo_changeme7.args 
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_verbos_infinitivo")

      for row in self.file:
         if row[1] != "": 
            try:
               self.dic_vb_infinitivo[row[0]] = row[1] 
            except UnicodeDecodeError:
               self.dic_vb_infinitivo[row[0]] = row[1]


   def carregar_verbos_ligacao(self):
      '''Carrega arquivo de verbos de ligação.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("verbosLigacao.csv")))
      except IOError as xxx_todo_changeme8:
         (errno, strerror) = xxx_todo_changeme8.args
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_verbos_ligacao")
  
      rows = []
      for row in self.file:
         rows.append(row[0].decode("utf-8"))
      self.set_vb_ligacao = set(rows) 

   def carregar_pronomes_tratamento(self):
      '''Carrega arquivo de pronomes de tratamento.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("pronomesTratamento.csv")))
      except IOError as xxx_todo_changeme9:
         (errno, strerror) = xxx_todo_changeme9.args
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_pronomes_tratamento")
  
      rows = []
      for row in self.file:
         rows.append(row[0])
      self.set_pron_trat = set(rows) 

   def carregar_verbos_muda_negacao(self):
      '''Carrega arquivo de verbos que mudam a negação.
      '''
      try:
         self.file = csv.reader(open(self.montar_diretorio("verbosMudaNegacao.csv")), delimiter=";")
      except IOError as xxx_todo_changeme10: 
         (errno, strerror) = xxx_todo_changeme10.args 
         print("I/O error(%s): %s" % (errno, strerror))
         print("carregar_verbos_muda_negacao")

      for row in self.file:
         if row[1] != "": 
            self.dic_vb_muda_negacao[row[0]] = row[1]  

   def has_excecao_plural(self, token):
      '''Verifica se o token recebido consta no arquivo de exceções de plural.
      '''
      if not self.set_exc_plural:
         self.carregar_excecoes_plural()
      return token not in self.set_exc_plural

   def has_adverbio_intensidade(self, token):
      '''Verifica se o token recebido consta no arquivo de advérbios de intensidade.
      '''
      if not self.dic_adv_intensidade:
         self.carregar_adverbios_intensidade()
      return token in self.dic_adv_intensidade

   def has_adverbio_tempo(self, token):
      '''Verifica se o token recebido consta no arquivo de advérbios de tempo.
      '''
      if not self.set_adv_tempo:
         self.carregar_adverbios_tempo()
      return token in self.set_adv_tempo

   def has_artigo(self, token):
      '''Verifica se o token recebido consta no arquivo de artigos a serem removidos.
      '''
      if not self.set_art:
         self.carregar_artigos()
      return token in self.set_art

   def has_preposicao(self, token):
      '''Verifica se o token recebido consta no arquivo de preposições a serem removidas.
      '''
      if not self.set_prep:
         self.carregar_preposicoes()
      return token in self.set_prep
      
   def has_sinonimo(self, token):
      '''Verifica se o token recebido consta no arquivo de sinonimos.
      '''
      if not self.dic_sin:
         self.carregar_sinonimos()
      return token in self.dic_sin

   def has_pron_tratam(self, token):
      '''Verifica se o token recebido consta no arquivo de pronomes de tratamento.
      '''
      if not self.set_pron_trat:
         self.carregar_pronomes_tratamento()
      return token in self.set_pron_trat

   def has_subst_2_generos (self, token):
      '''Verifica se o token recebido consta no arquivo de substantivos comuns de 2 generos.
      '''
      if not self.set_sb_2_gen:
         self.carregar_subs_2_generos()
      # print('token ' + token)
      # print('self.set_sb_2_gen ' + str(self.set_sb_2_gen))
      # print('token in self.set_sb_2_gen ' + str(token in self.set_sb_2_gen))
      return token in self.set_sb_2_gen

   def has_verbo_infinitivo(self, token):
      '''Verifica se o token recebido consta no arquivo de verbos no infinitivo.
      '''
      if not self.dic_vb_infinitivo:
         self.carregar_verbos_infinitivo()
      return token in self.dic_vb_infinitivo

   def has_verbo_ligacao(self, token):
      '''Verifica se o token recebido consta no arquivo de verbos de ligação.
      '''
      if not self.set_vb_ligacao:
         self.carregar_verbos_ligacao()
      return token in self.set_vb_ligacao

   def has_verbo_muda_negacao(self, token):
      '''Verifica se o token recebido consta no arquivo de verbos que mudam de negação.
      '''
      if not self.dic_vb_muda_negacao:
         self.carregar_verbos_muda_negacao()
      return token in self.dic_vb_muda_negacao

   def get_adverbio_intensidade(self, token):
      '''Verifica se o token recebido consta no arquivo de advérbios de intensidade.
      '''
      if not self.dic_adv_intensidade:
         self.carregar_adverbios_intensidade()
      return self.dic_adv_intensidade[token]

   def get_sinonimo(self, token):
      '''Obtém o sinônimo do token.
      '''
      if not self.dic_sin:
         self.carregar_sinonimos()
      return self.dic_sin[token]

   def get_verbo_infinitivo(self, token):
      '''Obtém o verbo no infinitivo do token.
      '''
      if not self.dic_vb_infinitivo:
         self.carregar_verbos_infinitivo()
      return self.dic_vb_infinitivo[token]

   def get_verbo_muda_negacao(self, token):
      '''Obtém o verbo que muda a negação do token.
      '''
      if not self.dic_vb_muda_negacao:
         self.carregar_verbos_muda_negacao()
      return self.dic_vb_muda_negacao[token]