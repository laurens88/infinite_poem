from openai import OpenAI
from flask import Flask, render_template_string, jsonify
import threading

client = OpenAI()
app = Flask(__name__)

current_poem = """Oh, beste Diederik, wat een fijne tijd,
Sinterklaas is weer in het land, dat weet je ongetwijfeld al kwijt.
Met surprises, lekkers en een goed stukje pepernoot,
Komt dit gedicht als cadeautje, recht uit de Sint zijn boot.

Op de middelbare school doe jij je best,
Maar in je vrije tijd vind je natuurlijk pas echt rust en rest.
Achter je scherm, met een game in je hand,
Reis je door werelden, vaak spannender dan ons platte land.

Of zet je muziek op, lekker keihard in je oren,
Van beats, melodieën en teksten kan jij zo veel horen.
Een echte kenner ben jij, dat moet ik wel zeggen,
Misschien kun je de Sint ooit nog wat goede nummers uitleggen.

Maar nu terug naar vandaag, met wat lekkers erbij,
Want Sinterklaas heeft voor jou een pakje, o zo blij.
Pak het uit en geniet, dat is het enige wat telt,
Want deze avond is speciaal, met jou gezellig in het veld."""
next_poem = None

lock = threading.Lock()


def generate_poem(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a conversation assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def prefetch_next_poem():
    global next_poem
    prompt = f"Schrijf het vervolg van het sinterklaas gedicht hieronder. Het is erg belangrijk dat het nieuwe deel even lang is als het vorige deel (16 regels). Zorg ervoor dat het einde niet afsluitend is, zodat er later nog een kantje aan toegevoegd kan worden.\n\n{current_poem}"
    with lock:
        next_poem = generate_poem(prompt)


@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gedicht Diederik</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: gold;
                color: #333;
                margin: 0;
                padding: 20px;
                text-align: center;
            }

            h1 {
                color: #CC0000;
                margin-bottom: 20px;
            }

            pre {
                background-color: sandybrown;
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
                font-size: 16px;
                white-space: pre-wrap;
                word-wrap: break-word;
                margin: 20px auto;
                max-width: 600px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }

            button {
                background-color: #CC0000;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                border-radius: 5px;
            }

            button:hover {
                background-color: #45a049;
            }

            #loading {
                display: none;
                margin-top: 20px;
                font-size: 14px;
                color: #CC0000;
            }
        </style>
        <script>
            async function fetchPoem() {
                const loadingIndicator = document.getElementById('loading');
                loadingIndicator.style.display = 'block'; // Show loading message
                try {
                    const response = await fetch('/poem');
                    const data = await response.json();
                    document.getElementById('poem').innerText = data.poem;
                } finally {
                    loadingIndicator.style.display = 'none'; // Hide loading message
                }
            }
        </script>
    </head>
    <body>
        <h1>Sinterklaas Gedicht Diederik</h1>
        <pre id="poem">{{ poem }}</pre>
        <button onclick="fetchPoem()">Volgende pagina</button>
        <div id="loading">Volgende pagina aan het laden...</div>
    </body>
    </html>
    ''', poem=current_poem)


@app.route('/poem')
def poem():
    global current_poem, next_poem
    with lock:
        served_poem = next_poem
        current_poem = served_poem
        next_poem = None

    threading.Thread(target=prefetch_next_poem).start()

    return jsonify(poem=served_poem)


if __name__ == '__main__':
    threading.Thread(target=prefetch_next_poem).start()
    app.run(debug=True, port=8000)
