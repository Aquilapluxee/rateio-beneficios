import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gerador de Rateio", layout="wide")

st.title("📊 Gerador de Rateio de Benefícios")
st.write("Carregue a planilha, aplique filtros e baixe o arquivo final.")


# --------------------------
# Upload do arquivo
# --------------------------
arquivo = st.file_uploader("Selecione a planilha Excel", type=["xlsx", "xls"])

if arquivo:
    df = pd.read_excel(arquivo)

    colunas_necessarias = ["FILIAL", "PRODUTO", "MOTIVO", "VALOR", "nota_fiscal", "data_compra"]

    for col in colunas_necessarias:
        if col not in df.columns:
            st.error(f"A coluna obrigatória '{col}' não existe na planilha.")
            st.stop()

    df["data_compra"] = pd.to_datetime(df["data_compra"], errors="coerce")

    st.success("Arquivo carregado com sucesso!")

    st.subheader("Prévia dos dados")
    st.dataframe(df.head(50))

    # --------------------------
    # Filtros
    # --------------------------
    st.subheader("Filtros")

    motivo = st.selectbox("Motivo", ["TODOS"] + sorted(df["MOTIVO"].dropna().unique().tolist()))
    produto = st.selectbox("Benefício", ["TODOS"] + sorted(df["PRODUTO"].dropna().unique().tolist()))
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

    if motivo != "TODOS":
        df_f = df_f[df_f["MOTIVO"] == motivo]

    if produto != "TODOS":
        df_f = df_f[df_f["PRODUTO"] == produto]

    if ano != "TODOS":
        df_f = df_f[df_f["data_compra"].dt.year == int(ano)]

    if mes != "TODOS":
        numero_mes = meses_lista.index(mes)
        df_f = df_f[df_f["data_compra"].dt.month == numero_mes]

    if df_f.empty:
        st.warning("Nenhum dado encontrado com os filtros aplicados.")
        st.stop()

    # --------------------------
    # Rateio
    # --------------------------
    rateio = (
        df_f.groupby(["FILIAL", "PRODUTO", "MOTIVO"])
            .agg({
                "VALOR": "sum",
                "nota_fiscal": lambda x: " / ".join(x.astype(str).unique())
            })
            .reset_index()
    )

    st.subheader("Rateio Gerado")
    st.dataframe(rateio)

    # --------------------------
    # Download do Excel
    # --------------------------
    excel_bytes = rateio.to_excel(index=False, engine="openpyxl")

    st.download_button(
        label="⬇ Baixar Rateio em Excel",
        data=excel_bytes,
        file_name="rateio.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
