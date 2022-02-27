from crypt import methods
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:example@localhost:5432/postgres"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class CarsModel(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    model = db.Column(db.String())
    doors = db.Column(db.Integer())

    def __init__(self, name, model, doors):
        self.name = name
        self.model = model
        self.doors = int(doors)

    def __repr__(self):
        return f"<Car {self.name}>"


@app.route('/')
def hello():
    return {"message": "hello world"}


@app.route('/car', methods=["POST", "GET"])
def handler_cars():
    if request.method == 'POST':
        if request.json:
            data = request.json
            print("data_____", data)
            print("data_____", data.get('name'))
            new_car = CarsModel(
                name=data['name'], model=data['model'], doors=data['doors'])

            db.session.add(new_car)
            db.session.commit()
            return {"message": "{} is created".format(new_car.name)}
        else:
            return {"message": "no json provided"}

    elif request.method == 'GET':
        cars = CarsModel.query.all()
        results = [
            {
                "name": car.name,
                "model": car.model,
                "doors": car.doors
            } for car in cars]

        return {"count": len(results), "cars": results}


if __name__ == '__main__':
    app.run(debug=True)
