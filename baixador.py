#%%
import ioerj_dl
import datetime as dt

def fData(x): return dt.date(int(x.split('/')[2]), int(x.split('/')[1]), int(x.split('/')[0]))
   
conf = {
        'tipoDownload': 'periodo',
        'diretorio_pdf': 'pdfs/',
        'diretorio_txt': 'txts/',
        'cadernos': ['Parte I (Poder Executivo)'],
        'dataInicio': fData('21/09/2023'),
        'dataFim': fData('22/09/2023'),

    }

ioerj_dl.executarDO(conf)
# %%