#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
api = Api(app)

db.init_app(app)


class Campers(Resource):
    def get(self):
        campers = [c.to_dict(rules=("-signups",)) for c in Camper.query.all()]
        return make_response(campers, 200)


api.add_resource(Campers, "/campers")


class CamperById(Resource):
    def get(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        return make_response(camper.to_dict(rules=("-signups.activity.signups",)), 200)

    def patch(self, id):
        data = request.get_json()
        camper = Camper.query.get(id)
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        try:
            for attr, value in data.items():
                setattr(camper, attr, value)
        except:
            return make_response({"errors": ["validation erros"]})
        db.session.add(camper)
        db.session.commit()
        return make_response(camper.to_dict(rules=("-signups",)), 202)


api.add_resource(CamperById, "/campers/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
