#%%
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import re
import conf
import datetime as dt
# módulo tqdm para barra de progresso não é obrigatório
try:
  from tqdm import tqdm
except ImportError:
  tqdm = None
import fitz 
import html 
from unicodedata import normalize

def para_txt(pdf_file, txt_file):
  doc = fitz.open(pdf_file)
  with open(txt_file, "w+")  as out:
      for page in doc: 
          txt = html.unescape(page.get_text('xhtml', 
                                flags = fitz.TEXT_DEHYPHENATE & fitz. TEXTFLAGS_SEARCH &
                                fitz.TEXT_PRESERVE_SPANS & fitz.TEXT_INHIBIT_SPACES & 
                                fitz.TEXTFLAGS_XHTML & ~fitz.TEXT_PRESERVE_IMAGES))
          txt = txt.replace(' - ',' @@@ ').replace('- ','').replace(' @@@ ', ' - ')
          txt = txt.replace('</div>','').replace('<div id="page0">','')
          txt = re.sub(r"\<b\>\s*\<\/b\>", r'', txt)
          txt = re.sub(r"\<p\>\s*\<\/p\>", r'', txt)
          txt = re.sub(r"\<h3\>\s*\<\/h3\>", r'', txt)
          txt = normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
          txt = txt.replace('<h3><b>A</b></h3>','')
          txt = re.sub(r"\<b\>\s*\<\/b\>", r'', txt)
          txt = re.sub(r"\<p\>\s*\<\/p\>", r'', txt)
          txt = re.sub(r"\<h3\>\s*\<\/h3\>", r'', txt)
          txt = re.sub(r"\<h1\>\s*\<\/h1\>", r'', txt)
          txt = re.sub(r"\s\s+", r' ', txt)
          out.write(txt)
  return txt


gl = conf.Globals()

def defSoup(url, parser='html.parser'):
  try:
    html = requests.get(url, headers=gl.headers)
    soup = BeautifulSoup(html.content, parser)
    return soup
  except:
    print('Erro ao conectar ao site da IOERJ')

def savePdf(urlPdf, conf):
  fullDir_pdf = Path(conf['diretorio_pdf'])
  Path.mkdir(fullDir_pdf, exist_ok=True, parents=True)
  fullDir_txt = Path(conf['diretorio_txt'])
  Path.mkdir(fullDir_txt, exist_ok=True, parents=True)
  nomeArq_pdf = f"DO_{conf['dataAtual'].year}_{str(conf['dataAtual'].month).zfill(2)}_{str(conf['dataAtual'].day).zfill(2)}_{conf['caderno']}.pdf"
  nomeArq_txt = f"DO_{conf['dataAtual'].year}_{str(conf['dataAtual'].month).zfill(2)}_{str(conf['dataAtual'].day).zfill(2)}_{conf['caderno']}.txt"
  nomeFull_pdf = Path(fullDir_pdf, nomeArq_pdf)
  nomeFull_txt = Path(fullDir_txt, nomeArq_txt)
  try:
    conf['labelGUI'].value = 'Baixando %s' % nomeArq_pdf
  except KeyError:
    print('Baixando %s' % nomeArq_pdf)
  res = requests.get(urlPdf, stream=True, headers=gl.headers)
  with open(nomeFull_pdf, 'wb') as f:
    if tqdm:
      tamanhoArq = int(res.headers.get('Content-Length', 0))
      for chunk in tqdm(res.iter_content(32*1024), total=tamanhoArq, unit='B', unit_scale=True):
        if chunk:
          f.write(chunk)
    else:
      f.write(res.content)
  if conf['tipoDownload'] == 'hoje':
    nomeFull = Path(conf['diretorio_pdf'], 'IOERJ_Hoje_%s.pdf' % conf['caderno'])
    res = requests.get(urlPdf, stream=True, headers=gl.headers)
    with open(nomeFull, 'wb') as f:
      f.write(res.content)
  para_txt(nomeFull_pdf, nomeFull_txt)

