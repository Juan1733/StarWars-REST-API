"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorito, Personaje, Planeta
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

def save(new_object):
    try:
        db.session.add(new_object)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def delete(object):
    try:
        db.session.delete(object)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/personajes', methods=['GET'])
def get_personajes():
    try:
        personajes = Personaje.query.all()
        if personajes:
            personajes_dict = list(map(lambda personaje: personaje.serialize(), personajes))
            return jsonify(personajes_dict),200
        return jsonify({
            "message": "No se encontro la informacion"
        }),404

    except:
        return({
            "message": "Ha ocurrido un error"
        }),500

@app.route('/personajes/<int:personaje_id>', methods=['GET'])
def get_personaje_byid(personaje_id):
    try:
        personaje = Personaje.query.get(personaje_id)
        if personaje:
            return jsonify(personaje.serialize()),200
        return jsonify({
            "message": "No se encontro el personaje"
        }),404

    except:
        return({
            "message": "Ha ocurrido un error"
        }),500

@app.route('/planetas', methods=['GET'])
def get_planetas():
    try:
        planetas = Planeta.query.all()
        if planetas:
            planetas_dict = list(map(lambda planeta: planeta.serialize(), planetas))
            return jsonify(planetas_dict),200
        return jsonify({
            "message": "No se encontro la informacion"
        }),404

    except:
        return({
            "message": "Ha ocurrido un error"
        }),500

@app.route('/planetas/<int:planeta_id>', methods=['GET'])
def get_planetas_byid(planeta_id):
    try:
        planeta = Planeta.query.get(planeta_id)
        if planeta:
            return jsonify(planeta.serialize()),200
        return jsonify({
            "message": "No se encontro el planeta"
        }),404

    except:
        return({
            "message": "Ha ocurrido un error"
        }),500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        usuarios = User.query.all()
        if usuarios:
            usuarios_dict = list(map(lambda user: user.serialize(), usuarios))
            return jsonify(usuarios_dict),200
        return jsonify({
            "message": "No se encontro la informacion"
        }),404

    except:
        return({
            "message": "Ha ocurrido un error"
        }),500

@app.route('/<int:user_id>/favoritos', methods=['GET'])
def get_favoritos(user_id):
    try:
        usuario = User.query.get(user_id)
        if not usuario:
            return jsonify({
                "message": "No se encontro el usuario"
            }),404
        
        favoritos_dict = list(map(lambda favorito: favorito.serialize(), usuario.favorites))
        return jsonify(favoritos_dict),200
    except:
        return({
            "message": "Ha ocurrido un error"
        }),500

@app.route('/<int:user_id>/favoritos/planeta/<int:planeta_id>', methods=['POST'])
def add_planet(user_id, planeta_id):
    try:
        usuario = User.query.get(user_id)
        planeta = Planeta.query.get(planeta_id)
        favorito = Favorito.query.filter(Favorito.id_user == user_id, Favorito.planeta_id == planeta_id).first()

        if usuario == None or planeta == None:
            return jsonify({
                "message": "No se encontro la informacion suministrada"
            }),404
        if favorito:
            return jsonify({
                "message": "el favorito ya existe"
            }),400

        new_favorito = Favorito.create(user_id, planeta_id, None)
        saved = save(new_favorito)
        if not saved:
            return jsonify({
                "message": "server down"
            }),500
        return jsonify({
            "message": "Planeta favorito añadido"
        }),200

    except:
        return({
            "message": "Ha ocurrido un error"
        }),500

@app.route('/<int:user_id>/favoritos/personaje/<int:personaje_id>', methods=['POST'])
def add_personaje(user_id, personaje_id):
    try:
        usuario = User.query.get(user_id)
        personaje = Personaje.query.get(personaje_id)
        favorito = Favorito.query.filter(Favorito.id_user == user_id, Favorito.personaje_id == personaje_id).first()

        if usuario == None or personaje == None:
            return jsonify({
                "message": "No se encontro la informacion suministrada"
            }),404
        if favorito:
            return jsonify({
                "message": "el favorito ya existe"
            }),400

        new_favorito = Favorito.create(user_id, None, personaje_id)
        saved = save(new_favorito)
        if not saved:
            return jsonify({
                "message": "server down"
            }),500
        return jsonify({
            "message": "Personaje favorito añadido"
        }),200
    except:
        return({
            "message": "Ha ocurrido un error"
        }),500


@app.route('/personajes', methods=['POST'])
def create():
    body = request.json
    new_personaje = Personaje.create(body["name"], body["gender"], body["height"])
    if isinstance(new_personaje, Personaje):
        saved = save(new_personaje)
        if not saved:
            return jsonify({
                "message": "Server down"
            }),500

        return jsonify({
            "message": "Personaje creado"
        }),201
    
    return jsonify({
        "message": "No se pudo crear"
    }),500

@app.route('/planetas', methods=['POST'])
def create_planet():
    body = request.json
    new_planeta = Planeta.create(body["name"], body["diameter"], body["gravity"])
    save(new_planeta)
    return jsonify({
        "message": "Planeta creado"
    })

@app.route('/usuario', methods=['POST'])
def create_user():
    body = request.json
    new_user = User.create(body["name"], body["last_name"], body["email"], body["password"])

    if new_user["success"] and isinstance(new_user, User):
        saved = save(new_user)
        if not saved:
            return jsonify({
                "message": "server down"
            }),500
        return jsonify([]),201
    return jsonify(new_user), 500

@app.route("/<int:user_id>/favoritos/planeta/<int:planeta_id>", methods=['DELETE'])
def pop_planeta(user_id, planeta_id):

    usuario = User.query.get(user_id)
    planeta = Planeta.query.get(planeta_id)
    if usuario == None or planeta == None:
        return jsonify({
            "message": "No se encontro la informacion suministrada"
        }),404
    favoritos = Favorito.query.filter_by(id_user=user_id).all()

    if len(favoritos) == 0:
        return jsonify({
            "message": "No se encontraron favoritos para el usuario seleccionado"
        }),200
    
    for i in range(0, len(favoritos)):
        if favoritos[i].planeta_id == planeta_id:
            id = favoritos[i].id
            fav = Favorito.query.get(id)
            deleted = delete(fav)
            if not deleted:
                return jsonify({
                    "message": "server down"
                }),500
            return jsonify({
                "message": "Se elimino el planeta de favoritos"
            }),200

    return({
        "message": "No se encontro el planeta favorito"
    }),404

@app.route("/<int:user_id>/favoritos/personaje/<int:personaje_id>", methods=['DELETE'])
def pop_personaje(user_id, personaje_id):

    usuario = User.query.get(user_id)
    personaje = Personaje.query.get(personaje_id)
    if usuario == None or personaje == None:
        return jsonify({
            "message": "No se encontro la informacion suministrada"
        }),404
    favoritos = Favorito.query.filter_by(id_user=user_id).all()

    if len(favoritos) == 0:
        return jsonify({
            "message": "No se encontraron favoritos para el usuario seleccionado"
        }),200
    
    for i in range(0, len(favoritos)):
        if favoritos[i].personaje_id == personaje_id:
            id = favoritos[i].id
            fav = Favorito.query.get(id)
            deleted = delete(fav)
            if not deleted:
                return jsonify({
                    "message": "server down"
                }),500
            return jsonify({
                "message": "Se elimino el personaje de favoritos"
            }),200
    return({
        "message": "No se encontro el personaje favorito"
    }),404

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
