#%%
import ioerj_dl
import datetime as dt

def fData(x): return dt.date(int(x.split('/')[2]), int(x.split('/')[1]), int(x.split('/')[0]))
   
conf = {'tipoDownload': 'periodo',
        'diretorio_pdf': 'pdfs/',
        'diretorio_txt': 'txts/',
        'cadernos': ['Parte I (Poder Executivo)'],
        'dataInicio': fData('01/06/2024'),
        'dataFim': fData('31/12/2024')    }

ioerj_dl.executarDO(conf)
# %%
