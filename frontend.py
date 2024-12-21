import requests
import streamlit as st

# URL do servidor Flask
API_URL = "http://127.0.0.1:5000/upload"


st.title("Correção de Textos Docx")

uploaded_file = st.file_uploader("Envie um arquivo .docx para correção", type=["docx"])

if uploaded_file is not None:
    with st.spinner("Enviando arquivo e aguardando correção..."):
        try:
            # Enviar arquivo para o servidor
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(API_URL, files=files)

            # Verificar status da resposta
            if response.status_code == 200:
                # Salvar o arquivo corrigido
                corrected_file = f"corrigido_{uploaded_file.name}"
                with open(corrected_file, "wb") as f:
                    f.write(response.content)
                st.success("Arquivo corrigido com sucesso!")
                st.download_button("Baixar arquivo corrigido", data=response.content, file_name=corrected_file)
            else:
                try:
                    # Tentar decodificar JSON para obter o erro
                    error_message = response.json().get("error", response.text)
                except ValueError:
                    # Caso a resposta não seja JSON
                    error_message = response.text
                st.error(f"Erro: {error_message}")
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao se conectar ao servidor: {str(e)}")
