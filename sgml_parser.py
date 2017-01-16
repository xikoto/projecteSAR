'''
SGML Parser
@author: Vicent Blanes Selva
@author: David Picornell Carpi
'''
import sys


def parse(text):
	#deixa les etiquetes en una linea a banda	
	text = text.replace('<', '\n<')
	text = text.replace('>', '>\n')

	return text

def busqueda(etiqueta, text):
	#conjunto guarda el contenido de las multiples etiquetas	
	conjunto = []
	#contenido guarda todas las lineas que componen una etiqueta	
	contenido = []
	bandera = 0
	for linea in text.split('\n'):
		#si es etiqueta de apertura		
		if linea.strip() == ('<'+etiqueta+'>'):
			bandera = 1
			contenido = []
		#si es etiqueta de tancament
		elif linea.strip() == ('</'+etiqueta+'>'):
			conjunto.append(contenido)
			bandera = 0
		#si es una linea del mig		
		else:
			#la bandera esta activa, estic pillant el contingut entre dos etiquetes (obertura i tancament)			
			if bandera:			
				contenido.append(linea.strip())

	return listOfStrings(conjunto)

def listToString(llista):
    cadena = ""
    for paraula in llista:
        cadena = cadena + paraula + " "
    return cadena

def listOfStrings(listOfList):
    for i in range(len(listOfList)):
        listOfList[i] = listToString(listOfList[i])
    return listOfList

if __name__ == "__main__":

    nom = sys.argv[1]
    eti = sys.argv[2]
    contingut = open(nom).read()
    text = parse(contingut)
    flag = 1
    while flag:
        res = busqueda(eti, text)
        res = listOfStrings(res)
        flag = 0
        print(res)
        


		
	
