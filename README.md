# COVID-19 no Rio Grande do Norte — Projeto de POO

Análise e visualização de dados da COVID-19 no estado do Rio Grande do Norte (Brasil), desenvolvida como projeto da disciplina de Programação Orientada a Objetos.

Demonstração online: [https://covid-19-ff6ee4e6fa78.herokuapp.com/](https://covid-19-ff6ee4e6fa78.herokuapp.com/)

## Requisitos

- Python 3.14+
- Consulte o arquivo `requirements.txt` para as dependências Python

## Execução local

```bash
pip3 install -r requirements.txt
streamlit run main.py
```

A aplicação será aberta em http://localhost:8501.

## Fontes de dados

- Dados de casos e óbitos por COVID-19: [LAIS/UFRN](https://covid.lais.ufrn.br)
- Dados populacionais: [Wikipedia](https://pt.wikipedia.org/wiki/Lista_de_munic%C3%ADpios_do_Rio_Grande_do_Norte_por_popula%C3%A7%C3%A3o)
- Limites geográficos (mapa): [geodata-br](https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-24-mun.json)
