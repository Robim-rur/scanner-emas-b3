import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Scanner EMAs B3 - Diário", layout="wide")

st.title("Scanner de Tendência por EMAs (9 / 29 / 69 / 169) – Gráfico Diário")

st.markdown("""
**Regras do scanner (long only):**

- Fechamento acima da EMA 69
- EMA 9 > EMA 29
- EMA 29 > EMA 69
- EMA 69 > EMA 169

Não exige cruzamento no candle atual.
Apenas estado de alinhamento.
""")

# -------------------------
# Lista de ativos
# -------------------------
ativos = [
    "ABEV3.SA","ALOS3.SA","AMER3.SA","ASAI3.SA","AZUL4.SA","B3SA3.SA",
    "BBAS3.SA","BBDC3.SA","BBDC4.SA","BBSE3.SA","BEEF3.SA","BPAC11.SA",
    "BRAP4.SA","BRFS3.SA","BRKM5.SA","CCRO3.SA","CIEL3.SA","CMIG4.SA",
    "COGN3.SA","CPFE3.SA","CPLE6.SA","CRFB3.SA","CSAN3.SA","CSNA3.SA",
    "CVCB3.SA","CYRE3.SA","DXCO3.SA","ECOR3.SA","EGIE3.SA","ELET3.SA",
    "ELET6.SA","EMBR3.SA","ENEV3.SA","ENGI11.SA","EQTL3.SA","EZTC3.SA",
    "FLRY3.SA","GGBR4.SA","GOAU4.SA","GOLL4.SA","HAPV3.SA","HYPE3.SA",
    "IGTI11.SA","IRBR3.SA","ITSA4.SA","ITUB4.SA","JBSS3.SA","KLBN11.SA",
    "LREN3.SA","MGLU3.SA","MRFG3.SA","MRVE3.SA","MULT3.SA","NTCO3.SA",
    "PCAR3.SA","PETR3.SA","PETR4.SA","PRIO3.SA","QUAL3.SA","RADL3.SA",
    "RAIL3.SA","RDOR3.SA","RENT3.SA","SANB11.SA","SBSP3.SA","SLCE3.SA",
    "SMTO3.SA","SOMA3.SA","SUZB3.SA","TAEE11.SA","TIMS3.SA","TOTS3.SA",
    "UGPA3.SA","USIM5.SA","VALE3.SA","VBBR3.SA","VIVT3.SA","WEGE3.SA",
    "YDUQ3.SA"
]

# -------------------------
# Funções
# -------------------------

@st.cache_data(show_spinner=False)
def baixar_dados(ticker):
    fim = datetime.today()
    inicio = fim - timedelta(days=600)

    df = yf.download(
        ticker,
        start=inicio.strftime("%Y-%m-%d"),
        end=fim.strftime("%Y-%m-%d"),
        progress=False
    )

    if df.empty:
        return df

    df["EMA9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["EMA29"] = df["Close"].ewm(span=29, adjust=False).mean()
    df["EMA69"] = df["Close"].ewm(span=69, adjust=False).mean()
    df["EMA169"] = df["Close"].ewm(span=169, adjust=False).mean()

    return df


def verifica_setup(df):

    if len(df) < 170:
        return False, None

    linha = df.iloc[-1]

    close = float(linha["Close"])
    ema9 = float(linha["EMA9"])
    ema29 = float(linha["EMA29"])
    ema69 = float(linha["EMA69"])
    ema169 = float(linha["EMA169"])

    condicoes = (
        close > ema69 and
        ema9 > ema29 and
        ema29 > ema69 and
        ema69 > ema169
    )

    return condicoes, linha


# -------------------------
# Processamento
# -------------------------

if st.button("Rodar scanner"):

    resultados = []

    barra = st.progress(0)

    total = len(ativos)

    for i, ativo in enumerate(ativos):

        try:
            df = baixar_dados(ativo)

            if df.empty:
                continue

            ok, linha = verifica_setup(df)

            if ok:

                resultados.append({
                    "Ativo": ativo.replace(".SA", ""),
                    "Fechamento": round(float(linha["Close"]), 2),
                    "EMA9": round(float(linha["EMA9"]), 2),
                    "EMA29": round(float(linha["EMA29"]), 2),
                    "EMA69": round(float(linha["EMA69"]), 2),
                    "EMA169": round(float(linha["EMA169"]), 2),
                    "Data": linha.name.strftime("%d/%m/%Y")
                })

        except Exception:
            pass

        barra.progress((i + 1) / total)

    barra.empty()

    if resultados:
        df_resultados = pd.DataFrame(resultados)
        st.success(f"{len(df_resultados)} ativos encontrados.")
        st.dataframe(df_resultados, use_container_width=True)
    else:
        st.warning("Nenhum ativo encontrado com as regras atuais.")
