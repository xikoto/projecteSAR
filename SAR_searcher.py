"""
    SAR searcher
    Team: David Picornell Carpi
          Jose Miguel Benítez
"""
import sys
import pickle
import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import SAR_indexer as indexer
import sgml_parser as parser
import os


#Utils
operadores = ['AND', 'OR', 'NOT']
defaultOperator = 'AND'
etis = ['headline','category','text','date']


#ALGORITMO OR
def algoritmoOR(tuples1,tuples2):
    tuples1 = sorted(tuples1)
    tuples2 = sorted(tuples2)
    res = indexer.algoritmoOR_int(tuples1,tuples2)
    return res
#Fin algoritmoOR


#ALGORITMO AND
def algoritmoAND(tuples1, tuples2):
    i = 0
    j = 0
    res = []
    tuples1 = sorted(tuples1)
    tuples2 = sorted(tuples2)

    while(i<len(tuples1) and j<len(tuples2)):
        if tuples1[i] < tuples2[j]:
            i += 1
        elif tuples1[i] > tuples2[j]:
            j += 1
        else:
            res.append(tuples1[i])
            i += 1
            j += 1
    return res
#Fin algoritmoAND



def algoritmoNOT(tuples):
    tuples = sorted(tuples)
    res = []
    lengths = list(indices[7].values())
    i = 0
    k = 0
    while(i<len(lengths)):
        j = 0
        while(j<lengths[i]):
            tupla = (i+1,j+1)
            if tupla < tuples[k] or tupla > tuples[k]:
                res.append(tupla)

            else:
                if k < len(tuples)-1:
                    k += 1
            j += 1
        i += 1
    return res
#Fin algoritmoNOT

def algoritmoANDNOT(tuples1, tuples2):
    res = []
    not_tuples2 = algoritmoNOT(tuples2)
    res = algoritmoAND(tuples1,not_tuples2)
    return res
#Fin algoritmoANDNOT


def algoritmoORNOT(tuples1, tuples2):
    res = []
    not_tuples2 = algoritmoNOT(tuples2)
    res = algoritmoOR(tuples1, not_tuples2)
    return res
    # Fin algoritmoORNOT

def superMetodoImpostorDic(dic1, dic2):
    res = {}

    for key1 in dic1.keys():
        if key1 in dic2:
            resAux = superMetodoImpostor(dic1[key1],dic2[key1])
            if resAux != []:
                res[key1] = resAux
    return res


def superMetodoImpostor(l1, l2):
    res = []
    i = 0
    j = 0
    while(i<len(l1) and j<len(l2)):
        if l1[i] < l2[j]:
            if l1[i]+1 == l2[j]:
                res.append(l2[j])
                i += 1
                j += 1
            else:
                if l1[i] < l2[j]:
                    i+=1
                else:
                    j+=1
        else:
            j+=1
    return res

#TO BE IMPLEMENTED PERO QUE FLIPES
def busquedaLiteral(busqueda, stem):
    if not stem:
        indice = indices[0]
    else:
        indice = indices[3]

    diccionaris = []
    for i in range(len(busqueda)):
        diccionaris.append(indice[busqueda[i]])
    inicial = {}
    inicial = superMetodoImpostorDic(diccionaris[0],diccionaris[1])
    if inicial != {}:
        i = 2
        while(i<len(diccionaris)):
            inicial = superMetodoImpostorDic(inicial,diccionaris[i])

    return list(inicial.keys())

#Fin busquedaLiteral


def busquedaUnaParaula(paraula, index):
    diccionari = index.get(paraula,{})
    posting = list(diccionari.keys())
    return posting
#Fin busquedaUnaParaula


def consultaEtis(consulta,stem):
    res = []
    consulta = consulta.split(':')
    word = consulta[0]
    if word in etis:
        if word == 'headline':
            if not stem:
                indice = indices[1]
                res = busquedaUnaParaula(consulta[1], indice)
            else:
                indice = indices[4]
                res = busquedaUnaParaula(consulta[1], indice)
        elif word == 'category':
            if not stem:
                indice = indices[2]
                res = busquedaUnaParaula(consulta[1], indice)
            else:
                indice = indices[5]
                res = busquedaUnaParaula(consulta[1], indice)
        elif word == 'text':
            if not stem:
                indice = indices[0]
                res = busquedaUnaParaula(consulta[1], indice)
            else:
                indice = indices[3]
                res = busquedaUnaParaula(consulta[1], indice)
        elif word == 'date':
            indice = indices[6]
            res = busquedaUnaParaula(consulta[1], indice)
    return res
#Fin consultaEtis



