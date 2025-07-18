import streamlit as st
from docx import Document
import re
import streamlit.components.v1 as components

def extrair_campos(doc):
    texto = "\n".join([p.text for p in doc.paragraphs])
    return list(set(re.findall(r"\{\{(.*?)\}\}", texto)))

def docx_para_texto(doc, dados):
    texto = ""
    for p in doc.paragraphs:
        linha = p.text
        for chave, valor in dados.items():
            linha = linha.replace(f"{{{{{chave}}}}}", valor)
        texto += linha + "\n"
    return texto.strip()

st.title("📝 Gerar PDF simples no Navegador")

uploaded_file = st.file_uploader("Envie o .docx com campos {{campo}}", type="docx")

if uploaded_file:
    doc = Document(uploaded_file)
    campos = extrair_campos(doc)

    if campos:
        st.success(f"Campos: {', '.join(campos)}")
        dados = {}
        for campo in campos:
            dados[campo] = st.text_input(campo)

        gerar_pdf = st.button("Gerar PDF")
        if gerar_pdf:
            texto_preenchido = docx_para_texto(doc, dados)
            texto_js = texto_preenchido.replace("\n", "\\n").replace("'", "\\'").replace('"', '\\"')

            components.html(f"""
                <html>
                <head>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
                </head>
                <body>
                    <button id="download" style="font-size:16px; padding:8px 16px;">📥 Baixar PDF</button>

                    <script>
                    const {{ jsPDF }} = window.jspdf;

                    document.getElementById("download").onclick = () => {{
                        var doc = new jsPDF();
                        var texto = "{texto_js}";
                        var linhas = texto.split("\\n");
                        var y = 10;
                        for(var i=0; i<linhas.length; i++) {{
                            doc.text(linhas[i], 10, y);
                            y += 10;
                        }}
                        doc.save("documento_preenchido.pdf");
                    }};
                    </script>
                </body>
                </html>
            """, height=100)
    else:
        st.warning("Nenhum campo {{campo}} encontrado no documento.")
