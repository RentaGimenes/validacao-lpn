from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validação LPN</title>
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            width: 100%;
            max-width: 1600px;
            gap: 30px;
        }
        .section {
            display: flex;
            flex-direction: column;
            align-items: center;
            background: #1e1e1e;
            padding: 20px;
            border-radius: 8px;
            width: 45%;
            min-width: 500px;
        }
        .question {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }
        .options {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 20px;
            align-items: center;
        }
        .options label {
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
        }
        .options input[type="radio"] {
            transform: scale(1.4);
            accent-color: #ff4d4d;
            cursor: pointer;
        }
        .image-container {
            width: 100%;
            display: flex;
            justify-content: center;
        }
        .image-container img {
            width: 100%;
            max-width: 650px;
            height: auto;
            border-radius: 4px;
            border: 1px solid #333;
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- 1. Data Fabricação -->
        <div class="section">
            <div class="question">📌 A Data de Fabricação está correta?</div>
            <div class="options">
                <label><input type="radio" name="q1" checked> Selecione...</label>
                <label><input type="radio" name="q1"> Sim</label>
                <label><input type="radio" name="q1"> Não</label>
            </div>
            <div class="image-container">
                <img src="{{ img_dataf01 }}" alt="Data Fabricação">
            </div>
        </div>

        <!-- 2. Data Validade -->
        <div class="section">
            <div class="question">📌 A Data de Validade está correta?</div>
            <div class="options">
                <label><input type="radio" name="q2" checked> Selecione...</label>
                <label><input type="radio" name="q2"> Sim</label>
                <label><input type="radio" name="q2"> Não</label>
            </div>
            <div class="image-container">
                <img src="{{ img_datav02 }}" alt="Data Validade">
            </div>
        </div>

        <!-- 3. DUN -->
        <div class="section">
            <div class="question">📌 O DUN está correto?</div>
            <div class="options">
                <label><input type="radio" name="q3" checked> Selecione...</label>
                <label><input type="radio" name="q3"> Sim</label>
                <label><input type="radio" name="q3"> Não</label>
            </div>
            <div class="image-container">
                <img src="{{ img_dun03 }}" alt="DUN">
            </div>
        </div>

        <!-- 4. Material -->
        <div class="section">
            <div class="question">📌 O Material está correto?</div>
            <div class="options">
                <label><input type="radio" name="q4" checked> Selecione...</label>
                <label><input type="radio" name="q4"> Sim</label>
                <label><input type="radio" name="q4"> Não</label>
            </div>
            <div class="image-container">
                <img src="{{ img_material04 }}" alt="Material">
            </div>
        </div>

        <!-- 5. Guia -->
        <div class="section">
            <div class="question">📌 A Guia está correta?</div>
            <div class="options">
                <label><input type="radio" name="q5" checked> Selecione...</label>
                <label><input type="radio" name="q5"> Sim</label>
                <label><input type="radio" name="q5"> Não</label>
            </div>
            <div class="image-container">
                <img src="{{ img_guia05 }}" alt="Guia">
            </div>
        </div>

        <!-- 6. Lote -->
        <div class="section">
            <div class="question">📌 O Lote está correto?</div>
            <div class="options">
                <label><input type="radio" name="q6" checked> Selecione...</label>
                <label><input type="radio" name="q6"> Sim</label>
                <label><input type="radio" name="q6"> Não</label>
            </div>
            <div class="image-container">
                <img src="{{ img_lote06 }}" alt="Lote">
            </div>
        </div>

        <!-- 7. Descrição -->
        <div class="section">
            <div class="question">📌 A Descrição está correta?</div>
            <div class="options">
                <label><input type="radio" name="q7" checked> Selecione...</label>
                <label><input type="radio" name="q7"> Sim</label>
                <label><input type="radio" name="q7"> Não</label>
            </div>
            <div class="image-container">
                <img src="{{ img_descricao07 }}" alt="Descrição">
            </div>
        </div>

        <!-- 8. Ordem -->
        <div class="section">
            <div class="question">📌 A Ordem está correta?</div>
            <div class="options">
                <label><input type="radio" name="q8" checked> Selecione...</label>
                <label><input type="radio" name="q8"> Sim</label>
                <label><input type="radio" name="q8"> Não</label>
            </div>
            <div class="image-container">
                <img src="{{ img_ordem08 }}" alt="Ordem">
            </div>
        </div>
    </div>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(
        HTML_TEMPLATE,
        img_dataf01="dataf01.png",
        img_datav02="datav02.png",
        img_dun03="dun03.png",
        img_material04="material04.png",
        img_guia05="guia05.JPG",
        img_lote06="lote06.png",
        img_descricao07="descricao07.png",
        img_ordem08="ordem08.png"
    )

if __name__ == '__main__':
    app.run(debug=True)
