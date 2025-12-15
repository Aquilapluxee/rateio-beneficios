import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Gerador de Rateio", layout="wide")

st.title("📊 Gerador de Rateio de Benefícios")
st.write("Carregue a planilha, aplique filtros e baixe o arquivo final.")

# --------------------------
# Upload do arquivo
# --------------------------
arquivo = st.file_uploader("Selecione a planilha Excel", type=["xlsx", "xls"])

if arquivo:
    df = pd.read_excel(arquivo)

    colunas_necessarias = [
        "FILIAL",
        "PRODUTO",
        "MOTIVO",
        "VALOR",
        "nota_fiscal",
        "data_compra",
        "CNPJ"
    ]

    for col in colunas_necessarias:
        if col not in df.columns:
            st.error(f"A coluna obrigatória '{col}' não existe na planilha.")
            st.stop()

    # Tratamentos iniciais
    df["data_compra"] = pd.to_datetime(df["data_compra"], errors="coerce")
    df["CNPJ"] = df["CNPJ"].astype(str).str.strip()

    # Identificação da empresa
    df["EMPRESA"] = df["CNPJ"].apply(
        lambda x: "CARGO" if x.startswith("00")
        else "SWISSPORT" if x.startswith("01")
        else "NÃO IDENTIFICADA"
    )

    st.success("Arquivo carregado com sucesso!")

    st.subheader("Prévia dos dados")
    st.dataframe(df.head(50), use_container_width=True)

    # --------------------------
    # Filtros
    # --------------------------
    st.subheader("Filtros")

    empresa = st.selectbox(
        "Empresa",
        ["TODOS"] + sorted(df["EMPRESA"].unique().tolist())
    )

    motivo = st.selectbox(
        "Motivo",
        ["TODOS"] + sorted(df["MOTIVO"].dropna().unique().tolist())
    )

    produto = st.selectbox(
        "Benefício",
        ["TODOS"] + sorted(df["PRODUTO"].dropna().unique().tolist())
    )

    anos = ["TODOS"] + sorted(df["data_compra"].dt.year.dropna().unique().tolist())
    ano = st.selectbox("Ano", anos)

    meses_lista = [
        "TODOS", "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
        "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
    ]
    mes = st.selectbox("Mês", meses_lista)

    # --------------------------
    # Aplicar filtros
    # --------------------------
    df_f = df.copy()

    if empresa != "TODOS":
        df_f = df_f[df_f["EMPRESA"] == empresa]

    if motivo != "TODOS":
        df_f = df_f[df_f["MOTIVO"] == motivo]

    if produto != "TODOS":
        df_f = df_f[df_f["PRODUTO"] == produto]

    if ano != "TODOS":
        df_f = df_f[df_f["data_compra"].dt.year == int(ano)]

    if mes != "TODOS":
        df_f = df_f[df_f["data_compra"].dt.month == meses_lista.index(mes)]

    if df_f.empty:
        st.warning("Nenhum dado encontrado com os filtros aplicados.")
        st.stop()

    # --------------------------
    # Rateio
    # --------------------------
    rateio = (
        df_f.groupby(["FILIAL", "PRODUTO", "MOTIVO", "CNPJ", "EMPRESA"])
            .agg({
                "VALOR": "sum",
                "nota_fiscal": lambda x: " / ".join(x.astype(str).unique())
            })
            .reset_index()
    )

    st.subheader("Rateio Gerado")
    st.dataframe(rateio, use_container_width=True)

    # --------------------------
    # Download do Excel (compatível Streamlit Cloud)
    # --------------------------
    buffer = BytesIO()
    rateio.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="⬇ Baixar Rateio em Excel",
        data=buffer,
        file_name="rateio.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
