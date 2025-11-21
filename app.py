# ============================================================================
# DASHBOARD BAILE 2025 - VERSÃO STREAMLIT COMPLETA
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import gdown
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================
st.set_page_config(
    page_title="Dashboard Baile 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

SENHA_SECRETA = "baile2025"

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# ============================================================================
# TELA DE LOGIN
# ============================================================================
if not st.session_state.autenticado:
    st.markdown("""
        <style>
            .login-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px;
                border-radius: 15px;
                color: white;
                text-align: center;
                margin: 50px auto;
                max-width: 500px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .login-container h1 {
                font-size: 40px;
                margin: 0 0 10px 0;
            }
            .login-container p {
                font-size: 16px;
                margin: 10px 0;
                opacity: 0.9;
            }
        </style>
        <div class="login-container">
            <h1>🔐 ACESSO RESTRITO</h1>
            <p>Dashboard Baile 2025</p>
            <p>Apenas Usuários Autorizados</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 Digite a Senha")
        
        senha = st.text_input(
            "Senha:",
            type="password",
            key="login_senha",
            placeholder="Digite a senha para acessar"
        )
        
        if st.button("🔓 Acessar Dashboard", use_container_width=True, type="primary"):
            if senha == SENHA_SECRETA:
                st.session_state.autenticado = True
                st.success("✅ Acesso concedido!")
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
                st.info("💡 Se esqueceu a senha, contate o administrador")

else:
    # ====================================================================
    # DASHBOARD COMPLETO
    # ====================================================================
    
    # Botão de logout
    col1, col2, col3 = st.columns([10, 1, 1])
    with col3:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()
    
    st.sidebar.success("✅ Você tem acesso autorizado!")
    
    # ====================================================================
    # CARREGAR DADOS
    # ====================================================================
    @st.cache_data
    def carregar_dados():
        GOOGLE_DRIVE_FILE_ID = "1bKyxuaOkGHKkVx2e5gdYISMi7zckmyjy"
        
        try:
            url = f"https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}"
            gdown.download(url, "baile-2025.xlsx", quiet=True)
            
            df = pd.read_excel("baile-2025.xlsx", sheet_name='Mesas', header=3)
            return df
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {e}")
            return None

    # ====================================================================
    # PROCESSAR DADOS
    # ====================================================================
    def processar_dados(df):
        df = df.dropna(axis=1, how='all')
        df = df.dropna(how='all')
        df.columns = df.columns.str.strip()
        
        colunas_desejadas = ['ORD', 'NOME', 'Cliente', 'MESA', 'VALOR', 'DATA_REC']
        df_limpo = df[colunas_desejadas].copy()
        
        # Converter tipos
        df_limpo['ORD'] = pd.to_numeric(df_limpo['ORD'], errors='coerce')
        df_limpo['MESA'] = pd.to_numeric(df_limpo['MESA'], errors='coerce')
        df_limpo['VALOR'] = pd.to_numeric(df_limpo['VALOR'], errors='coerce')
        df_limpo['VALOR_CALCULADO'] = df_limpo['VALOR'].fillna(0)
        
        # Limpar NaN
        df_limpo['NOME'] = df_limpo['NOME'].fillna('-')
        df_limpo['Cliente'] = df_limpo['Cliente'].fillna('-')
        df_limpo['MESA'] = df_limpo['MESA'].fillna(-1)
        df_limpo['DATA_REC'] = df_limpo['DATA_REC'].fillna('-')
        
        # Remover linhas sem ORD
        df_limpo = df_limpo[df_limpo['ORD'].notna()].copy()
        
        # Classificar
        def classificar_mesa(row):
            valor = row['VALOR']
            if pd.isna(valor) or valor == 0:
                return 'PENDENTE'
            elif valor == 600:
                return 'MESA PAGA'
            elif valor == 300:
                return 'MEIA ENTRADA'
            elif valor >= 1000:
                return 'PATROCÍNIO'
            else:
                return 'OUTRO'
        
        df_limpo['CLASSIFICACAO'] = df_limpo.apply(classificar_mesa, axis=1)
        
        return df_limpo

    # ====================================================================
    # FORMATAÇÃO
    # ====================================================================
    def formatar_moeda(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # ====================================================================
    # MAIN - DASHBOARD
    # ====================================================================
    st.markdown("""
        <style>
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px;
                border-radius: 15px;
                color: white;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .header h1 {
                margin: 0;
                font-size: 36px;
            }
            .header p {
                margin: 10px 0 0 0;
                opacity: 0.9;
                font-size: 16px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Carregar dados
    df_limpo = carregar_dados()

    if df_limpo is not None and len(df_limpo) > 0:
        
        # Processar dados
        df_limpo = processar_dados(df_limpo)
        
        # Cabeçalho
        st.markdown("""
            <div class="header">
                <h1>📊 DASHBOARD BAILE 2025</h1>
                <p>✅ Acesso Autorizado | Relatório Interativo em Tempo Real</p>
            </div>
        """, unsafe_allow_html=True)
        
        # ====================================================================
        # CÁLCULOS
        # ====================================================================
        TOTAL_ATUALMENTE_ESPERADO = int(df_limpo['ORD'].max())
        ord_distribuidos = sorted(df_limpo['ORD'].astype(int).unique())
        mesas_esperadas = set(range(1, TOTAL_ATUALMENTE_ESPERADO + 1))
        ord_faltantes = sorted(mesas_esperadas - set(ord_distribuidos))
        
        # Contar por classificação
        mesas_pagas = len(df_limpo[df_limpo['CLASSIFICACAO'] == 'MESA PAGA'])
        total_mesas_pagas = df_limpo[df_limpo['CLASSIFICACAO'] == 'MESA PAGA']['VALOR_CALCULADO'].sum()
        
        meia_entrada = len(df_limpo[df_limpo['CLASSIFICACAO'] == 'MEIA ENTRADA'])
        total_meia_entrada = df_limpo[df_limpo['CLASSIFICACAO'] == 'MEIA ENTRADA']['VALOR_CALCULADO'].sum()
        
        patrocinios = len(df_limpo[df_limpo['CLASSIFICACAO'] == 'PATROCÍNIO'])
        valor_patrocinios_total = df_limpo[df_limpo['CLASSIFICACAO'] == 'PATROCÍNIO']['VALOR_CALCULADO'].sum()
        
        mesas_pendentes_com_dados = len(df_limpo[df_limpo['CLASSIFICACAO'] == 'PENDENTE'])
        total_mesas_pendentes = mesas_pendentes_com_dados + len(ord_faltantes)
        
        total_recebido = df_limpo[df_limpo['VALOR_CALCULADO'] > 0]['VALOR_CALCULADO'].sum()
        previsao = (TOTAL_ATUALMENTE_ESPERADO * 600) + (patrocinios * 400)
        saldo_a_receber = previsao - total_recebido
        percentual = (total_recebido / previsao * 100) if previsao > 0 else 0
        
        # ====================================================================
        # KPIs
        # ====================================================================
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Distribuído", f"{TOTAL_ATUALMENTE_ESPERADO}", "mesas")
        
        with col2:
            st.metric("💰 Total Recebido", formatar_moeda(total_recebido), f"{percentual:.1f}%")
        
        with col3:
            st.metric("📈 Previsão", formatar_moeda(previsao), "estimado")
        
        with col4:
            st.metric("💵 Saldo", formatar_moeda(saldo_a_receber), "a receber")
        
        st.divider()
        
        # ====================================================================
        # INFORMAÇÕES RESUMIDAS
        # ====================================================================
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.info(f"🎯 **Mesas Pagas:** {mesas_pagas}\n\nTotal: {formatar_moeda(total_mesas_pagas)}")
        
        with col2:
            st.info(f"🎫 **Meias Entradas:** {meia_entrada}\n\nTotal: {formatar_moeda(total_meia_entrada)}")
        
        with col3:
            st.info(f"⭐ **Patrocínios:** {patrocinios}\n\nTotal: {formatar_moeda(valor_patrocinios_total)}")
        
        with col4:
            st.warning(f"⏳ **Pendentes:** {total_mesas_pendentes}\n\n{len(ord_faltantes)} faltando dados")
        
        st.divider()
        
        # ====================================================================
        # GRÁFICOS
        # ====================================================================
        
        # Gráfico 1: Pizza
        st.subheader("📈 Distribuição por Classificação")
        classificacoes = df_limpo['CLASSIFICACAO'].value_counts()
        fig_pizza = go.Figure(data=[go.Pie(
            labels=classificacoes.index,
            values=classificacoes.values,
            marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'])
        )])
        fig_pizza.update_layout(
            height=500,
            showlegend=True,
            font=dict(size=12)
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
        
        # ====================================================================
        # RESUMO POR RESPONSÁVEL
        # ====================================================================
        resumo_responsavel = df_limpo.groupby('NOME').agg(
            Mesas_Distribuidas=('ORD', 'count'),
            Total_Recebido=('VALOR_CALCULADO', 'sum'),
            Mesas_Pagas=('CLASSIFICACAO', lambda x: (x == 'MESA PAGA').sum() + (x == 'PATROCÍNIO').sum() + (x == 'MEIA ENTRADA').sum())
        )
        
        # Obter patrocínios por responsável
        patrocinios_por_responsavel = df_limpo[df_limpo['CLASSIFICACAO'] == 'PATROCÍNIO'].groupby('NOME').size()
        resumo_responsavel['Patrocinios'] = patrocinios_por_responsavel
        resumo_responsavel['Patrocinios'] = resumo_responsavel['Patrocinios'].fillna(0).astype(int)
        
        # Calcular previsão e saldo
        resumo_responsavel['Previsao'] = (resumo_responsavel['Mesas_Distribuidas'] * 600) + (resumo_responsavel['Patrocinios'] * 400)
        resumo_responsavel['A_Receber'] = resumo_responsavel['Previsao'] - resumo_responsavel['Total_Recebido']
        
        # Ordenar por Mesas DECRESCENTE
        resumo_responsavel = resumo_responsavel.sort_values('Mesas_Distribuidas', ascending=False)
        
        # Gráfico 2: Barras - Top Responsáveis
        st.subheader("🏆 Top 10 Responsáveis por Mesas")
        top_responsaveis = resumo_responsavel.head(10).sort_values('Mesas_Distribuidas', ascending=True)
        fig_barras = go.Figure(data=[go.Bar(
            y=top_responsaveis.index,
            x=top_responsaveis['Mesas_Distribuidas'],
            orientation='h',
            marker=dict(color=top_responsaveis['Mesas_Distribuidas'], colorscale='Viridis'),
            text=top_responsaveis['Mesas_Distribuidas'],
            textposition='auto',
        )])
        fig_barras.update_layout(
            height=500,
            xaxis_title="Mesas Distribuídas",
            yaxis_title="Responsável",
            showlegend=False,
            margin=dict(l=200)
        )
        st.plotly_chart(fig_barras, use_container_width=True)
        
        # Gráfico 3: Linhas - Acumulado
        st.subheader("📈 Evolução Acumulada de Recebimentos")
        df_acumulado = df_limpo.sort_values('ORD').copy()
        df_acumulado['Acumulado'] = df_acumulado['VALOR_CALCULADO'].cumsum()
        fig_linhas = px.line(
            df_acumulado,
            x='ORD',
            y='Acumulado',
            markers=True,
            labels={'ORD': 'Número da Mesa', 'Acumulado': 'Valor Acumulado (R$)'}
        )
        fig_linhas.update_layout(
            height=500,
            hovermode='x unified',
            template='plotly_white'
        )
        st.plotly_chart(fig_linhas, use_container_width=True)
        
        # ====================================================================
        # TABELA COMPLETA
        # ====================================================================
        st.subheader("📋 Resumo Detalhado por Responsável (Top 15)")
        
        tabela_dados = resumo_responsavel.reset_index().head(15)[
            ['NOME', 'Mesas_Distribuidas', 'Total_Recebido', 'Previsao', 'A_Receber', 'Patrocinios']
        ].copy()
        
        tabela_dados.columns = ['Responsável', 'Mesas', 'Recebido', 'Previsão', 'A Receber', 'Patrocínios']
        
        # Formatar valores monetários
        for col in ['Recebido', 'Previsão', 'A Receber']:
            tabela_dados[col] = tabela_dados[col].apply(formatar_moeda)
        
        st.dataframe(tabela_dados, use_container_width=True, hide_index=True)
        
        # ====================================================================
        # GRÁFICO EXTRA: Barras por Valor Recebido
        # ====================================================================
        st.subheader("💰 Top 10 Responsáveis por Valor Recebido")
        top_valor = resumo_responsavel.head(10).sort_values('Total_Recebido', ascending=True)
        fig_valor = px.bar(
            x=top_valor['Total_Recebido'],
            y=top_valor.index,
            orientation='h',
            labels={'x': 'R$', 'y': 'Responsável'},
            title="Ranking de Valor Recebido"
        )
        fig_valor.update_layout(height=500, margin=dict(l=200))
        st.plotly_chart(fig_valor, use_container_width=True)
        
        st.divider()
        
        # Footer
        st.markdown(f"""
            <div style="text-align: center; color: #666; font-size: 12px;">
                ✨ Atualizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
                <br>
                Dashboard Baile 2025 © 2025
            </div>
        """, unsafe_allow_html=True)

    else:
        st.error("❌ Não foi possível carregar os dados. Verifique o arquivo no Google Drive.")
        st.info("💡 Dica: Verifique se o arquivo 'Baile-2025(python).xlsx' existe no Google Drive")
