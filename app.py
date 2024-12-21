import os
import logging
import shutil
from flask import Flask, request, send_file, jsonify
from docx import Document
import zipfile
from spellchecker import SpellChecker

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # Limite de 200MB

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def correct_spelling(text):
    spell = SpellChecker(language='pt')  # Correção em português
    words = text.split()
    corrected_text = []

    for word in words:
        corrected_word = spell.correction(word)
        corrected_text.append(corrected_word)

    return ' '.join(corrected_text)


def fix_lists(doc):
    for par in doc.paragraphs:
        if par.style.name == 'List Number' or par.style.name == 'List Bullet':
            # Corrigir as listas numeradas ou com marcadores (bullets)
            for run in par.runs:
                run.text = correct_spelling(run.text)
    return doc


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    if not file.filename.endswith('.docx'):
        return jsonify({"error": "Formato inválido. Envie um arquivo .docx"}), 400

    try:
        input_path = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(input_path)

        # Criar diretório temporário para manipular o conteúdo do arquivo
        temp_dir = os.path.join("temp", os.path.splitext(file.filename)[0])
        os.makedirs(temp_dir, exist_ok=True)

        # Extrair conteúdo do arquivo DOCX (ZIP)
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        doc = Document(input_path)

        # Corrigir ortografia no documento e listas
        doc = fix_lists(doc)

        output_path = os.path.join("outputs", f"copiado_{file.filename}")
        os.makedirs("outputs", exist_ok=True)

        # Salvar o documento corrigido
        doc.save(output_path)

        # Limpeza de arquivos temporários
        shutil.rmtree(temp_dir)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}", exc_info=True)
        return jsonify({"error": f"Ocorreu um erro inesperado: {str(e)}. Tente novamente mais tarde."}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