class CadernoDL():
  def __init__(self, element, data):
    self.element = element
    self.url = gl.urlDiaBase + element['href']
    self.caderno = element.text
    self.data = data
    self.nome = re.findall('Parte [IVB]', self.caderno)[0].replace(' ', '')
    if element.parent.find(id='EdicaoExtraDO'):
      self.extra = True
      self.caderno = self.caderno + ' Edição Extra'
      self.nome = self.nome + 'Extra'
    else:
      self.extra = False

  def numerarExtra(self, num):
    self.extraNum = num
    if int(num) > 1:
      self.nome = self.nome + str(num)
      self.caderno = self.caderno + ' ' + str(num)
    return self

  def download(self, conf):
    htmlDO = defSoup(self.url)
    scriptLink = htmlDO.find(id='scaleSelectContainer').find('script').text
    key = re.findall('"(.*?)"', scriptLink)[0]
    keyArr = key.split('-')
    keyMain = keyArr[1]
    keyArr[1] = keyMain[:3] + 'P' + keyMain[3:]
    key = '-'.join(keyArr)
    urlPdf = gl.urlDiaBase + 'mostra_edicao.php?k=' + key
    conf['caderno'] = self.nome
    savePdf(urlPdf, conf)

def downloadDia(url, conf):
  htmlDia = defSoup(url)
  htmlDia.find(id='xo-content').find_all('a')
  for tipoCaderno in conf['cadernos']:
    extra = 0
    for link in htmlDia.find(id='xo-content').find_all('a'):
      if link.text == tipoCaderno:
        caderno = CadernoDL(link, conf['dataAtual'])
        if caderno.extra:
          extra += 1
          caderno = caderno.numerarExtra(extra)
        caderno.download(conf)

def executarDO(conf: dict()):
  print('conf',conf)
  conf['dataAtual'] = gl.hoje
  if conf['tipoDownload'] == 'hoje':
    pagUltima = defSoup(gl.urlUltima)
    urlHoje = gl.urlDiaBase + pagUltima.find('a')['href']
    downloadDia(urlHoje, conf)
  elif conf['tipoDownload'] == 'periodo':
    print('Buscando dias de DO.')
    html = defSoup(gl.urlAnos, parser='html.parser').find(id='xo-page')
    class LinkDO():
      def __init__(self, url, dia, mes, ano):
        self.data = dt.date(int(ano), int(mes), int(dia))
        self.url = url
      def download(self, conf):
        conf['dataAtual'] = self.data
        downloadDia(self.url, conf)
    anosNum = []
    htmlAnos = html.find_all(class_='titulosecao')
    for ano in htmlAnos:
      anoNum = re.findall('([0-9]+)', ano.text)
      anosNum.append(anoNum[0])
      print(anosNum)
    linksDias = []
    htmlCalAno = html.find_all('table')
    print('4',len(htmlCalAno))
    for indexAno in range(len(anosNum)):
      ano = anosNum[indexAno]
      print('2',ano,indexAno)
      htmlMeses = htmlCalAno[indexAno].find_all(class_='calendario')
      print('3',len(htmlMeses))
      for mes in htmlMeses:
        mesNome = mes.find(class_='mes').text.replace('\n', '')
        mesNum = gl.meses[mesNome]
        print('1', mesNome, ano)
        diasUteis = mes.find_all(class_='dialink')
        for dia in diasUteis:
          diaNum = dia.text.replace('\n', '')
          print('ano',ano,'mes',mesNum,'dia',diaNum)
          urlDia = gl.urlDiaBase + dia.find('a')['href']
          link = LinkDO(urlDia, diaNum, mesNum, ano)
          if link.data >= conf['dataInicio'] and link.data <= conf['dataFim']:
            linksDias.append(link)
    print('%s dias selecionados para baixar.' % len(linksDias))
    try:
      d = 0
      conf['barraProgresso'].max = len(linksDias)
    except KeyError:
      pass
    for linkDia in linksDias:
      try:
        conf['barraProgresso'].value = d
        d += 1
      except KeyError:
        pass
      linkDia.download(conf)

# %%
