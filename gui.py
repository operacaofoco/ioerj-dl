import pyforms
import conf
import ioerj_dl
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlText, ControlCheckBox, ControlButton, ControlDir, ControlLabel, ControlProgress
import datetime as dt

gl = conf.Globals
df = conf.Defaults

class GUI(BaseWidget):
  def __init__(self):
    super(GUI, self).__init__('IOERJ-DL')
    self._diretorio = ControlDir('Pasta destino')
    self._diretorio.value = str(df.workDir)
    n = 1
    for cad in gl.cadernosDisponiveis:
      self.__setattr__('_cadernoCheck%i' % n, ControlCheckBox(cad, value=True, changed_event=self.__marcarCaderno))
      n += 1
    self._cadernoCheck1.value = True
    self.operacao = 'periodo'
    self._modo = ControlCheckBox('Baixar apenas de hoje', changed_event=self.__trocarModo)

    def fData(x): 
      return x.strftime('%d/%m/%Y')
    
    inicioPadrao = fData(df.inicio)
    fimPadrao = fData(gl.hoje)
    self._inicio = ControlText(
        'Data início', helptext='Primeira data a ser baixada. Deve ser digitada no formato DD/MM/YYYY.',
        default=inicioPadrao)
    self._fim = ControlText(
        'Data fim', helptext='Última data a ser baixada. Deve ser digitada no formato DD/MM/YYYY.', default=fimPadrao)
    self._label = ControlLabel()
    self._progress = ControlProgress('Progresso total')
    self._button = ControlButton('Baixar')
    self._button.value = self.__download

  def __trocarModo(self):
    if self._modo.value == False:
      self.operacao = 'periodo'
      self._inicio.enabled = True
      self._fim.enabled = True
    elif self._modo.value == True:
      self.operacao = 'hoje'
      self._inicio.enabled = False
      self._fim.enabled = False

  def __marcarCaderno(self):
    cadernos = [key for key in self.__dict__.keys() if key.startswith('_cadernoCheck')]
    self._cadernosSelecionados = [self.__getattribute__(
        cad).label for cad in cadernos if self.__getattribute__(cad).value == True]

  def __download(self):
    self._button.enabled = False
    def parseDate(x): return dt.date(int(x.split('/')[2]), int(x.split('/')[1]), int(x.split('/')[0]))
    conf = {
        'tipoDownload': self.operacao,
        'diretorio': self._diretorio.value,
        'cadernos': self._cadernosSelecionados,
        'dataInicio': parseDate(self._inicio.value),
        'dataFim': parseDate(self._fim.value),
        'barraProgresso': self._progress,
        'labelGUI': self._label
    }

    ioerj_dl.executarDO(conf)

    self._progress.value = 0
    self._label.value = 'Concluído!'
    self._button.enabled = True


def main():
  pyforms.start_app(GUI)

if __name__ == "__main__":
  main()
