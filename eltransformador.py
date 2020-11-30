import numpy as np
import pandas as pd
import itertools
import ast
import time
import csv
import sys
from datetime import datetime, timedelta
import os

#nombre_archivo = "3A47_3A00"


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def generar_carga_caida(fecha, fecha_inicio, fecha_termino, archivo):

    nombre_archivo = os.path.join('momentaneo', archivo )
    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S')
    fecha_termino = datetime.strptime(fecha_termino, '%Y-%m-%d %H:%M:%S')
    #Cada cuanto revisa las matrices, eje: 1 para cada segundo, 60 para cada un minuto
    intervalo_salto = 1

    vector_listas = []
    b = []
    print("cuatro")
    #vector_listas.append(['id', 'promedio', 'mediana','std', 'var', 'min', 'max', 'rango'])
    the_contador = 1
    matriz = ""
    contadorql = 24*15*intervalo_salto
    print(nombre_archivo)
    with open( nombre_archivo , 'r') as f:
        for linea in f:
            
            if contadorql >=24*15*intervalo_salto:
                linea = linea.replace("{", "[").replace("}", "]").replace("nan", "-99").replace("NaN", "-99")
                matriz = matriz + linea
                if the_contador==24 :
                    res = []
                    #b = np.concatenate(np.array(ast.literal_eval(matriz)))
                    b = np.array(ast.literal_eval(matriz))
                    #b = sorted(b)

                    #b = np.array(b)
                    mediana = np.median(b)
                    np.where(b == -99, mediana, b)
                    b[b > 80] = mediana
                    b[b < -40] = -40

                    #res.append(np.mean(b))
                    res.append(mediana)
                    #res.append(np.var(b))

                    vector_listas.append(res)
                    the_contador=1
                    matriz = ""
                    contadorql = 0
                else:
                    the_contador +=1
            else:
                contadorql+=1
        
    #print("cinco")
    df = pd.DataFrame(vector_listas, columns=[ 'mediana'])
    df.index.name = 'id'
    df = df.round(decimals=2)
    #df.to_csv("3A47_3A00_CSV_INTE.csv")
    q1 = df.mediana.quantile(0.25)
    q3 = df.mediana.quantile(0.75)
    rango_iq = q3-q1
    val_aes = q3+3*rango_iq
    val_aei = q3-3*rango_iq
    presencia = []
    for index, row in df.iterrows():
        if row['mediana'] > val_aes or row['mediana'] < val_aei:
            presencia.append("1")
        else:
            presencia.append("0")

    cantidad_matrices = int(file_len(nombre_archivo)/(24))

    df['presencia'] = presencia
    #df.to_csv("3A47_3A00_CSV_conprsencia.csv")

    fecha_1 = fecha_inicio
    fecha_2 = fecha_termino
    #print(fecha_2 - fecha_1)
    dif_horas = int(((fecha_2 - fecha_1).seconds)/60)
    #print(dif_horas)
    ctn_matrices = int(file_len(nombre_archivo)/(24*15*intervalo_salto))
    print(ctn_matrices)
    presencia_final = []
    fechas = []
    fecha_inicial = fecha_1
    t = timedelta(minutes=1)
    if ctn_matrices >= dif_horas:
        resultado_m = int((ctn_matrices)/dif_horas)
        #print("RESULTADO FINAL : ", resultado_m)
        for i in range(0, 60):
            if presencia[i*resultado_m:i*resultado_m+resultado_m].count("1") >= 1:
                presencia_final.append("1")
                fechas.append(fecha_inicial)
                fecha_inicial = fecha_inicial+t

            else:
                presencia_final.append("0")
                fechas.append(fecha_inicial)
                fecha_inicial = fecha_inicial+t

    else:
        print("no se puede ")
        os.remove(nombre_archivo)
    resultado_final = {'fecha': fechas, 'presencia': presencia_final}
    df2 = pd.DataFrame(data=resultado_final)
    #df2.to_csv("3A47_3A00_CSV_FINAL.csv")
    os.remove(nombre_archivo)
    return df2