# -*- coding: utf-8 -*-
"""Projeto

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1i-sJsZNm0fRbENZ4IR-PVBSgQZaQJGP6

# Bibliotecas do Projeto
"""

!pip install geopandas beautifulsoup4 #urllib3[secure]
import urllib3, urllib.request, json, pandas as pd, geopandas as gpd, plotly.express as px
from bs4 import BeautifulSoup

import geopandas as gpd
import requests
import zipfile
import io

"""tapoha qq isso

"""

url = 'https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2021/UFs/RN/RN_Municipios_2021.zip'
local_path = 'tmp/'
print('Downloading shapefile...')
r = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(r.content))
print("Done")
z.extractall(path=local_path) # extract to folder
filenames = [y for y in sorted(z.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending)] 
print(filenames)
dbf, prj, shp, shx = [filename for filename in filenames]
usa = gpd.read_file(local_path + shp)
print("Shape of the dataframe: {}".format(usa.shape))
print("Projection of dataframe: {}".format(usa.crs))
usa.tail() #last 5 records in dataframe
usa.loc[91,'NM_MUN'] = "Olho-d'Água do Borges"
usa.loc[58,'NM_MUN'] = "Boa Saúde"
usa.loc[usa['NM_MUN'].str.contains('Cicco', case=False)]

"""### classes"""

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


#VERRRRRRRRR https://medium.com/@loldja/reading-shapefile-zips-from-a-url-in-python-3-93ea8d727856
#VERRR https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html?=&t=acesso-ao-produto
#boa saude e serra caiada
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

"""

### Criando o dataframe para as mortes por faixa etária"""

faixa_etaria = Faixa('obitos','fx_etaria','total');
faixa_etaria.get().columns = ['faixa etaria', 'obitos']
faixa_etaria.agrupar('faixa etaria')
faixa_etaria.get().head()

"""### Criando o dataframe para as médias móveis de mortes e casos diário"""

#fazendo dataframe apenas com data e casos confirmados
casos_diarios = Faixa('municipios','data','confirmados')
casos_diarios.get().columns = ['data','casos confirmados']

#display existe, caso contrário n imprime os dois
display(casos_diarios.get().head())

#fazendo dataframe apenas com data e obitos
obitos_diarios = Faixa('municipios','data','obitos')
obitos_diarios.get().head()

"""### Web scraping para obter população por município"""

populacao = WebScraping();

#adicionando nomes das colunas, porque o pandas não os via como string, ainda aproveitando pra remover o que n preciso
populacao.get().columns = ['Posicao', 'Municipio', 'Populacao', 'lixo']

#removendo todas as linhas que contém "habitantes"
populacao.dropColumnValue('Posicao','habitantes')

#removendo as colunas que não preciso
populacao.dropColumn('Posicao','lixo')

#Colocando valores em ordem alfabetica
populacao.sort('Municipio')

#tirando espaço em branco dos numeros
populacao.rmSpaceInt('Populacao')

#renomeando algumas coisas escritas erradas.
populacao.replace(9,'Municipio', 'Arês')
populacao.replace(10,'Municipio','Açu')
populacao.replace(18,'Municipio', 'Brejinho')
populacao.replace(96,'Municipio', 'Passa e Fica')
populacao.replace(133,'Municipio', 'São Bento do Trairí')

populacao.get().head()

"""### Criando o dataframe para médias de mortes por 100 mil habitantes no RN"""

#fazendo dataframe apenas com municipio e casos confirmados
cemMil = Media100mil('municipios','mun_residencia','obitos')
cemMil.get().columns = ['Municipio','obitos']


#agrupar todos os valores, sort para deixar em ordem alfabetica baseada nos municípios e resetar o índice
cemMil.agruparSort('Municipio')

cemMil.replace(10,'Municipio','Campo Grande')
cemMil.replace(55,'Municipio','Boa Saúde')

cemMil.sort('Municipio')

