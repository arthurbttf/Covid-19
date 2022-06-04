import plotly.express as px, streamlit as st
from classes import *
from funcoes import *

st.set_page_config(layout="wide")

##inicio do streamlit
st.title('Projeto POO - Covid-19')
st.write('Neste projeto, foi feita a análise de dados de Covid-19 no Rio Grande do Norte e organizados em gráficos para melhor visualização.')

st.title('Óbitos por faixa etária')

faixa_etaria = func_faixae()
fig = px.bar(faixa_etaria.get(), x='faixa etaria', y='obitos',title='')

st.plotly_chart(fig,use_container_width=True)

obitos_maior = faixa_etaria.findMaxMin('obitos','obitos','max')
obitos_menor = faixa_etaria.findMaxMin('obitos','obitos','min')
fx_etaria_maior = faixa_etaria.findMaxMin('obitos','faixa etaria','max')
fx_etaria_menor = faixa_etaria.findMaxMin('obitos','faixa etaria','min')

st.write('‣ A faixa etária ',fx_etaria_maior,' possui a maior quantidade de óbitos, com ',str(obitos_maior),' óbitos totais.\n\n‣ A faixa etária ',fx_etaria_menor,' possui a menor quantidade de óbitos, com ',str(obitos_menor),' óbitos totais.')


#mapa do RN
st.title('Mapa de óbitos para cada 100 mil habitantes')
geometria = Geometry()

cemMil = func_mediaCem()
mun_maior = cemMil.findMaxMin('Mortes por 100 mil','Municipio','max')
mun_menor = cemMil.findMaxMin('Mortes por 100 mil','Municipio','min')
mun_maior_num = cemMil.findMaxMin('Mortes por 100 mil','Mortes por 100 mil','max')
mun_menor_num = cemMil.findMaxMin('Mortes por 100 mil','Mortes por 100 mil','min')

geometria.get().columns = ['geometry','id','Municipio','description']

geometria.replace(12,'Municipio','Campo Grande')
geometria.replace(58,'Municipio','Boa Saúde')
merged = geometria.get().set_index('Municipio').join(cemMil.get().set_index('Municipio'))

fig = px.choropleth(merged, geojson=merged.geometry, locations=merged.index, color="Mortes por 100 mil",
                    color_continuous_scale=[[0,'#ffb3b3'],[0.5,'#800000'],[1,'#190000']],
                    )


fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig,use_container_width=True)
st.write('‣',mun_maior,' possui a maior média de óbitos, com ', str(round(mun_maior_num,2)),' mortes a cada 100 mil habitantes.\n\n‣', mun_menor,' possui a menor média de óbitos, com ', str(round(mun_menor_num,2)),' mortes a cada 100 mil habitantes.')

#medias moveis
st.title('Médias móveis diárias')
st.write('A média móvel é uma evolução da média de um dado, em nosso caso, a dos obitos e casos de Covid-19 confirmados em um certo intervalo de tempo')

obitos_diarios = o_diarios()
casos_diarios = c_diarios()

option = st.selectbox(
     'Selecione em quantos dias você deseja ver as médias móveis',
     ('3 dias', '7 dias', '15 dias'))
col1, col2 = st.columns(2)
if option == '3 dias':
    fig1 = px.line(obitos_diarios.rollingGet('data',3), x='data', y='obitos',title='Obitos confirmados')
    col1.plotly_chart(fig1, use_container_width=True)
    fig2 = px.line(casos_diarios.rollingGet('data',3), x='data', y='casos confirmados',title='Casos confirmados')
    col2.plotly_chart(fig2, use_container_width=True)
elif option == '7 dias':
    fig1 = px.line(obitos_diarios.rollingGet('data',7), x='data', y='obitos',title='Obitos confirmados')
    col1.plotly_chart(fig1, use_container_width=True)
    fig2 = px.line(casos_diarios.rollingGet('data',7), x='data', y='casos confirmados',title='Casos confirmados')
    col2.plotly_chart(fig2, use_container_width=True)
elif option == '15 dias':
    fig1 = px.line(obitos_diarios.rollingGet('data',15), x='data', y='obitos',title='Obitos confirmados')
    col1.plotly_chart(fig1, use_container_width=True)
    fig2 = px.line(casos_diarios.rollingGet('data',15), x='data', y='casos confirmados',title='Casos confirmados')
    col2.plotly_chart(fig2, use_container_width=True)

st.write('Dados de óbitos obtidos de [lais](https://covid.lais.ufrn.br), dados de população obtidos da [wikipedia](https://pt.wikipedia.org/wiki/Lista_de_munic%C3%ADpios_do_Rio_Grande_do_Norte_por_popula%C3%A7%C3%A3o) e dados do mapa obtido do [github](https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-24-mun.json)')