def parseConsulta(consulta,stem):
    if not stem:
        indice = indices[0]
    else:
        indice = indices[3]
    res = []

    for i in range(len(consulta)):
        word = consulta[i]
        if word in operadores and word != defaultOperator:
            if word == 'OR' and consulta[i+1]!='NOT':
                tuples1 = list(indice[consulta[i-1]].keys())
                tuples2 = list(indice[consulta[i+1]].keys())
                res = algoritmoOR(tuples1, tuples2)

            elif word == 'OR' and consulta[i+1]=='NOT':
                tuples1 = list(indice[consulta[i-1]].keys())
                tuples2 = list(indice[consulta[i+2]].keys())
                res = algoritmoORNOT(tuples1, tuples2)

            elif word == 'NOT':
                tuples = list(indice[consulta[i+1]].keys())
                res = algoritmoNOT(tuples)

        elif word == defaultOperator and consulta[i+1] != 'NOT':
            tuples1 = list(indice[consulta[i-1]].keys())
            tuples2 = list(indice[consulta[i+1]].keys())
            res = algoritmoAND(tuples1, tuples2)

        elif word == defaultOperator and consulta[i+1] == 'NOT':
            tuples1 = list(indice[consulta[i-1]].keys())
            tuples2 = list(indice[consulta[i+2]].keys())
            res = algoritmoANDNOT(tuples1, tuples2)

    return res
#Fin parseConsulta


def snippets(noticia, busqueda):
    snippet = []
    busquedaSnippet = []

    #Busqueda de terminos que no sean operadores o etiquetas
    for word in busqueda:
        if word not in operadores and not (':' in word):
            busquedaSnippet.append(word)
    noticia = noticia.split('.')
    #Busqueda de oraciones donde aparezcan las palabras validas para crear el snippet
    for sentence in noticia:
        for paraula in busquedaSnippet:
            if sentence.find(paraula) >= 0:
                snippet.append(sentence)
                busquedaSnippet.remove(paraula)
    #Creo el conjunto de snippets separandolos con el separador que implica texto omitido
    finalSnippet = '[...]'.join(snippet)
    return finalSnippet
#Fin snippets


#TO BE IMPLEMENTED
def retorno(posting, consulta):
    ficheros = os.listdir(dir)
    docsid = []
    for tupla in posting:
        if tupla[0] not in docsid:
            docsid.append(tupla[0])

    if len(posting) <=2:
        #Print titulo y cuerpo de las noticias
        for tupla in posting:
            fichero = open(dir+'/'+ficheros[tupla[0]-1])
            fichero = fichero.read()
            noticias = parser.parse(fichero)
            print(parser.busqueda('TITLE', noticias)[tupla[1]])
            print(parser.busqueda('TEXT', noticias)[tupla[1]])
            print('###########################################')

    elif len(posting) > 2 and len(posting) <=5:
        #Print titulo y snippets
        for tupla in posting:
            fichero = open(dir + '/' + ficheros[tupla[0] - 1]).read()
            noticias = parser.parse(fichero)
            print(parser.busqueda('TITLE', noticias)[tupla[1]])
            snippet = snippets(parser.busqueda('TEXT',noticias)[tupla[1]],consulta)
            print(snippet)
            print('###########################################')
    else:
        #Print titulos de las 10 primeras
        if len(posting) < 10:
            max_prints = len(posting)
        else:
            max_prints = 10

        for i in range(max_prints):
            tupla = posting[i]
            fichero = open(dir+'/'+ficheros[tupla[0] - 1]).read()
            noticias = parser.parse(fichero)
            print(parser.busqueda('TITLE', noticias)[tupla[1]])
            print('###########################################')


    #En todos los casos, print de los nombres de los dicheros y del tamaño total
    for id in docsid:
        print(ficheros[id-1])

    #Si no hay resultados informa al usuario
    if posting is None or len(posting) == 0:
        print('No hay resultados')
    else:
        print(len(posting))
#Fin retorno


#Metodo para eliminar stopwords de una lista de palabras
def remove_stopwords(wordlist, idioma):
    stopwords = nltk.corpus.stopwords.words(idioma)
    result = [w for w in wordlist if w.lower() not in stopwords]
    return result
#Fin remove_stopwords


