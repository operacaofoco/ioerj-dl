#%%
from bs4 import BeautifulSoup as BS
import conf
gl = conf.Globals
import requests
#%%
url_base = 'http://www.ioerj.com.br/portal/modules/conteudoonline/'
url_calendario = url_base+'mostra_edicao.php?session=VGxSQ1ExSnFZekJOUkVWMFRrUk5OVkpETURCTlZGbDVURlJuTkU1VldYUlNSR015VWtWVmVFNVVVVE5PYWxVdw==&calendario=true'


# %%
with open('diarios.html','w+') as f:
    r = requests.get(url_calendario)
    paginas = str(r.content, encoding='utf-8').split('<div class="titulosecao">Ano de ')[1:3]
    for pagina in paginas:
        ano = pagina.split('<')[0].strip()
        f.write(f'\n<p><b>{ano}</b>')
        f.write(f'\n<table><tr  valign="top">')
        pagina = BS(pagina, 'html.parser' )
        tabelas = pagina.findAll('table',{'class':'calendario'})
        for tabela in tabelas:
            mes = gl.meses[tabela.find('b').text]
            f.write(f'\n<td><p>{tabela.find("b").text}')
            for dia in tabela.findAll('a')[::-1]:
                f.write(f'\n<br><a href="{url_base+dia["href"]}"> {ano}/{str(mes).zfill(2)}/{str(dia.text).zfill(2)}</a>')
            f.write(f'\n</td>')
        f.write(f'\n</tr></table>')
#%%

gl.meses
# %%
