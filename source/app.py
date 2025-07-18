import streamlit as st
from docx import Document
import re
from jinja2 import Template
from weasyprint import HTML
import tempfile
import os

# Extrai os campos {{campo}} do .docx
def extrair_campos(doc):
    texto = "\n".join([p.text for p in doc.paragraphs])
    return list(set(re.findall(r"\{\{(.*?)\}\}", texto)))

# Converte o documento para HTML simples
def docx_para_html(doc, dados):
    html = ""
    for p in doc.paragraphs:
        linha = p.text
        for chave, valor in dados.items():
            linha = linha.replace(f"{{{{{chave}}}}}", valor)
        html += f"<p>{linha}</p>\n"
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 40px;
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """

st.set_page_config(page_title="Word para PDF - Web Friendly", layout="centered")
st.title("📄 Preencher Template Word e Gerar PDF (100% Web)")

uploaded_file = st.file_uploader("📤 Envie o template .docx com campos {{nome}}, {{data}}, etc.", type="docx")

if uploaded_file:
    doc = Document(uploaded_file)
    campos = extrair_campos(doc)

    if campos:
        st.success(f"Campos encontrados: {', '.join(campos)}")
        st.subheader("✏️ Preencha os dados:")

        dados = {}
        for campo in campos:
            dados[campo] = st.text_input(f"{campo}")

        if st.button("📄 Gerar PDF"):
            html_resultado = docx_para_html(doc, dados)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                HTML(string=html_resultado).write_pdf(tmp_pdf.name)
                with open(tmp_pdf.name, "rb") as f:
                    st.download_button(
                        label="📥 Baixar PDF",
                        data=f,
                        file_name="documento_preenchido.pdf",
                        mime="application/pdf"
                    )
                os.remove(tmp_pdf.name)
    else:
        st.warning("⚠️ Nenhum campo {{campo}} encontrado no documento.")
