#%%
import requests
from bs4 import BeautifulSoup
import datetime as dt

#%%

url_calendario = 'http://www.ioerj.com.br/portal/modules/conteudoonline/do_seleciona_data.php'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'}
meses = {'Janeiro': 1, 'Fevereiro': 2, 'Março': 3,
           'Abril': 4, 'Maio': 5, 'Junho': 6,
           'Julho': 7, 'Agosto': 8, 'Setembro': 9,
           'Outubro': 10, 'Novembro': 11, 'Dezembro': 12}

calendario = requests.get(url_calendario, headers=headers)
html = BeautifulSoup(calendario.text, parser='html.parser').find(id='xo-page')

# %%

for secao in html.find_all('div', class_='titulosecao'):
    ano = secao.text[-4:]
    for secao_mes in html.find_all('table')[0].find_all('table',class_='calendario'):
        mes = secao_mes.find('b').text
        for secao_dia in secao_mes.find_all('a'):
            dia = int(secao_dia.text)
            print(ano, meses[mes], dia, secao_dia['href'])

# %%
