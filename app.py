from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Rota para registrar o serviço
@app.route('/registrar_servico', methods=['POST'])
def registrar_servico():
    try:
        # Recebe os dados da requisição
        data = request.get_json()

        # Armazena os dados no arquivo JSON (ou qualquer outro meio de persistência)
        with open("dados_servico.json", "a") as f:
            json.dump(data, f)
            f.write("\n")  # Adiciona uma nova linha para cada registro

        return jsonify({"message": "Dados registrados com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
