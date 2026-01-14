import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# Configurações de Cores Raízen
RAIZEN_COLORS = {
    "verde_acinzentado": "#4d6d5d",
    "verde": "#60903e",
    "cinza_claro": "#b9bcc0",
    "cinza_escuro": "#666666",
    "branco": "#FFFFFF"
}

st.set_page_config(page_title="Dashboard de Indicadores - Raízen", layout="wide")

# Estilização Customizada
st.markdown(f"""
    <style>
    .main {{
        background-color: #f5f5f5;
    }}
    .stMetric {{
        background-color: {RAIZEN_COLORS['branco']};
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        border-left: 5px solid {RAIZEN_COLORS['verde']};
    }}
    h1, h2, h3 {{
        color: {RAIZEN_COLORS['verde_acinzentado']};
    }}
    .stButton>button {{
        background-color: {RAIZEN_COLORS['verde']};
        color: white;
    }}
    </style>
    """, unsafe_locally_executable=True, unsafe_allow_html=True)

def parse_value(val):
    if pd.isna(val) or val == "":
        return 0.0
    val = str(val).replace('%', '').replace(',', '.')
    try:
        # Tratar formato hh:mm
        if ':' in val:
            parts = val.split(':')
            return int(parts[0]) * 60 + int(parts[1]) # converter para minutos
        return float(val)
    except:
        return 0.0

def format_display_value(val, original_str):
    if '%' in str(original_str):
        return f"{val:.2f}%"
    if ':' in str(original_str):
        hours = int(val // 60)
        minutes = int(val % 60)
        return f"{hours:02d}:{minutes:02d}"
    return f"{val:.2f}"

def load_data(file):
    # Tentar ler o arquivo tratando o encoding se necessário
    try:
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8-sig')
        df = pd.read_csv(io.StringIO(content), sep=';', skiprows=3)
    except:
        df = pd.read_csv(file, sep=';', skiprows=3)
        
    # Limpar colunas vazias
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # Remover linhas vazias
    df = df.dropna(subset=['Indicador'])
    
    # Identificar a coluna do mês (quarta coluna)
    mes_col = df.columns[3]
    
    # Processar valores numéricos para cálculos
    df['val_acumulado'] = df['Acumulado Safra'].apply(parse_value)
    df['val_mes'] = df[mes_col].apply(parse_value)
    df['val_min'] = df['Minimo'].apply(parse_value)
    
    return df, mes_col

st.title("📊 Dashboard de Indicadores da Unidade")
st.sidebar.image("https://www.raizen.com.br/themes/custom/raizen_theme/logo.svg", width=150) # Fallback se não carregar
st.sidebar.header("Configurações")

uploaded_file = st.sidebar.file_uploader("Carregar arquivo CSV de indicadores", type="csv")

if uploaded_file is not None:
    df, mes_nome = load_data(uploaded_file)
    
    st.subheader(f"Resultados de {mes_nome}")
    
    # Métricas Principais em Colunas
    cols = st.columns(len(df))
    for i, row in df.iterrows():
        with cols[i % 4]:
            val_display = format_display_value(row['val_mes'], row[mes_nome])
            st.metric(label=row['Indicador'], value=val_display, help=row['Categoria'])

    st.divider()

    # Gráficos
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("### Comparativo: Mês vs Acumulado Safra")
        # Preparar dados para gráfico de barras
        plot_df = df.melt(id_vars=['Indicador'], value_vars=['val_mes', 'val_acumulado'], 
                          var_name='Tipo', value_name='Valor')
        plot_df['Tipo'] = plot_df['Tipo'].map({'val_mes': 'Mês Atual', 'val_acumulado': 'Acumulado Safra'})
        
        fig = px.bar(plot_df, x='Indicador', y='Valor', color='Tipo', barmode='group',
                     color_discrete_map={'Mês Atual': RAIZEN_COLORS['verde'], 'Acumulado Safra': RAIZEN_COLORS['verde_acinzentado']})
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        st.markdown("### Status em relação ao Mínimo")
        # Gráfico de radar ou barras horizontais para metas
        fig_meta = go.Figure()
        fig_meta.add_trace(go.Bar(
            y=df['Indicador'],
            x=df['val_mes'],
            name='Valor Atual',
            orientation='h',
            marker=dict(color=RAIZEN_COLORS['verde'])
        ))
        fig_meta.add_trace(go.Scatter(
            y=df['Indicador'],
            x=df['val_min'],
            name='Mínimo/Meta',
            mode='markers',
            marker=dict(color='red', size=10, symbol='diamond')
        ))
        fig_meta.update_layout(barmode='overlay', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_meta, use_container_width=True)

    # Tabela de Detalhes e Pontos de Atenção
    st.markdown("### 📝 Detalhamento e Pontos de Atenção")
    
    def highlight_attention(val):
        return f'background-color: {RAIZEN_COLORS["cinza_claro"]}' if "Investigar" in str(val) or "Atenção" in str(val) else ''

    display_df = df[['Indicador', 'Categoria', mes_nome, 'Acumulado Safra', 'Minimo', 'Pontos de Atenção']]
    st.table(display_df)

else:
    st.info("Aguardando upload do arquivo CSV para gerar o painel.")
    # Mostrar exemplo de como o arquivo deve ser
    st.warning("Certifique-se de que o arquivo segue o padrão do modelo enviado.")
