#!/usr/bin/python
# -*- coding: utf-8 -*-

# Autor: Erickson Silva
# Email: <erickson.silva@lavid.ufpb.br> <ericksonsilva@live.com>

# LAViD - Laboratório de Aplicações de Vídeo Digital

import re
import xml.etree.ElementTree as ET
from os.path import expanduser
from os import environ, path
from collections import deque
from LerDicionarios import *
from Iterator import *
from ConverteExtenso import *
from nltk_tgrep import tgrep_positions, tgrep_nodes
from nltk import ParentedTree, Tree, draw
from unidecode import unidecode


class AplicaRegras(object):
    '''Aplica as regras morfológicas e sintáticas após a análise morfológica/sintática.
    '''

    def __init__(self):
        '''Define funções para campos especificos do arquivo de regras.
        '''
        self.__root = self.get_root()
        self.dicionarios = LerDicionarios()
        # Dicionário de funcões do campo specific do arquivo de regras
        self.__especificos = {"advt": self.verificar_adv_tempo, "v": self.verificar_vb_infinitivo, "x": self.verificar_preposicao,
                              "c": self.verificar_subst_genero, "a": self.verificar_artigo, "l": self.verificar_vb_ligacao,
                                                                "i": self.verificar_adv_intensidade, "vbi": "zero", "n": self.verificar_vb_muda_negacao, "abmn": "zero",
                              "adji": "zero", "adjn": "zero", "advi": "zero"}

        self.__acoes = {"change_vb": self.get_vb_infinitivo}

    # Gera arvore a partir do arquivos regras.xml
    def get_root(self):
        '''Verifica qual o SO e gera o path de onde se encontra o diretório data.
        '''
        if "TRANSLATE_DATA" in environ:
            arq_regras = path.join(environ.get("TRANSLATE_DATA"), "regras.xml")
            return ET.parse(arq_regras).getroot()
        return ET.parse(expanduser("~") + '/vlibras-translate/data/regras.xml').getroot()

    # def p(self, action, newprop, newtoken, newtokenpos, specific):
    # 	print('\n'+'#'*30)
    # 	print('# action ' +      ('None' if action is None else action.text))
    # 	print('# newprop ' +     ('None' if newprop is None else newprop.text))
    # 	print('# newtoken ' +    ('None' if newtoken is None else newtoken.text))
    # 	print('# newtokenpos ' + ('None' if newtokenpos is None else newtokenpos.text))
    # 	print('# specific ' +    ('None' if specific is None else specific.text))
    # 	print('#'*30+'\n')

    # Aplica regras morfológicas apartir do arquivo regras.xml
    def aplicar_regras_morfo(self, lista, sint=False):
        # print('\n\n\n>>> RULES MORPHO')
        '''Aplica regras morfológicas na lista de tuplas.
        '''
        self.lista = list(lista)  # Nova cópia da lista morfológica
        self.lista_corrigida = []  # Lista morfológica após a aplicação das regras

        it = Iterator()
        it.load(self.lista)

        while(it.has_next()):
            for morpho in self.__root.findall('morphological'):
                self.has_rule = False  # Boolean caso encontre encontre regra compativel
                for rule in morpho.findall('rule'):
                    # Verifica se a regra está ativa e se o nome da regra, ou o ínicio, é igual a tag de classificação do token atual

                    a = rule.find("active").text == "true"  # print('rule.find("active").text == "true"', a)
                    b = rule.get('name').split("_")[0] == it.get_ticket()  # print('rule.get(\'name\').split("_")[0] == it.get_ticket()', b)
                    if a and b:
                        count = int(rule.find('count').text)
                        self.lista_iteracoes = []  # Lista que conterá todas tuplas referentes a quantidade de classes da regra

                        # Obtém o intervalo de tuplas de acordo com o número de classes da regra
                        try:
                            self.lista_iteracoes = it.get_interval(count)
                        except:
                            continue

                        # Gera o nome da regra do intervalo de tuplas e verifica se é igual ao nome da regra em si
                        # print('self.lista_iteracoes', self.lista_iteracoes)
                        self.nome_regra = self.gerar_nome_regra(self.lista_iteracoes)
                        # print('nome_regra', self.nome_regra)
                        if rule.get('name') == self.nome_regra:
                            self.has_rule = True
                            self.count_iteracao_regra = -1

                            # print "REGRA MORFOLÓGICA ENCONTRADA: " + rule.get('name')

                            self.lista_iteracao_regra = []  # Lista temporária | Insere tokens após a aplicação das regras
                            # i = 0
                            # print('INNER FOR LOOP')
                            for classe in rule.iter('class'):  # for nas tags class
                                action = classe.find('action')
                                newprop = classe.find('newprop')
                                newtoken = classe.find('newtoken')
                                newtokenpos = classe.find('newtokenpos')
                                specific = classe.find('specific')
                                # print('>>>>>>>>>>>>>>' + str(i));i+=1
                                # self.p(action, newprop, newtoken, newtokenpos, specific)

                                self.count_iteracao_regra += 1
                                tupla = self.lista_iteracoes[self.count_iteracao_regra]

                                if specific is not None:
                                    # print('specific is not None')
                                    result_specific = self.__especificos[specific.text](tupla[0])
                                    # print('self.__especificos ' + str(self.__especificos.keys()))
                                    # print('specific.text ' + specific.text)
                                    # print('tupla[0] ' + tupla[0])
                                    # print('>>>>>> result_specific ' + str(result_specific))
                                    if result_specific is False:
                                        # print('result_specific is False')
                                        # print "REGRA MORFOLÓGICA " + rule.get('name') + " INVÁLIDA. PROCURANDO OUTRA..."
                                        self.has_rule = False
                                        break

                                if action is not None:
                                    # print('action is not None')
                                    action_text = action.text
                                    if action_text == "remove":
                                        # print('action_text == "remove"')
                                        self.lista_iteracao_regra.append(None)
                                        # print('remove self.lista_iteracao_regra', self.lista_iteracao_regra)
                                        continue
                                    elif action_text == "invert":
                                        # print('action_text == "invert"')
                                        self.lista_iteracao_regra.reverse()
                                    elif action_text in self.__acoes:
                                        # print('action_text in self.__acoes')
                                        result_action = self.__acoes[action_text](tupla[0]).lower()
                                        self.lista_iteracao_regra.append([result_action, tupla[1]])
                                else:
                                    self.lista_iteracao_regra.append(tupla)

                                if newprop is not None:
                                    # print('newprop is not None')
                                    self.lista_iteracao_regra[self.count_iteracao_regra][1] = newprop.text

                                if newtoken is not None:
                                    # print('newtoken is not None')
                                    if newtokenpos.text == "next":
                                        # print('newtokenpos.text == "next"')
                                        # print('lista_iteracao_regra', self.lista_iteracao_regra, 'tupla', tupla, '\n\n\n')
                                        self.lista_iteracao_regra.append([newtoken.text.lower(), "NTK"])
                                        # print('lista_iteracao_regra', self.lista_iteracao_regra, 'tupla', tupla, '\n\n\n')
                                    elif newtokenpos.text == "previous":
                                        # print('newtokenpos.text == "previous"')
                                        self.lista_iteracao_regra.append(self.lista_iteracao_regra[-1])
                                        self.lista_iteracao_regra[-2] = [newtoken.text.lower(), "NTK"]
                                    elif newtokenpos.text == "end":
                                        # print('newtokenpos.text == "end"')
                                        print("TODO")

                        if self.has_rule:
                            # print('self.has_rule')
                            it.skip(count - 1)
                            self.lista_corrigida.extend(self.lista_iteracao_regra)
                            break

                # print('self.has_rule', self.has_rule)
                if self.has_rule is False:
                    # print('self.has_rule is False')
                    # print('BREAK!!!!!!!!!!!!!!')
                    # print 'NÃO ACHOU REGRA - ' + it.get_word().encode('utf-8')
                    self.lista_corrigida.append(it.get_token())  # se nao achou regra, entao adiciona a tupla original
        # print('>>>END RULES MORPHO\n\n\n')
        if sint:
            # print('sint')
            return self.lista_corrigida
        return [_f for _f in self.lista_corrigida if _f]

    def aplicar_regras_sint(self, lista, arvore):
        '''Aplica regras sintáticas na árvore.
        '''
        p_arvore = ParentedTree.convert(arvore)
        self.adaptar_regras_morfo_arvore(lista, p_arvore)
        for morpho in self.__root.findall('syntactic'):
            for rule in morpho.findall('rule'):  # procura a tag rule
                nome_regra = self.corrigir_nome_regra(rule.get('name'))
                regra = self.separar_regra(nome_regra)
                node_pai = tgrep_nodes(p_arvore, regra[0], search_leaves=False)
                if node_pai and rule.find('active').text == "true":
                    node_pai = node_pai[0]
                    node_regra = tgrep_nodes(node_pai, regra[1].replace('$', '..'), search_leaves=False)
                    if node_regra:
                        node_esq_pos = tgrep_positions(node_pai, regra[1], search_leaves=False)
                        node_dir_pos = tgrep_positions(node_pai, regra[2], search_leaves=False)
                        if node_esq_pos and node_dir_pos:
                            # print "REGRA SINTÁTICA ENCONTRADA: " + rule.get('name')
                            nodes_positions = node_esq_pos + node_dir_pos
                            self.count = -1
                            self.has_rule = True

                            count_temp = -1
                            for classe in rule.findall('class'):
                                count_temp += 1
                                leaves = node_pai[nodes_positions[count_temp]].leaves()
                                token = filter(None, leaves)[0]
                                specific = classe.find('specific')
                                if specific is not None:
                                    result_specific = self.__especificos[specific.text](token)
                                    if result_specific is False:
                                        self.has_rule = False

                            if self.has_rule is False:
                                # print "REGRA SINTÁTICA " + rule.get('name') + " INVÁLIDA. PROCURANDO OUTRA..."
                                break

                            nodes_deleted = []

                            for classe in rule.iter('class'):
                                action = classe.find('action')
                                newprop = classe.find('newprop')
                                title_text = classe.find('title').text

                                self.count += 1

                                if action is not None:
                                    action_text = action.text

                                    if action_text == "remove":
                                        pos_del = nodes_positions[self.count]
                                        nodes_deleted.append(node_pai[pos_del])
                                        node_pai[pos_del] = None
                                        continue

                                    elif action_text == "invert":
                                        aux1 = node_pai[nodes_positions[self.count]]
                                        aux2 = node_pai[nodes_positions[self.count + 1]]
                                        node_pai[nodes_positions[self.count]] = None
                                        node_pai[nodes_positions[self.count + 1]] = None
                                        node_pai[nodes_positions[self.count]] = aux2
                                        node_pai[nodes_positions[self.count + 1]] = aux1

                                    elif action_text == "concate_intens":
                                        if title_text == "ADV-R":
                                            node_prev = nodes_deleted.pop()
                                            label_prev = node_prev[0][0].label()
                                            token_prev = filter(None, node_prev).leaves()[0]
                                            token = filter(None, node_pai[nodes_positions[count_temp]].leaves())[0]
                                            specific = classe.find('specific')
                                            result_specific = self.get_adv_intensidade(token)
                                            token_concate = result_specific + "_" + token_prev
                                            node_pai[nodes_positions[count_temp]][0][0][0] = token_concate
                                            newprop = ""
                                            if label_prev[:-2] == "VB":
                                                newprop = "VBi"
                                            elif label_prev[:-3] == "ADJ":
                                                newprop = "ADJi"
                                            node_pai[nodes_positions[count_temp]][0][0].set_label(newprop)

                                        else:
                                            token_prev = filter(None, nodes_deleted.pop()).leaves()[0]
                                            token_prev_specific = self.get_adv_intensidade(token_prev)
                                            token = filter(None, node_pai[nodes_positions[count_temp]].leaves())[0]
                                            token_concate = token_prev_specific + "_" + token
                                            node_pai[nodes_positions[count_temp]][0][0][0] = token_concate
                                            node_pai[nodes_positions[count_temp]][0][0].set_label(newprop.text)

                                    elif action_text == "concate_neg":
                                        token = filter(None, node_pai[nodes_positions[count_temp]].leaves())[0]
                                        token_concate = token + "_não"
                                        node_pai[nodes_positions[count_temp]][0][0][0] = token_concate
                                        # TODO: PRECISA ADD NEWPROP?

                                if newprop is not None:
                                    node_pai[nodes_positions[self.count]].set_label(newprop.text)

                                break
        return self.converter_arv_para_lista(p_arvore)

    def adaptar_regras_morfo_arvore(self, lista, arvore):
        '''Aplica regras morfológicas na árvore sintática.
        '''
        lista_pos_arv = []
        # Pega as posições das classificações morfológicas dos tokens na arvore sintática
        for tupla in lista:
            string_grep = self.corrigir_nome_regra(tupla[1]) + " < " + tupla[0].lower()
            node = tgrep_positions(arvore, string_grep)
            if not node:
                string_grep = self.corrigir_nome_regra(tupla[1]) + " < " + self.remover_acento(tupla[0].lower())
                node = tgrep_positions(arvore, string_grep)
            if node[0] in lista_pos_arv:
                node.reverse()
            lista_pos_arv.append(node[0])

        # Aplica regras morfológicas na lista
        morfo = self.aplicar_regras_morfo(lista, sint=True)

        # Corrige arvore de acordo com a lista após aplicar as regras morfológicas
        for i in range(0, len(morfo)):
            # TODO: Corrigir essa verificação de FUTURO e PASSADO]
            # TODO: Exclusão do nó inteiro (VBar) - Removendo palavra junto com a marcação de tempo
            # EU FELIZ PASSADO -> EU FELIZ
            if morfo[i] is not None and morfo[i][1] == "NTK" and morfo[i][0]:
                new_node = self.gerar_no(morfo[i])

                #arvore[lista_pos_arv[i-1][:-3]].insert(2, new_node)
                #arvore[lista_pos_arv[i-1][:-3]].insert(2, new_node)

                if str(arvore[lista_pos_arv[i - 1][:-3]]).count('(') > 7:
                    arvore[lista_pos_arv[i - 1][:-2]].insert(2, new_node)
                else:
                    arvore[lista_pos_arv[i - 1][:-3]].insert(2, new_node)

                try:
                    lista_pos_arv.insert(i, lista_pos_arv[i])
                except:
                    continue

            arv_ticket = arvore[lista_pos_arv[i]].label()
            arv_token = arvore[lista_pos_arv[i]][0]

            if morfo[i] is None:
                arvore[lista_pos_arv[i]] = None

            elif arv_token != morfo[i][0] and arv_ticket != morfo[i][1]:
                arvore[lista_pos_arv[i]][0] = morfo[i][0]
                arvore[lista_pos_arv[i]].set_label(morfo[i][1])

            elif arv_token != morfo[i][0]:
                arvore[lista_pos_arv[i]][0] = morfo[i][0]

            elif arv_ticket != morfo[i][1]:
                arvore[lista_pos_arv[i]].set_label(morfo[i][1])

            # draw.draw_trees(arvore)

    def converter_arv_para_lista(self, arvore):
        '''Converte árvore sintática para uma lista de tuplas (igual a lista morfológica).
        '''
        folhas = [_f for _f in arvore.leaves() if _f]
        lista_nodes = []
        for folha in folhas:
            pos = tgrep_positions(arvore, folha)
            node = arvore[pos[0][:-1]]
            # decode node[0]
            lista_nodes.append([node[0], self.corrigir_nome_regra(node.label())])
        return lista_nodes

    def remover_acento(self, texto):
        '''Remove acento de um texto.
        '''
        try:
            return unidecode.unidecode(texto)
        except:
            return normalize('NFKD', texto.encode('iso-8859-1').decode('iso-8859-1')).encode('ASCII', 'ignore')

    def gerar_no(self, s):
        '''Gera um ParentedTree do NLTK apartir da string recebida.
        '''
        all_ptrees = []
        t_string = '(' + s[1] + ' ' + s[0] + ')'
        ptree = ParentedTree.convert(Tree.fromstring(t_string))
        all_ptrees.extend(t for t in ptree.subtrees()
                          if isinstance(t, Tree))
        return ptree

    def corrigir_nome_regra(self, anotacao):
        '''Corrige nome da regra descrita no arquivo de regras para como está na árvore sintática.
        '''
        split = anotacao.split('_')
        for i in range(0, len(split)):
            split[i] = re.sub(r"[-+]", "_", split[i])
            split[i] = re.sub(r"\$", "_S", split[i])
        return "-".join(split).encode('utf-8')

    def separar_regra(self, regra):
        '''Separa a regra por nó pai e seus filhos.
        Dessa forma, conseguimos encontrar a regra sintática exata para cada caso.
        '''
        split = regra.split("(")
        split[1] = split[1].replace(")", "").split("-")
        rev = list(split[1])
        rev.reverse()
        split.append(rev)
        split[1] = ' $ '.join(split[1])
        split[2] = ' $ '.join(split[2])
        return split

    def gerar_nome_regra(self, lista):
        '''Gera nome de regra a partir da lista morfológica.
        '''
        nome_regra = []
        for t in lista:
            nome_regra.append(t[1])
        return "_".join(nome_regra)

    def verificar_adv_tempo(self, token):
        for tupla in self.lista:
            if self.dicionarios.has_adverbio_tempo(tupla[0]):
                return True
        return False

    def verificar_excecao_plural(self, token):
        return self.dicionarios.has_excecao_plural(token)

    def verificar_vb_infinitivo(self, token):
        return self.dicionarios.has_verbo_infinitivo(token)

    def verificar_preposicao(self, token):
        return self.dicionarios.has_preposicao(token)

    def verificar_subst_genero(self, token):
        return self.dicionarios.has_subst_2_generos(token)

    def verificar_artigo(self, token):
        return self.dicionarios.has_artigo(token)

    def verificar_vb_ligacao(self, token):
        return self.dicionarios.has_verbo_ligacao(token)

    def verificar_adv_intensidade(self, token):
        return self.dicionarios.has_adverbio_intensidade(token)

    def verificar_vb_muda_negacao(self, token):
        return self.dicionarios.has_verbo_muda_negacao(token)

    def get_vb_infinitivo(self, token):
        if self.dicionarios.has_verbo_infinitivo(token):
            return self.dicionarios.get_verbo_infinitivo(token)
        return token

    def get_adv_intensidade(self, token):
        return self.dicionarios.get_adverbio_intensidade(token)

    def simplificar_sentenca(self, lista):
        '''Simplifica a sentença para que possa evitar a ditalogia.
        Como por exemplo a troca de uma palavra no plural para singular.
        '''
        lista_simplificada = list(lista)
        it = Iterator()
        it.load(lista_simplificada)
        num = False
        while(it.has_next()):
            tag = it.get_ticket()

            try:
                num_romano = roman_to_int(it.get_word())
                if it.get_prev_ticket()[-2:] == "-F":
                    lista_simplificada[it.get_count()] = [num_romano + "ª", 'NUM-R']
                else:
                    lista_simplificada[it.get_count()] = [num_romano + "º", 'NUM-R']
            except:
                pass

            if tag == "NUM":
                num = True

            if tag != "NPR-P" and (tag[-2:] == "-P" or tag[-2:] == "_P") and self.verificar_excecao_plural(it.get_word()):
                singular = self.analisar_plural(it.get_word())
                lista_simplificada[it.get_count()][0] = singular

        # print('lista_simplificada', lista_simplificada)

        if num:
            try:
                lista_simplificada = self.converter_extenso(lista_simplificada)
            except:
                pass

        # print('lista_simplificada', lista_simplificada)
        return lista_simplificada

    def analisar_plural(self, token):
        '''Altera uma palavra do plural para o singular de acordo com o final da mesma.
        '''
        vogais = ['a', 'e', 'i', 'o', 'u']
        if(token[-3:] == "ões" or token[-3:] == "ães" or token[-3:] == "ãos"):
            return token[:-3] + "ão"
        elif(token[-3:] == "res" or token[-3:] == "zes" or token[-3:] == "nes"):
            if token[-4] not in vogais:
                return token[:-1]
            return token[0:-2]
        elif(token[-3:] == "ses"):
            # TODO: Algumas palavras possuem marcações gráficas na raiz singular. Ex: Gás – Gases
            if token[-4] not in vogais:
                return token[:-1]
            return token[:-2]
        elif(token[-2:] == "ns"):
            return token[0:-2] + "m"
        elif(token[-3:] == "eis"):
            return token[:-3] + "il"
        elif(token[-2:] == "is"):
            if(token[-3] == "a" or token[-3] == "e" or token[-3] == "o" or token[-3] == "u"):
                return token[:-2] + "l"
            return token
        elif(token[-1] == "s"):
            # TODO: Palavras paroxítonas ou proparoxítonas terminadas em S. Ex: lápis, vírus, tagênis, ônibus, etc
            return token[:-1]
        else:
            return token

    def converter_extenso(self, lista):
        '''Converte número por extenso para sua forma numerica.
        '''
        lista_extensos = []
        indices_deletar = []
        count = 0
        is_sequence = False
        for i in range(0, len(lista)):
            token = lista[i][0]
            tag = lista[i][1]
            if tag == "NUM" and token.isalpha():
                # Verifico se não há sequência de obtenção de extenso em andamento para começar a obter um nova sequência
                if (is_sequence is False):  # and len(lista_extensos) == count (???)
                    lista_extensos.append([i, [token]])  # i = Posição do primeiro extenso encontrado, token = número por extenso
                    is_sequence = True
                else:
                    lista_extensos[count][1].append(token)  # Pego número por extenso que está na sequência e adiciona na lista
                    indices_deletar.append(i)  # Insiro indice na lista para ser removido depois
            elif (is_sequence):
                # Se o token anterior e o próximo foram classificados como número, e o token atual como conjunção, significa que podemos remove-lo
                if ((i + 1 < len(lista)) and (lista[i - 1][1] == "NUM") and (lista[i + 1][1] == "NUM") and (tag == "CONJ")):
                    indices_deletar.append(i)
                else:
                    # A sequência foi quebrada, o que significa que selecionamos o extenso do número por completo
                    # Podemos agora procurar por outra sequencia de número por extenso na lista
                    is_sequence = False
                    count += 1

        # print('>>> lista_extensos', lista_extensos, len(lista_extensos))
        for extenso in lista_extensos:
            ext = convert_extenso(' '.join(extenso[1]))
            # print('>>>> ext', ext)
            lista[extenso[0]] = [str(ext), "NUM"]
        # print('>>> 2lista', lista)

        deque((list.pop(lista, i) for i in sorted(indices_deletar, reverse=True)), maxlen=0)
        return lista
