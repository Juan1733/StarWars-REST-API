from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    favorites = db.relationship('Favorito', backref="user", lazy='select')
    
    @classmethod
    def create(cls, name, last_name, email, password):
        try:
            email_valid = cls.email_is_valid(email)
            if not email_valid:
                raise Exception({
                    "message": "el email no es valido"
                })
            new_user = cls(name=name, last_name=last_name, email=email, password=password)
            return ({
                "success": True,
                "user": new_user,
                "message": "created"
            })
        except:
            return ({
                "success": False,
                "user": None,
            })
        
    
    @classmethod
    def email_is_valid(cls, user_email):
        try:
            user_exist = cls.query.filter_by(email=user_email).one_or_none()
            if user_exist:
                return False
            return True
        except Exception as error:
            return False

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.last_name,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Favorito(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    personaje_id = db.Column(db.Integer, db.ForeignKey('personaje.id'))
    planeta_id = db.Column(db.Integer, db.ForeignKey('planeta.id'))

    @classmethod
    def create(cls, id_user, planeta_id, personaje_id):
        return cls(id_user=id_user, planeta_id=planeta_id, personaje_id=personaje_id)
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.id_user,
            "personaje_id": self.personaje_id,
            "planeta_id": self.planeta_id
        }

class Personaje(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    gender = db.Column(db.String(250), nullable=False)
    height = db.Column(db.String(250), nullable=False)
    favoritos = db.relationship('Favorito', backref="personaje", lazy='select', uselist=False)

    @classmethod
    def create(cls, name, gender, height):
        return cls(name=name, gender=gender, height=height)
    
    @classmethod
    def name_is_valid(cls, name):
        pass

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
        }

class Planeta(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    diameter = db.Column(db.String(250), nullable=False)
    gravity = db.Column(db.String(250), nullable=False)
    favoritos = db.relationship('Favorito', backref="planeta", lazy='select', uselist=False)

    @classmethod
    def create(cls, name, diameter, gravity):
        return cls(name=name, diameter=diameter, gravity=gravity)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "gravity": self.gravity,
        }