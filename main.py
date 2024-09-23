import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta

# Criar as funções de carregamento de dados
@st.cache_data #decorator para armazenar em cache
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period='1d', start='2010-01-01', end='2024-09-22')
    print(cotacoes_acao)
    cotacoes_acao = cotacoes_acao['Close']
    return cotacoes_acao

@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv('IBOV.csv', sep=';')
    tickers = list(base_tickers['Código'])
    tickers = [item + '.SA' for item in tickers] #adiciona o .SA no final de cada ticker
    return tickers

acoes = carregar_tickers_acoes()

# Carregar os dados
dados = carregar_dados(acoes)

#Criação da interfaçe
st.write("""
# App Preço de Ações
O gráfico abaixo representa a evolução do preço de ações ao longo dos anos.
         """) # markdown

# sidebar com os filtros
st.sidebar.header('Filtros')

# Filtros
lista_acoes = st.sidebar.multiselect('Selecione as ações que deseja visualizar', dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: 'Close'}) 
        
# filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider('Selecione o intervalo de datas', data_inicial, data_final, (data_inicial, data_final),step=timedelta(days=30))

#filtrar as linhas de acordo com as datas selecionadas
dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

# criar gráfico
st.line_chart(dados)

# calculo de performace
texto_performace_ativos = ''

if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes) == 1:
    dados = dados.rename(columns={'Close':acao_unica}) 
    

carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)
    
for i, acao in enumerate(lista_acoes):
    preco_inicial = dados[acao].iloc[0]
    preco_final = dados[acao].iloc[-1]
    performace_ativo = (preco_final - preco_inicial) / preco_inicial
    performace_ativo = float(performace_ativo)
    
    carteira[i] = carteira[i] * (1 + performace_ativo)
    
    if performace_ativo > 0:
        texto_performace_ativos = texto_performace_ativos + f'{acao}: :green[{performace_ativo:.2f}%]  \n'
    elif performace_ativo < 0:
        texto_performace_ativos = texto_performace_ativos + f'{acao}: :red[{performace_ativo:.2f}%]  \n'
    else:
        texto_performace_ativos = texto_performace_ativos + f'{acao}: {performace_ativo:.2f}%  \n'
    

total_final_carteira = sum(carteira)
performace_carteira = total_final_carteira / total_inicial_carteira - 1


if performace_carteira > 0:
    texto_performace_carteira =  f'Performace da carteira com todos os ativos: :green[{performace_carteira:.2f}%]  \n'
elif performace_carteira < 0:
    texto_performace_carteira =  f'Performace da carteira com todos os ativos: :red[{performace_carteira:.2f}%]  \n'
else:
    texto_performace_carteira =  f'Performace da carteira com todos os ativos: {performace_carteira:.2f}%  \n'

st.write(f"""
### Performace do Ativos
A tabela abaixo mostra a performace dos ativos selecionados.

{texto_performace_ativos}

{texto_performace_carteira}
         """)