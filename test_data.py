import pandas as pd

def parse_value(val):
    if pd.isna(val) or val == "":
        return 0.0
    val = str(val).replace('%', '').replace(',', '.')
    try:
        if ':' in val:
            parts = val.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        return float(val)
    except:
        return 0.0

def load_data(path):
    df = pd.read_csv(path, sep=';', skiprows=3)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(subset=['Indicador'])
    mes_col = df.columns[3]
    df['val_acumulado'] = df['Acumulado Safra'].apply(parse_value)
    df['val_mes'] = df[mes_col].apply(parse_value)
    df['val_min'] = df['Minimo'].apply(parse_value)
    return df, mes_col

try:
    df, mes = load_data('/home/ubuntu/upload/ResultadosdosIndicadores(11.csv')
    print(f"Sucesso! Mês detectado: {mes}")
    print(df[['Indicador', 'val_mes', 'val_acumulado']].head())
except Exception as e:
    print(f"Erro: {e}")
