#%%
import re
#%%
with open('txts/DO_2023_10_31_ParteI.txt') as f:
    do = f.readlines()
# %%
def limpa_tag(x):
    return re.sub(re.compile('<.*?>'),'',x).replace('\n', '')

def find(string, lista):
    dados = []
    for i, x in enumerate(lista):
        if x.startswith(string):
            dados.append(tuple((i , limpa_tag(x).strip())))
    return dados
# %%
find('<p><b>ATOS DO PODER', do)
# %%
find('<p><b>Secretaria de Estado', do)
# %%
find('<p><b>Id', do)
# %%
do[25:40]
# %%
find('<p><b>TORNAR SEM EFEITO', do)
# %%
find('<p><b>EXONERAR', do)
# %%
find('<p><b>NOMEAR', do)
# %%
find('<p><b>DEMITIR', do)
# %%
find('<p><b>ATOS DO', do)
# %%
limpa_tag(' '.join(do[25:40]))
# %%
group1 = find('<p><b>ATOS DO PODER', do)
for i in range(len(group1)-1):
    a,b = group1[i][0], group1[i+1][0]
    print(a,b)
    find('<p><b>Secretaria de Estado', do[a:b])
print(group1[i+1][0], len(do))
# %%
a
# %%
do[-20:]
# %%
import os
# %%
files = os.listdir('txts/')[:10]
for file in files:
    with open(f'txts/{file}') as f:
        do = f.readlines()
        poderes = find('<p><b>ATOS DO PODER', do)
        poderes = [[a," ".join(b.split(' ')[:4])] for a,b in poderes]
        poderes = list(zip(*poderes))
        a = 0
        atos = ['ATOS DO GOVERNADOR'] + list(poderes[1])
        cadernos = []
        for i in range(len(poderes[0])):
            b = poderes[0][i]
            cadernos.append([a, b, atos[i]])
            a= poderes[0][i]
        b = len(do)
        cadernos.append([a, b, atos[i+1]])
        print(cadernos)
        for caderno in cadernos:
            print(caderno)
# %%

d = {'FOCO':'FOCO',
     'SEFAZ':'Mercadorias e Barreiras Fiscais'}
for orgao in d.items():
    with open(f'RH_{orgao[0]}.txt', 'w+') as rh:
        for tipo in ['NOMEAR','EXONERAR','DEMITIR','TORNAR SEM EFEITO']:
            files = os.listdir('txts/')
            for file in files:
                with open(f'txts/{file}') as f:
                    do = f.readlines()
                    rh.write('\n'.join([f'{file};linha {x[0]};{x[1]}' for x in find(f'<p><b>{tipo}', do) if orgao[1] in x[1]]))
# %%