import streamlit as st
from docx import Document
import re
import tempfile
import os

import sys

if sys.platform == 'win32':
    print("Running on Windows")
    from docx2pdf import convert

    def convert(docx_path, pdf_path):
        convert(caminho_docx, caminho_pdf)

elif sys.platform == 'darwin':
    print("Running on macOS")
    from docx2pdf import convert

    def convert(docx_path, pdf_path):
        convert(caminho_docx, caminho_pdf)

else:
    print("Running on Linux or other Unix-like system")

    import subprocess

    def convert(docx_path, pdf_path):
        # Use the directory of the pdf_path as output dir
        outdir = os.path.dirname(pdf_path)
        subprocess.call([
            'soffice',
            '--headless',
            '--convert-to',
            'pdf',
            '--outdir',
            outdir,
            docx_path
        ])
        # The output PDF will be named after the DOCX file
        base = os.path.splitext(os.path.basename(docx_path))[0]
        generated_pdf = os.path.join(outdir, f"{base}.pdf")
        # If the desired pdf_path is different, rename/move it
        if generated_pdf != pdf_path:
            os.rename(generated_pdf, pdf_path)
        return pdf_path


def extrair_campos(doc):
    texto_total = "\n".join([p.text for p in doc.paragraphs])
    return list(set(re.findall(r"\{\{(.*?)\}\}", texto_total)))

def preencher_campos(doc, dados):
    for p in doc.paragraphs:
        for chave, valor in dados.items():
            p.text = p.text.replace(f"{{{{{chave}}}}}", valor)
    return doc

st.title("📝 Preencher Template Word e Exportar com docx2pdf (Windows/macOS)")

uploaded_file = st.file_uploader("📤 Faça upload de um .docx com campos como {{nome}}, {{data}}", type="docx")

if uploaded_file:
    doc = Document(uploaded_file)
    campos = extrair_campos(doc)

    if campos:
        st.success(f"Campos encontrados: {', '.join(campos)}")

        dados_usuario = {}
        for campo in campos:
            dados_usuario[campo] = st.text_input(f"{campo}")

        if st.button("📄 Gerar PDF"):
            # Preenche campos e salva temporariamente
            doc_editado = preencher_campos(doc, dados_usuario)

            with tempfile.TemporaryDirectory() as tmpdir:
                caminho_docx = os.path.join(tmpdir, "filled.docx")
                caminho_pdf = os.path.join(tmpdir, "filled.pdf")

                doc_editado.save(caminho_docx)
                try:
                    convert(caminho_docx, caminho_pdf)
                    with open(caminho_pdf, "rb") as f:
                        st.download_button(
                            label="📥 Baixar PDF",
                            data=f,
                            file_name="documento_preenchido.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"Erro ao converter: {e}")
    else:
        st.warning("❗ Nenhum campo do tipo {{campo}} foi detectado no documento.")
