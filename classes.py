import urllib3, urllib.request, json, pandas as pd, geopandas as gpd
from bs4 import BeautifulSoup

class Faixa:
    #recebe qual dos dataframes eu desejo escolher e quais as colunas eu quero para poder iniciar o dataframe
    def __init__(self,csv,col1,col2):
        #inicializa os dados do lais
        self.municipios = pd.read_csv ('https://covid.lais.ufrn.br/dados/boletim/evolucao_municipios.csv',sep=';')
        self.obitos = pd.read_csv ('https://covid.lais.ufrn.br/dados_abertos/faixa_etaria_pacientes_obitos.csv',sep=';')

        if csv == 'obitos':
            self.dataframe = pd.DataFrame(self.obitos,columns=[col1,col2])
        elif csv == 'municipios':
            self.dataframe = pd.DataFrame(self.municipios,columns=[col1,col2])
    
    #para imprimir o dataframe
    def get(self):
        return self.dataframe

    #agrupa os valores de uma coluna específica
    def agrupar(self,string):
        self.dataframe = self.dataframe.groupby([string]).sum().reset_index()

    #para fazer as médias móveis, recebe o nome da coluna e a quantidade de dias para fazer a média
    def rollingGet(self,string,nrolling):
        return self.dataframe.groupby(string).sum().rolling(nrolling).mean().reset_index()

    #para quando eu quero imprimir um dado baseado no maximo ou minimo de uma coluna específica
    def findMaxMin(self,idMaxColumn,columnToGet,which):
        if which == 'max':
            return self.dataframe.loc[self.dataframe[idMaxColumn].idxmax(),columnToGet]  
        elif which == 'min':
            return self.dataframe.loc[self.dataframe[idMaxColumn].idxmin(),columnToGet]
    
    #substituir um valor no dataframe
    def replace(self,position,column,valueToReplace):
        self.dataframe.loc[position,column] = valueToReplace

    #pesquisar numa coluna especifica um valor especifico
    def find(self,column,query):
        return self.dataframe.loc[self.dataframe[column].str.contains(query, case=False)]


#classe especifica para o dataframe da media por 100 mil, que herda a classe Faixa
class Media100mil(Faixa):
    #agrupa os valores de uma coluna específica e coloca essa coluna em ordem alfabetica
    def agruparSort(self,string):
        self.dataframe = self.dataframe.groupby([string]).sum().sort_values(by=string).reset_index()
    
    #agrupa os valores de uma coluna específica mas não ordena
    def sort(self,string):
        self.dataframe = self.dataframe.sort_values(by=string).reset_index(drop=True)
    
    #para criar uma nova coluna especifica para fazer a media de 100 mil
    def createColumnMedia(self,newColumn,column,webscrape,webscrapeColumn):
        self.dataframe[newColumn] = (self.dataframe[column] / webscrape[webscrapeColumn])*100000

    #cria uma nova coluna num dataframe especifico
    def createColumn(self,newColumn,webscrape,webscrapeColumn):
        self.dataframe[newColumn] = webscrape[webscrapeColumn]

#classe especifica para receber as geometrias do RN
class Geometry(Faixa):
    def __init__(self):
      #faltam 2 municipios
        with urllib.request.urlopen("https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-24-mun.json") as url:
            self.estados_rn = json.loads(url.read().decode())

        self.dataframe = gpd.GeoDataFrame.from_features(self.estados_rn["features"])
        self.dataframe = self.dataframe.set_geometry(self.dataframe.geometry)


#classe especifica para encontrar os dados de população do RN
class WebScraping(Media100mil):
    def __init__(self):
        #coloquei algumas funções em private  
        self.__conexao()

    #abre a conexao com a url da pagina
    def __conexao(self):
        self.url = "https://pt.wikipedia.org/wiki/Lista_de_munic%C3%ADpios_do_Rio_Grande_do_Norte_por_popula%C3%A7%C3%A3o"
        self.conexao = urllib3.PoolManager()
        self.retorno = self.conexao.request('GET',self.url)
        self.__transformaPagina()

    #cria um dataframe apenas com a tabela dos dados
    def __transformaPagina(self):
        self.pagina = BeautifulSoup(self.retorno.data,'html.parser')
        #pegando só a tabela
        self.pagina = self.pagina.findAll('table',class_="wikitable sortable")
        # Conversão da tabela em uma lista
        self.pagina = pd.read_html(str(self.pagina))
        #??
        self.dataframe = pd.concat(self.pagina)

    #remover valores iguais de uma coluna
    def dropColumnValue(self,column,query):
        self.dataframe = self.dataframe[self.dataframe[column].str.contains(query) == False]
    
    #resetar o index
    def resetIndex(self):
        self.dataframe.reset_index(drop=True, inplace=True)

    #remover uma coluna inteira
    def dropColumn(self,col1,col2):
        self.dataframe = self.dataframe.drop([col1,col2],axis=1)

    #remove espaços em branco e converte a população para int
    def rmSpaceInt(self,column):
        self.dataframe[column] = self.dataframe[column].str.replace("\s+","")
        self.dataframe[column] = self.dataframe[column].astype(int)
