from classes import *

def func_faixae():
    faixa_etaria = Faixa('obitos','fx_etaria','total')
    faixa_etaria.get().columns = ['faixa etaria', 'obitos']
    faixa_etaria.agrupar('faixa etaria')
    return faixa_etaria

def c_diarios():
    #fazendo dataframe apenas com data e casos confirmados
    casos_diarios = Faixa('municipios','data','confirmados')
    casos_diarios.get().columns = ['data','casos confirmados']
    return casos_diarios

def o_diarios():
    #fazendo dataframe apenas com data e obitos
    obitos_diarios = Faixa('municipios','data','obitos')
    return obitos_diarios


def funcao_webscrape():
    populacao = WebScraping()

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
    return populacao


def func_mediaCem():
    #fazendo dataframe apenas com municipio e casos confirmados
    cemMil = Media100mil('municipios','mun_residencia','obitos')
    cemMil.get().columns = ['Municipio','obitos']


    #agrupar todos os valores, sort para deixar em ordem alfabetica baseada nos municípios e resetar o índice
    cemMil.agruparSort('Municipio')

    cemMil.replace(10,'Municipio','Campo Grande')
    cemMil.replace(55,'Municipio','Boa Saúde')

    cemMil.sort('Municipio')

    populacao = funcao_webscrape()

    #concatenar a coluna do dataframe obtido pelo webscraping
    cemMil.createColumn('Populacao',populacao.get(),'Populacao')
    cemMil.createColumnMedia('Mortes por 100 mil','obitos',populacao.get(),'Populacao')
    #cemMil.get().head()
    return cemMil