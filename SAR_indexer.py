"""
    SAR indexer 
    Team: David Picornell Carpi
          Jose Miguel Benitez
"""
import sys
import re
import os
import pickle
import sgml_parser as parser
from nltk.stem import SnowballStemmer

#Indices y lista que contendra los indices al guardarlos en disco
normalIndex = {}
titleIndex = {}
categoryIndex = {}
dateIndex = {}
finalIndex = []

my_re = re.compile('\W+')

def algoritmoOR_int(lista1,lista2):
    res = []
    i = 0
    j = 0
    while(i<len(lista1) and j<len(lista2)):
        if lista1[i] < lista2[j]:
            res.append(lista1[i])
            i += 1
        elif lista1[i] > lista2[j]:
            res.append(lista2[j])
            j += 1
        else:
            res.append(lista1[i])
            i += 1
            j += 1
    if i == len(lista1):
        while(j<len(lista2)):
            res.append(lista2[j])
            j += 1
    if j == len(lista2):
        while(i<len(lista1)):
            res.append(lista1[i])
            i += 1
    return res



def procesar_doc(doc, eti):
    
    #Guardo como string el contenido del documento
    fitx = doc.read()
    #Deja las etiquetas en lineas separadas
    fitx = parser.parse(fitx)
    #Busqueda de los cuerpos de las noticias
    textos = parser.busqueda(eti,fitx)
    
    return textos

def indexar(parsed_doc, docid,indice):
    #Para cada noticia en el documento
    for i in range(len(parsed_doc)):
        aux = parsed_doc[i]
        #Paso el texto a minuscula
        aux = aux.lower()
        #Elimino caracteres no alfanumericos
        aux = aux.replace('-',' ')
        aux = my_re.sub(' ',aux)
        #Transformamos en una lista de terminos
        aux = aux.split()
        posid = i

        #Añado al indice        
        for j in range(len(aux)):
            # Creo el id final -> {(numero documento, posicion relativa) : [lista de posiciones de palabra]}
            finalid = {(docid,posid):[j]}
            term = aux[j]            
            if term not in indice:
                indice[term] = finalid
            elif term in indice:
                dic = indice[term]
                listaPosiciones = dic.get((docid,posid),[])
                listaPosiciones.append(j)
                dic[(docid,posid)] = listaPosiciones
    return indice

def stemDicc(dic,idioma):
    res = {}
    stemmer = SnowballStemmer(idioma)
    terminos = list(dic.keys())
    diccionarios = list(dic.values())

    #Hago stemming de las keys del diccionario
    for i in range(len(terminos)):
        terminos[i]=stemmer.stem(terminos[i])

    for i in range(len(terminos)):
        #Palabra stemming del indice
        termino = terminos[i]
        #Diccionario asociado a la palabra
        valorTermino = diccionarios[i]
        #Añado cada key no existente en el diccionario final
        if termino not in res:
            res[termino] = valorTermino

        #Si existe la key, añado solo las ocurrencias que no tenia previamente
        else:
            dicto = res[termino]
            if(type(dicto) == list):
                print('MAGIA ARCANA')
                print(i)
                print(terminos[i-1])
                print(diccionarios[i-1])
                print(dicto)
                sys.exit()
            listaKeys = list(dicto.keys())
            for tupla in list(valorTermino.keys()):
                if tupla not in listaKeys:
                    dicto[tupla] = valorTermino[tupla]
                else:
                    #La magia del OR
                    res[termino][tupla] = algoritmoOR_int(dicto[tupla],valorTermino[tupla])
    return res

if __name__ == '__main__':
    if(len(sys.argv)!=3):
        print('Usage: python3 SAR_indexer.py <ruta directorio> <nombre de indice>')
        sys.exit()
    lengths = {}
    ruta = sys.argv[1]
    index = sys.argv[2]
    fitxers = os.listdir(ruta)
    docid = 0
    #Recorro los ficheros buscando en los cuerpos de las noticias e indexando en su correspondiente indice
    for fitxer in fitxers:
        doc = open(ruta+'/'+fitxer, 'r')
        text_doc = procesar_doc(doc, 'TEXT')
        docid = docid+1
        indexar(text_doc,docid,normalIndex)
        lengths[docid]=len(text_doc)

    #Recorro los ficheros buscando en los titulos e indexando en su correspondiente indice
    docid = 0
    for fitxer in fitxers:
        doc = open(ruta + '/' + fitxer, 'r')
        title_doc = procesar_doc(doc, 'TITLE')
        docid = docid + 1
        indexar(title_doc, docid, titleIndex)

    #Recorro los ficheros buscando en la etiqueta de categoria e indexando en su correspondiente indice
    docid = 0
    for fitxer in fitxers:
        doc = open(ruta + '/' + fitxer, 'r')
        cat_doc = procesar_doc(doc, 'CATEGORY')
        docid = docid + 1
        indexar(cat_doc, docid, categoryIndex)

    docid = 0
    for fitxer in fitxers:
        doc = open(ruta + '/' + fitxer, 'r')
        date_doc = procesar_doc(doc, 'DATE')
        docid = docid + 1
        indexar(date_doc, docid, dateIndex)

    #Creo los diccionarios stemmizados
    idioma = "spanish"
    normalStem = stemDicc(normalIndex, idioma)
    titleStem = stemDicc(titleIndex, idioma)
    catStem = stemDicc(categoryIndex, idioma)

    #Añado a una lista final todos los indices para guardarlos en disco
    finalIndex.append(normalIndex)
    finalIndex.append(titleIndex)
    finalIndex.append(categoryIndex)
    finalIndex.append(normalStem)
    finalIndex.append(titleStem)
    finalIndex.append(catStem)
    finalIndex.append(dateIndex)
    finalIndex.append(lengths)


    #Guardo el archivo en disco con el nombre que se le ha proporcionado por consola
    print('Created index: normalIndex, titleIndex, categoryIndex, normalStem, titleStem, catStem, dateIndex')
    pickle.dump(finalIndex, open(index,'wb'))
