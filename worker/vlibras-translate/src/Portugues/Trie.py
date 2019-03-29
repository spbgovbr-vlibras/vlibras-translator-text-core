#!/usr/bin/python
# -*- coding: utf-8 -*-


class Node:
	def __init__(self, end = False):
		self.end = end
		self.children = {}

class Trie:
	def __init__(self, characters):
		self.characters = characters
		self._parse_characters()
		self.root = Node()

	def _parse_characters(self):
		self.characters_keys = {}
		for i in range(len(self.characters)):
			self.characters_keys[self.characters[i]] = i

	def _key_of(self, item, i):
		return self.characters_keys[item[i].encode('utf-8')]
 	
	def _add(self, item):
		node = self.root
		item = list(item.decode('utf-8'))
		for i in range(len(item)):
			key = self._key_of(item, i)
			if key not in node.children:
				node.children[key] = Node()
			node = node.children[key]
		node.end = True

	def _to_json(self, node):
		keys = [];
		children = {}
		for key, value in node.children.items():
			keys.append(key)
			children[key] = self._to_json(value)
		keys.sort()
		return { 'end': node.end, 'keys': keys, 'children': children }

	def add(self, data):
		if type(data) is list:
			for d in data:
				if not d in ignore:
					self._add(d)
		else:
			self._add(data)

	def to_json(self):
		return self._to_json(self.root)

chars = ["'", '$', ',', '_', '%', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
		'A', 'Á', 'Â', 'Ã', 'À', 'B', 'C', 'Ç', 'D', 'E', 'É', 'Ê', 'F', 'G', 'H',
		'I', 'Í', 'J', 'K', 'L', 'M', 'N', 'O', 'Ó', 'Ô', 'Õ', 'P', 'Q', 'R', 'S',
		'T', 'U', 'Ú', 'V', 'W', 'X', 'Y', 'Z']

ignore = ["[INTERROGAÇÃO]", "[EXCLAMAÇÃO]", "[PONTO]"]

def gen(data):
	trie = Trie(chars)
	trie.add(data)
	return { 'characters': chars, 'keys': trie.characters_keys, 'trie': trie.to_json() }