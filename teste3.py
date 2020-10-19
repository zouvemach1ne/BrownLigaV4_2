import cx_Oracle
import os
import sys
import time
import numpy as np
import pandas as pd
import copy

class loop:
    def __init__(self, once=False):
        self.once = once 
        if self.once: 
            while self.once:
                self.con = get_inter_from_matrix()
        else:
            self.con = get_inter_from_matrix()
                

def create_connection():
    cx_Oracle.init_oracle_client()
    cx_Oracle.clientversion()

    service_name = 'EMTPRDPDB.br1.ocm.s7104093.oraclecloudatcustomer.com'

    dsn_tns = cx_Oracle.makedsn('192.168.134.22', '1521', service_name=service_name) 
    conn = cx_Oracle.connect(user='maa18', password='Deop13#1423', dsn=dsn_tns) # (user='ealmeida1', password='Energisa*2021', dsn=dsn_tns)
    
    return conn


def get_from_sub(subestacoes):
    subs_count = 0
    cursor = conn.cursor()
    alim_exam = []
    start_time = time.clock()
    subs_did = []
    for subs in subestacoes:
        subs_count+=1
        print(f'Quanto está : {subs_count}')
        print(f'Quanto falta: {len(subestacoes) - subs_count}')
        if subs not in subs_did:
            subs_did.append(subs)
            
            cursor.execute(f"SELECT num_ele_sub, cod_sub_estd_sub FROM cad_topo_sub WHERE cod_situ_sub = 'IM' and cod_sub_estd_sub = ('{subs}')")
            result = cursor.fetchall()
            if len(result)>0:
                subs_cod = result[0][0]
                print(f'SUBESTAÇÂO EXAMINADA: {subs} - id: {subs_cod}')

                cursor.execute(f"SELECT num_ele_tpo FROM rel_elemento_top WHERE num_ele_pai_tpo = ({subs_cod}) and cod_ele_rede_tpo in('AL')")
                alimentadores = cursor.fetchall()
                print(f'ALIMENTADORES: {alimentadores}')
                rls_alimentadores = []


                for al_pai in alimentadores:
                    al_pai = al_pai[0]   
                    cursor.execute(f"SELECT num_ele_aln, cod_alim_aln FROM cad_topo_aln WHERE cod_situ_aln = 'IM' AND num_ele_aln = ('{al_pai}')")
                    al_pai_trad = cursor.fetchall()
                    print(f'ALIMENTADOR EXAMINADO: {al_pai_trad[0][1]}')

                    # consult every CH element on a feeder
                    cursor.execute(f'''
                                    SELECT 
                                    num_ele_tpo, 
                                    fun_topo(num_ele_tpo, 'cod_ele'), 
                                    fun_topo(num_ele_tpo, 'sta_oper') 

                                    FROM 
                                    rel_elemento_top 
                                    
                                    WHERE 
                                    num_alim_tpo = ('{al_pai}') 
                                    AND cod_ele_rede_tpo = ('CH') 
                                    AND fun_topo(num_ele_tpo, 'sta_oper') = 'A'
                                    AND (fun_topo(num_ele_tpo, 'cod_ele')  LIKE ('79%') OR fun_topo(num_ele_tpo, 'cod_ele')  LIKE ('89%'))
                                    ''')
                    results = cursor.fetchall()

                    elementos = []
                    for elem in results:
                        elementos.append(elem[1])

                    alim_exam.append([al_pai_trad[0][1]] + elementos)

                    print(results)
    return alim_exam


def write_text_files(subs):
    alims = get_from_sub(subs)

    with open(os.path.join(os.getcwd(),"interligações.txt" ), "w") as file:
        for i in alims:
            file.write(str(i)+'\n')
    os.startfile('interligações.txt')

    rows = len(alims)
    cols = len(alims)

    matrix = [ [0]*rows for _ in range(cols) ]

    for i in range(len(alims)-1):
        matrix[i][i] = alims[i][0] 
        for ii in range(1, len(alims[i])):
            elemento_examinado = alims[i][ii]
            for iii in range(i+1, len(alims)-1): # now loop through every alim after the i alim
                alim_search = alims[iii]
                for iiii in range(1, len(alim_search)):
                    elemento_search = alims[iii][iiii]
                    if elemento_search == elemento_examinado:
                        if matrix[i][iii] == 0:
                            matrix[i][iii] = elemento_search
                            matrix[iii][i] = elemento_search
                        else:
                            matrix[i][iii] += '-'+elemento_search
                            matrix[iii][i] += '-'+elemento_search
                        break;
    matrix[-1][-1] = alims[-1][0]

    with open(os.path.join(os.getcwd(),"interligações_matrix.txt" ), "w") as file:
        for i in matrix:
            file.write(str(i)+'\n')
    os.startfile('interligações_matrix.txt')


def get_matrix_from_txt():
    matrix = []
    with open(os.path.join(os.getcwd(),"interligações_matrix.txt" ), "r") as file:
        lines = file.readlines()
        for line in lines:
            #print(line)
            line = line.strip('\n').replace("'",'').replace(' ','').strip('[]').split(',')
            matrix.append(line)

    return matrix


def get_inter_from_matrix():
    matrix = get_matrix_from_txt()

    #for mat in matrix:
    #    #print(mat)

    alim1 = input('Qual alimentador você quer interligar? ')


    connections = []
    for i in range(len(matrix)):
        if matrix[i][i] == alim1:
            for ii in range(len(matrix[i])):
                if ii != i and matrix[i][ii] != '0' and ii != i and matrix[i][ii] != 0:
                    if '-' not in matrix[i][ii]:
                        connections.append([matrix[i][ii], matrix[ii][ii]])
                    else:
                        elems = matrix[i][ii].split('-')
                        for elem in elems:
                            connections.append([elem, matrix[ii][ii]])
    if len(connections) > 0:
        print(f'Você pode interligar o alimentador {alim1} pelos elementos:')
        for i in connections:
            print(f'Elemento: {i[0]} -> Alimentador: {i[1]} ')
    else:
        print(f'Este alimentador não possui interligação.')
    
    return connections, alim1


def unwrap_from_fetch(fetch, index):
    elementos = []
    for elem in fetch:
        elementos.append(elem[index])

    return elementos




#conn = create_connection()
#cursor = conn.cursor()
#cursor.execute(f"SELECT cod_sub_estd_sub FROM cad_topo_sub")
#subs_cod = cursor.fetchall()
#subs_cod = unwrap_from_fetch(subs_cod, 0)
#print(f'SUBESTAÇÂO EXAMINADA: - id: {subs_cod}')
#write_text_files(subs_cod)


#get_inter_from_matrix(true, once=True)

def start_while_loop():
    lop = loop()
    return lop


