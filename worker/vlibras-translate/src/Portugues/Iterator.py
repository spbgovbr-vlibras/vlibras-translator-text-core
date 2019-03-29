#!/usr/bin/python
# -*- coding: utf-8 -*-

#Autor: Erickson Silva 
#Email: <erickson.silva@lavid.ufpb.br> <ericksonsilva@live.com>

#LAViD - Laboratório de Aplicações de Vídeo Digital

class Iterator(object):
	'''Itera lista no formato da classfição morfológica [token,tag].
	'''
	
	def init(self):	
		self.count = -1
		
	def load(self, lista):
		'''Carrega a lista no iterator.
		'''
		self.reset()
		self.list = list(lista);
		self.size = len(lista)

	def reset(self):
		'''Reseta o iterator.
		'''
		self.count = -1

	def get_size(self):
		'''Obtém o tamanho da lista carregada.
		'''
		return self.size

	def get_count(self):
		'''Obtém o contador do iteração.
		'''
		return self.count

	def get_token(self, i=None):
		'''Obtém a tupla corrente da lista.
		Caso seja informado o parametro i, será retornado atual+i.
		'''
		if(i != None):
			return self.list[self.count+(i)]
		return self.list[self.count]

	def get_word(self):
		'''Obtém a palavra da tupla corrente.
		'''
		return self.get_token()[0]

	def get_ticket(self):
		'''Obtém a tag(classificação) da tupla corrente.
		'''
		return self.get_token()[1]

	def get_next_word(self):
		'''Obtém a palavra da próxima tupla.
		'''
		return self.get_token(1)[0]

	def get_next_ticket(self):
		'''Obtém a tag(classificação) da próxima tupla.
		'''
		return self.get_token(1)[1]		

	def get_prev_word(self):
		'''Obtém a palavra da tupla anterior.
		'''
		return self.get_token(-1)[0]

	def get_prev_ticket(self):
		'''Obtém a tag(classificação) da tupla anterior.
		'''
		return self.get_token(-1)[1]

	def get_interval(self, n):
		'''Obtém o intervalo entre a tupla corrente e contador corrente + n.
		'''
		if self.count+n > self.size:
			raise IndexError
		return self.list[self.count:self.count+n]

	def skip(self, n):
		'''Pula n iterações.
		'''
		self.count += n

	def has_next(self):
		'''Verifica se ainda há tupla a ser analisada.
		'''
		if(self.count < self.size-1):
			self.count += 1
			return True
		return False