#FALTA IMPLEMENTAR COSAS
if __name__ == '__main__':
    if(len(sys.argv)!= 4):
        print("Usage: python3 SAR_searcher.py <index> optional parameters: <stopwords> <stemming>")
        print("Si no quieres activar los parametros opcionales, escribe 0")
        sys.exit()

    #Cargo el archivo binario con la lista de indices
    dir = sys.argv[1]
    dir = dir[0:len(dir)-1]
    index = open(sys.argv[1],'rb')
    indices = pickle.load(index)
    indice = indices[0]
    aux_ret = [[],0]

    #Bucle de consultas
    while True:
        consulta = input('Introduce tu consulta:\n')
        if consulta == '':
            print('Hasta la proxima')
            sys.exit()
        literal = False
        stem = False

        #Comprobacion de banderas
        if sys.argv[3] != '0':
            stem = True

        if consulta[0] == '\"' and consulta[len(consulta)-1] == '\"':
            literal = True
            consulta = consulta[1:len(consulta)-1]

        #Ningun extra activado y consulta de una palabra o una etiqueta
        if (sys.argv[2] == '0' and sys.argv[3] == '0'):
            consulta = consulta.split()

        #Activado solo stopwords
        if(sys.argv[2] != '0' and sys.argv[3] == '0' and not literal):
            #Quitar stopwords
            indice = indice[0]
            consulta = remove_stopwords(consulta.split(),'spanish')

        #Activado solo stemming
        if(sys.argv[3] != '0' and sys.argv[2] == '0'):
            #Aplicar stemming
            indice = indices[3]
            stemmer = SnowballStemmer('spanish')
            consulta = consulta.split()
            for i in range(len(consulta)):
                if consulta[i] not in operadores:
                    consulta[i] = stemmer.stem(consulta[i])

        #Activado tanto stopwords como stemming
        if(sys.argv[2] != '0' and sys.argv[3] != '0'):
            indice = indices[3]
            stemmer = SnowballStemmer('spanish')
            if not literal:
                consulta = remove_stopwords(consulta.split(), 'spanish')
            for i in range(len(consulta)):
                if consulta[i] not in operadores:
                    consulta[i] = stemmer.stem(consulta[i])

        i = 0
        if literal:
            aux_ret[0] = busquedaLiteral(consulta,stem)
        else:
            while( i < len(consulta)):
                word = consulta[i]
                if word in operadores:
                    #OR == 1
                    if word == 'OR':
                        if consulta[i+1] == 'NOT':
                            #OR NOT == 4
                            aux_ret[1] = 4
                            i += 1
                        else:
                            aux_ret[1] = 1
                    #AND == 2
                    elif word == 'AND':
                        if consulta[i + 1] == 'NOT':
                            # AND NOT == 5
                            aux_ret[1] = 5
                            i += 1
                        else:
                            aux_ret[1] = 2
                    #NOT == 3
                    elif word == 'NOT':
                        aux_ret[1] = 3

                else:
                    aux = []
                    if word.find(':')>=0:
                        aux = consultaEtis(word,stem)
                    else:
                        aux = busquedaUnaParaula(word,indice)

                    if aux_ret[1] == 0:
                        aux_ret[0] = aux

                    elif aux_ret[1] == 1:
                        aux_ret[0] = algoritmoOR(aux_ret[0],aux)

                    elif aux_ret[1] == 2:
                        aux_ret[0] = algoritmoAND(aux_ret[0], aux)

                    elif aux_ret[1] == 3:
                        aux_ret[0] = algoritmoNOT(aux_ret[0], aux)

                    elif aux_ret[1] == 4:
                        aux_ret[0] = algoritmoORNOT(aux_ret[0], aux)

                    elif aux_ret[1] == 5:
                        aux_ret[0] = algoritmoANDNOT(aux_ret[0], aux)
                i+=1
        retorno(aux_ret[0],consulta)
        aux_ret[0] = []
        aux_ret[1] = 0











"""
        if len(consulta)==1:
            if(consulta[0].find(':')>=0):
                res = consultaEtis(consulta,stem)
                retorno(res, consulta)
            else:
                res = busquedaUnaParaula(consulta[0], indice)
                retorno(res, consulta)
        elif len(consulta)==2:
            if literal:

                res = busquedaLiteral(consulta,stem)
                retorno(res,consulta)
            if consulta[0] in operadores:
                if consulta[0] == 'NOT':
                    aux = busquedaUnaParaula(consulta[1],indice)
                    print(aux[0])
                    res = algoritmoNOT(aux)
                    if aux[0] in res:
                        print('liada')
                    retorno(res, consulta)
        elif len(consulta)==3 and consulta[1] in operadores:
            if consulta[1] == 'NOT':
                res = algoritmoANDNOT(list(indice[consulta[0]].keys()),list(indice[consulta[2]].keys()))
                retorno(res, consulta)
            else:
                res = parseConsulta(consulta, stem)

                retorno(res, consulta)
"""

