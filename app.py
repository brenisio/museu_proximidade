from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
import psycopg2
import random

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class LeitorProximidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distancia = db.Column(db.Integer, nullable=False)
    risco = db.Column(db.String(100), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def index():
    return "Servidor Flask em execução!"


@app.route('/leituras')
def ver_leituras():
    leituras = LeitorProximidade.query.order_by(LeitorProximidade.data.desc()).all()
    return jsonify([{'distancia': l.distancia, 'risco': l.risco, 'data': l.data} for l in leituras])


@app.route('/arduino')
def arduino_data():
    distancia = random.randint(10, 100)
    risco = "Alto" if distancia < 50 else "Baixo"

    new_reading = LeitorProximidade(distancia=distancia, risco=risco)
    db.session.add(new_reading)
    db.session.commit()

    return jsonify({'distancia': distancia, 'risco': risco, 'data': new_reading.data})

@app.route('/receber_dados', methods=['POST'])
def receber_dados():
    print(request.form)
    distancia = request.form.get('distancia', type=int)

    hora_ajustada = (datetime.utcnow() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
    if distancia is not None:
        if distancia > 0 and distancia < 10:
            risco = "PERIGO EMINENTE DE ROUBO!"
        elif distancia >= 10 and distancia < 20:
            risco = "ALERTA! Pessoa próxima a peça!"
        elif distancia >= 20 and distancia < 50:
            risco = "Observar movimento!"
        else:
            risco = "Distância segura. Sistema de segurança ligado."

        nova_leitura = LeitorProximidade(
            distancia=distancia,
            risco=risco,
            data=hora_ajustada,
        )
        db.session.add(nova_leitura)
        db.session.commit()

        return jsonify({'status': 'sucesso', 'distancia': distancia, 'risco': risco})
    else:
        return jsonify({'status': 'erro', 'mensagem': 'Distância não especificada'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
