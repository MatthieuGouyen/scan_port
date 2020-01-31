#! /usr/bin/env python3
import os
import socket
import subprocess
import time
from tqdm import tqdm #barre d'avancement
import re		#Matche la regex
#import chardet #Ne fonctionne malheuresement pas correctement

def match (string,reg):
	"""Va renvoyer la valeur du match de la regex : None = mauvaise regex ou encodage"""
	test=re.match(reg, string)
	return test

def requestversion(request, port):
	"""Va envoyer la requête au port voulu et retourner le port, le nom et la version"""
	name=services(port)
	if name =='microsoft-ds' and port == 445: 	#nmap simple trouve microsoft tandis que nmap -sV trouve netbios-ssn, sûrement une erreur dans le dictionnaire...
		name=services(139)
	connection.send(request)
	version=connection.recv(2000)			#Problème ici de codec. Oui tout le monde n'utilise pas l'unicode
	#code=chardet.detect(version) 			#Ne fonctionne pas ! Renvoi un codec non fonctionnel et qui varie 
	#print(code)
	l=['ascii','big5','big5hkscs','cp037','cp273','cp424','cp437','cp500','cp720','cp737','cp775','cp850','cp852','cp855','cp856','cp857','cp858',
	'cp860','cp861','cp862','cp863','cp864','cp865','cp866','cp869','cp874','cp875','cp932','cp949','cp950','cp1006','cp1026','cp1125','cp1140',
	'cp1250','cp1251','cp1252','cp1253','cp1254','cp1255','cp1256','cp1257','cp1258','cp65001','euc_jp','euc_jis_2004','euc_jisx0213', 'euc_kr',
	 'gb2312','gbk','gb18030','hz','iso2022_jp','iso2022_jp_1','iso2022_jp_2','iso2022_jp_2004','iso2022_jp_3','iso2022_jp_ext','iso2022_kr',
	 'latin_1','iso8859_2','iso8859_3','iso8859_4','iso8859_5','iso8859_6','iso8859_7','iso8859_8','iso8859_9','iso8859_10','iso8859_11',
	 'iso8859_13','iso8859_14','iso8859_15','iso8859_16','johab','koi8_r','koi8_t','koi8_u','kz1048','mac_cyrillic','mac_greek','mac_iceland',
	 'mac_latin2','mac_roman','mac_turkish','ptcp154','shift_jis','shift_jis_2004','shift_jisx0213','utf_32','utf_32_be','utf_32_le',
	 'utf_16','utf_16_be','utf_16_le','utf_7','utf_8','utf_8_sig','iso8859-15']
#Cette liste de codecs va donc être utilisée pour matcher la regex
	with open("nmap-service-probes","r") as g:	#Ouverture de nmap-service-probes pour matcher et récuperer le proto et la version	
		ligne=g.readlines()
	b=0	
	while b <len(ligne):				#Pour chaque ligne du fichier
		espace=ligne[b].split()			#On découpe en espace
		if len(espace) > 1:				#Si la phrase contient plusieurs espaces, on enlève ainsi toutes les phrases sans valeurs
			if espace[0] == 'match' and espace[1] == name:	#Si la phrase commence par match et par notre service
				trio=ligne[b].split(" ",2)	#On sépare cette phrase en trois : match, le service et le reste
				reg=trio[2].split(" p/")	#On isole la regex du reste
				regp=reg[0].replace("m|","").replace("m=","").replace("|s","").replace("=s","")	#On rend "pur" la regex"
				n=0
				while n < len(l) :	#Le but ici est de tester tous les encodages et regex pour matcher
					try:
						try :
							v2=version.decode()
						except (LookupError,UnicodeDecodeError):
							v2=version.decode(l[n],'ignore')
						if match(v2,regp) :	#Si ça match, après test, il y en a plusieurs au sein de service-probes
							sproto=reg[1].split('/ v/')#On va donc essayer d'en éliminer pour récupérer que celui avec v/ soit la version
							if len(sproto) >1:	#L'élimination se fait ici
								prot=sproto[0]	#Le protocole est la première partie de ce split
								sversion=sproto[1].split('/ i/')
								if len(sversion) > 1:
									ver=sversion[0]	#La version se récupère de la même manière que le protocole
									version=prot+ver
									n=len(l)
									b=len(ligne)
								else:
									n=len(l)
							else :
								n=len(l)
						else:
							n+=1
					except LookupError :		#LookupError est obtenue lorsque l'on ne peut pas décoder la version
						n+=1
		b+=1
	connection.close()
	return port, name , version



def services(port) :							
	"""Retourne le service du port fourni"""
	with open("nmap-services","r") as f:		#Ouverture du fichier nmap-services où sont sotckés les noms des services
		list1 = f.readlines()
	for l in list1:
		test=(l.split()[1])						#nmap-services contient les ports en tcp et udp et on veut du tcp
		test2=test.split('/')
		if test2[1] != "udp" and test2[0] == str(port): #On récupère le nom en fonction du port
			return l.split()[0]

if __name__=="__main__":	
	os.system('clear')
	ip_dest=input("Entre ip victime : ")
	port=1
	time1=time.time()
	list_port=list()
	port_name=list()
	banner=list()
	for i in tqdm(range(1000)):					#On scanne ici les 1000 premiers ports
		connection=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #On ouvre le socket
		essai=connection.connect_ex((ip_dest, port))	#On essaie de se connecter, renvoi 0 si c'est une réussite
		if essai== 0:
			port, name, version = requestversion(b'\0\0\0\xa4\xff\x53\x4d\x42\x72\0\0\0\0\x08\x01\x40\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x40\x06\0\0\x01\0\0\x81\0\x02PC NETWORK PROGRAM 1.0\0\x02MICROSOFT NETWORKS 1.03\0\x02MICROSOFT NETWORKS 3.0\0\x02LANMAN1.0\0\x02LM1.2X002\0\x02Samba\0\x02NT LANMAN 1.0\0\x02NT LM 0.12\0',port)								#Requête pour les ports 139 et 445 trouvé dans nmap-service-probes


			port_name.append(port)			#Pour chaque port ouvert, on enregistre son nom, son port et sa version
			list_port.append(name)
			banner.append(version)
		port+=1
	for i in range (len(list_port)):		#On affiche le tout à la fin du scan
		print(list_port[i],port_name[i],banner[i])
	time2=time.time()-time1
	connection.close()
	print("Time of the scan :",time2)

