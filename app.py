from flask import Flask, jsonify, request, session, url_for # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore 
from flask_cors import CORS # type: ignore
import os


app = Flask(__name__)
# configura o caminho do meu banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:URzRovfysRZHYEoCTcRWePvDFzgsmMVT@metro.proxy.rlwy.net:14960/Cashback'
app.secret_key = 'CashbackCalculatorSecretKey' # chave secreta para a sessão, ou da erro de runtime

db = SQLAlchemy(app) #Inicia o FlaskAlchemy com Flask


with app.app_context():
    db.create_all()
    
CORS(app, resources={r"/*": {"origins": "*"}}) # Habilita o CORS para permitir requisições do frontend


class Consulta(db.Model): #criei direto daqui com sqlalchemy
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50))
    valor = db.Column(db.Float)
    tipo_cliente = db.Column(db.String(10))
    cashback = db.Column(db.Float)

# rota 
@app.route('/', methods=['GET', 'POST'])
def CashbackCalculator():

    if request.method == 'POST':
        dados_html = request.get_json() # pegou os dados do front, e fez o Python entender

        valor = float(dados_html.get('valor', '0'))
        vip = dados_html.get('vip', '') # recebe sim ou nao9
        cupom = dados_html.get('cupom', '') 
       

        # 1. Desconto do cupom
        if cupom:

            desconto_percentual = float(cupom) / 100 # transformou o valor do cupom para porcentagem
            desconto = valor * desconto_percentual # aqui ele calculou o valor do desconto
            
        else:
            desconto = 0   # se nao tem cupom, claro que nao tem desconto 


        valor_com_desconto = valor - desconto

        # 2. Parte do cashback

        cashback_normal = valor_com_desconto * 0.05 # primeiro o cashback base...

        if vip == 'sim':
            cashback_extra_vip = cashback_normal * 0.10 # depois o cashback do vip
            cashback = cashback_normal + cashback_extra_vip
        else:
            cashback = cashback_normal    

        if valor > 500: # regra dos 500
            cashback = cashback * 2
            
        cashback = round(cashback, 2) # arredonda  para 2 casas decimais
        
        
        ip = request.headers.get('X-Forwarded-For', request.remote_addr) # Para pegar o IP, mas se nao tiver, usa o padrao (importante)

        # Banco de dados: salva a consulta no banco de dados, com os dados que eu preciso
        nova_consulta = Consulta(ip=ip, valor=valor, tipo_cliente=vip, cashback=cashback)

        db.session.add(nova_consulta)
        db.session.commit()


        return jsonify({'cashback': cashback}) # devolve o meu valor de cashback em formato JSON 
    
    else:  

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)


        consultas = Consulta.query.filter_by(ip=ip)\
        .order_by(Consulta.id.desc())\
        .limit(4)\
        .all()




        resultado = [
            {
                "valor": consulta.valor,
                "tipo_cliente": consulta.tipo_cliente,
                "cashback": consulta.cashback
            }
            for consulta in consultas
        ]

        return jsonify(resultado)
        



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)