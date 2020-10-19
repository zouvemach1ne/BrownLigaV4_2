import os
import pandas as pd

def identify_unique(lista):
    df = pd.DataFrame(lista)
    df.drop_duplicates(inplace=True)
    mylist = df.values.tolist()
    return mylist


alims_list = os.listdir("complete_paths")
alims = []
for alim in alims_list:
    if "clear" not in alim:
        alims.append(alim)

def get_rls_privados():
    rls_priv = []
    with open(os.path.join(os.getcwd(),"rls_particulares.txt" ), "r") as file:
        lines = file.readlines()
        for line in lines:
            if len(line.strip('\n')) > 9:
                rls_priv.append(line.strip('\n'))
    
    return rls_priv

rls_priv = get_rls_privados()

for alim in alims:
    if ".txt" in alim:
        with open(os.path.join(os.getcwd(),"complete_paths/"+alim ), "r") as file:
            paths = []
            lines = file.readlines()
            for line in lines:
                #print(line)
                line = line.strip('\n').replace("'",'').replace(' ','').strip('[]').split(',')
                cur_line = []
                for i, elem in enumerate(line):
                    if ("79" in elem[:2] and len(elem)>9) or "52" in elem[:2] or ("RE" in elem[:2]) or  "89" in elem[:2]:# :
                        if elem not in rls_priv:
                            cur_line.append(elem)

                paths.append(cur_line)
            paths = identify_unique(paths)
        print(paths)

        with open(os.path.join(os.getcwd(),"complete_paths/clear_"+alim ), "w") as file:
            for i in paths:
                file.write(str(i)+'\n')
        #os.startfile('clear_complete_paths.txt')

