import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gdown
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Dashboard Baile 2025", page_icon="📊", layout="wide")

SENHA = "baile2025"

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 ACESSO RESTRITO")
        st.write("### Dashboard Baile 2025")
        senha = st.text_input("Senha:", type="password")
        if st.button("Acessar", use_container_width=True):
            if senha == SENHA:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")

else:
    if st.button("Sair", key="logout"):
        st.session_state.auth = False
        st.rerun()
    
    st.title("📊 DASHBOARD BAILE 2025")
    
    try:
        # Carregar dados
        url = "https://drive.google.com/uc?id=1bKyxuaOkGHKkVx2e5gdYISMi7zckmyjy"
        gdown.download(url, "baile.xlsx", quiet=True)
        df = pd.read_excel("baile.xlsx", sheet_name='Mesas', header=3)
        
        # Limpar
        df = df.dropna(how='all')
        df.columns = df.columns.str.strip()
        
        # Converter tipos
        df['ORD'] = pd.to_numeric(df['ORD'], errors='coerce')
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')
        df['VALOR'] = df['VALOR'].fillna(0)
        df['NOME'] = df['NOME'].fillna('-')
        
        # Remover linhas inválidas
        df = df[df['ORD'].notna()].copy()
        
        # Cálculos
        total_dist = int(df['ORD'].max())
        total_rec = df[df['VALOR'] > 0]['VALOR'].sum()
        previsao = total_dist * 600
        saldo = previsao - total_rec
        perc = (total_rec / previsao * 100) if previsao > 0 else 0
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📊 Distribuído", f"{total_dist}", "mesas")
        col2.metric("💰 Recebido", f"R$ {total_rec:,.0f}", f"{perc:.1f}%")
        col3.metric("📈 Previsão", f"R$ {previsao:,.0f}")
        col4.metric("💵 Saldo", f"R$ {saldo:,.0f}")
        
        st.divider()
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        # Pizza - Classificação
        with col1:
            st.subheader("📈 Distribuição")
            def classif(valor):
                if valor == 0: return 'PENDENTE'
                elif valor == 600: return 'MESA PAGA'
                elif valor == 300: return 'MEIA ENTRADA'
                elif valor >= 1000: return 'PATROCÍNIO'
                else: return 'OUTRO'
            
            df['CLASSIF'] = df['VALOR'].apply(classif)
            classif_count = df['CLASSIF'].value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=classif_count.index,
                values=classif_count.values,
                marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'])
            )])
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Barras - Top Responsáveis
        with col2:
            st.subheader("🏆 Top 10 Responsáveis")
            top = df.groupby('NOME')['VALOR'].sum().nlargest(10).sort_values(ascending=True)
            fig = px.bar(
                x=top.values,
                y=top.index,
                orientation='h',
                labels={'x': 'R$', 'y': 'Responsável'}
            )
            fig.update_layout(height=400, margin=dict(l=150))
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Gráfico de Linhas - Acumulado
        st.subheader("📈 Evolução Acumulada")
        df_acum = df.sort_values('ORD').copy()
        df_acum['ACUM'] = df_acum['VALOR'].cumsum()
        fig = px.line(
            df_acum,
            x='ORD',
            y='ACUM',
            markers=True,
            labels={'ORD': 'Mesa', 'ACUM': 'Acumulado (R$)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Tabela
        st.subheader("📋 Resumo por Responsável")
        resumo = df.groupby('NOME').agg({
            'ORD': 'count',
            'VALOR': 'sum'
        }).rename(columns={'ORD': 'Mesas', 'VALOR': 'Total'})
        resumo = resumo.sort_values('Mesas', ascending=False)
        
        # Formatar como moeda
        resumo['Total'] = resumo['Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        st.dataframe(resumo, use_container_width=True)
        
        st.success("✅ Dashboard carregado com sucesso!")
        
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
        st.info("💡 Verifique se o arquivo está no Google Drive")