#concatenar a coluna do dataframe obtido pelo webscraping
cemMil.createColumn('Populacao',populacao.get(),'Populacao')
cemMil.createColumnMedia('Mortes por 100 mil','obitos',populacao.get(),'Populacao')
print(cemMil.find('Municipio','caiada'))
#cemMil.get().head()

"""## Média móvel de novos casos diários"""

fig = px.line(casos_diarios.rollingGet('data',3), x='data', y='casos confirmados',title='Média móvel 3 dias')
fig.show()

fig = px.line(casos_diarios.rollingGet('data',7), x='data', y='casos confirmados',title='Média móvel 7 dias')
fig.show()

fig = px.line(casos_diarios.rollingGet('data',15), x='data', y='casos confirmados',title='Média móvel 15 dias')
fig.show()

"""# Média movel de óbitos diários"""

fig = px.line(obitos_diarios.rollingGet('data',3), x='data', y='obitos',title='Média móvel 3 dias')
fig.show()
    
fig = px.line(obitos_diarios.rollingGet('data',7), x='data', y='obitos',title='Média móvel 7 dias')
fig.show()
    
fig = px.line(obitos_diarios.rollingGet('data',15), x='data', y='obitos',title='Média móvel 15 dias')
fig.show()

"""# Mortes por faixa etária"""

fig = px.bar(faixa_etaria.get(), x='faixa etaria', y='obitos',title='Mortes por faixa etária')

fig.show()

obitos_maior = faixa_etaria.findMaxMin('obitos','obitos','max')
obitos_menor = faixa_etaria.findMaxMin('obitos','obitos','min')
fx_etaria_maior = faixa_etaria.findMaxMin('obitos','faixa etaria','max')
fx_etaria_menor = faixa_etaria.findMaxMin('obitos','faixa etaria','min')

print("A faixa etária {} possui a maior quantidade de óbitos, com {} óbitos totais.\nA faixa etária {} possui a menor quantidade de óbitos, com {} óbitos totais.".format(fx_etaria_maior, obitos_maior, fx_etaria_menor, obitos_menor))

"""# Mortes por 100k"""

geometria = Geometry()

geometria.get().columns = ['geometry','id','Municipio','description']

geometria.replace(12,'Municipio','Campo Grande')
geometria.replace(58,'Municipio','Boa Saúde')
print(geometria.find('description','Cicco'))
merged = usa.set_index('NM_MUN').join(cemMil.get().set_index('Municipio'))


fig = px.choropleth(merged, geojson=merged.geometry, locations=merged.index, color="Mortes por 100 mil",
                    color_continuous_scale=[[0,'#ffb3b3'],[0.5,'#800000'],[1,'#190000']],
                    )
#https://www.youtube.com/watch?v=aJmaw3QKMvk ver depois
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

"""# Comentários de lembrete"""

#print(obitos_populacao_municipio.loc[obitos_populacao_municipio['Municipio'].str.contains("Goianinha", case=False)])
#maior_mortes = soma_obitos_municipio.loc[soma_obitos_municipio['obitos'].idxmax(), 'obitos']
#menor_mortes = soma_obitos_municipio.loc[soma_obitos_municipio['obitos'].idxmin(), 'obitos']
#municipio_maior_mortes = soma_obitos_municipio.loc[soma_obitos_municipio['obitos'].idxmax(), 'mun_residencia']
#municipio_menor_mortes = soma_obitos_municipio.loc[soma_obitos_municipio['obitos'].idxmin(), 'mun_residencia']
#print(soma_obitos_municipio.sort_values(by='mun_residencia'))

#achar um municipio especifico
#print(soma_obitos_municipio.loc[soma_obitos_municipio['mun_residencia'].str.contains("Severiano Melo", case=False)])
#display(dias_obitos.groupby('data').sum())
#print("O estado {} teve {} mortes por 100 mil habitantes".format(municipio_maior_mortes,(maior_mortes/896708)*100000))
