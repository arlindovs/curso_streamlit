import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta
import plotly.graph_objs as go

# Função para carregar dados de ações
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period='1d', start='2010-01-01', end='2024-09-22')
    
    cotacoes_acao_close = cotacoes_acao['Close']
    cotacoes_acao_volume = cotacoes_acao.get('Volume')  # Usa get() para evitar KeyError
    
    return cotacoes_acao_close, cotacoes_acao_volume

# Função para carregar os tickers das ações
@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv('IBOV.csv', sep=';')
    tickers = list(base_tickers['Código'])
    tickers = [item + '.SA' for item in tickers]  # Adiciona .SA no final de cada ticker
    return tickers

# Função para criar o gráfico interativo com Plotly
def criar_grafico(dados, tipo_grafico='line', titulo='Evolução dos Preços'):
    fig = go.Figure()
    
    for coluna in dados.columns:
        if tipo_grafico == 'line':
            fig.add_trace(go.Scatter(x=dados.index, y=dados[coluna], mode='lines', name=coluna))
        elif tipo_grafico == 'area':
            fig.add_trace(go.Scatter(x=dados.index, y=dados[coluna], mode='lines', fill='tozeroy', name=coluna))
    
    fig.update_layout(
        title=titulo,
        xaxis_title='Data',
        yaxis_title='Preço',
        hovermode='x',
        template='plotly_dark'
    )
    
    return fig

# Carregar lista de ações
acoes = carregar_tickers_acoes()

# Carregar dados de preços e volumes
dados, dados_volume = carregar_dados(acoes)

# Criação da interface
st.write("""
# App Preço de Ações - Visualização Interativa
Aqui você pode visualizar e filtrar dados de ações de maneira interativa.
""")

# Sidebar com filtros
st.sidebar.header('Filtros')

# Filtros de seleção de ações
lista_acoes = st.sidebar.multiselect('Selecione as ações que deseja visualizar', dados.columns)

# Filtro para tipo de gráfico
tipo_grafico = st.sidebar.radio('Selecione o tipo de gráfico', ['line', 'area'], index=0)

# Filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider('Selecione o intervalo de datas', data_inicial, data_final, (data_inicial, data_final), step=timedelta(days=30))

# Verificar se há ações selecionadas
if lista_acoes:
    # Filtrar os dados de acordo com as datas selecionadas
    dados_filtrados = dados.loc[intervalo_data[0]:intervalo_data[1]]

    # Filtrar os dados das ações selecionadas
    dados_filtrados = dados_filtrados[lista_acoes]

    # Criar gráfico de preços interativo
    grafico_preco = criar_grafico(dados_filtrados, tipo_grafico=tipo_grafico, titulo='Evolução dos Preços das Ações')
    st.plotly_chart(grafico_preco)

    # Mostrar resumos estatísticos
    st.write("### Estatísticas Resumidas")
    for acao in lista_acoes:
        preco_inicial = dados[acao].loc[intervalo_data[0]]
        preco_final = dados[acao].loc[intervalo_data[1]]
        variacao = ((preco_final - preco_inicial) / preco_inicial) * 100
        preco_medio = dados[acao].mean()

        st.write(f"**{acao}**: Preço Inicial: R${preco_inicial:.2f}, Preço Final: R${preco_final:.2f}, Variação: {variacao:.2f}%, Preço Médio: R${preco_medio:.2f}")

    # Gráfico de volume (se existir)
    if dados_volume is not None:
        st.write("### Volume Negociado")
        dados_volume_filtrado = dados_volume[lista_acoes].loc[intervalo_data[0]:intervalo_data[1]]
        grafico_volume = criar_grafico(dados_volume_filtrado, tipo_grafico='area', titulo='Volume Negociado das Ações')
        st.plotly_chart(grafico_volume)
    else:
        st.write("Dados de volume não disponíveis para as ações selecionadas.")

    # Mostrar performance da carteira
    st.write("### Performance da Carteira")
    carteira_inicial = [1000] * len(lista_acoes)
    valor_carteira = 0
    for i, acao in enumerate(lista_acoes):
        preco_inicial = dados[acao].iloc[0]
        preco_final = dados[acao].iloc[-1]
        retorno_acao = (preco_final - preco_inicial) / preco_inicial
        carteira_inicial[i] = 1000 * (1 + retorno_acao)
        valor_carteira += carteira_inicial[i]
        st.write(f"{acao}: {retorno_acao * 100:.2f}% de retorno")

    total_inicial = 1000 * len(lista_acoes)
    st.write(f"Retorno total da carteira: {(valor_carteira - total_inicial) / total_inicial * 100:.2f}%")

else:
    st.warning("Por favor, selecione pelo menos uma ação para visualizar os gráficos e estatísticas.")
