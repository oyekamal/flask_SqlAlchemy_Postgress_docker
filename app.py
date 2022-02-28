from crypt import methods
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid
import jwt
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:example@localhost:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
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


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(255))
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    admin = db.Column(db.Boolean)


class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    Author = db.Column(db.String(50), unique=True, nullable=False)
    Publisher = db.Column(db.String(50), nullable=False)
    book_prize = db.Column(db.Integer)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Users.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator


@app.route('/register', methods=['POST'])
def signup_user():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(public_id=str(uuid.uuid4()),
                     name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'registered successfully'})


@app.route('/login', methods=['POST'])
def login_user():
    auth = request.json
    if not auth or not auth['name'] or not auth['password']:
        return make_response('could not verify', 401, {'Authentication': 'login required"'})

    user = Users.query.filter_by(name=auth['name']).first()
    if check_password_hash(user.password, auth['password']):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], "HS256")

        return jsonify({'token': token})

    return make_response('could not verify',  401, {'Authentication': '"login required"'})


@app.route('/book', methods=['POST'])
@token_required
def create_book(current_user):

    data = request.get_json()

    new_books = Books(name=data['name'], Author=data['Author'], Publisher=data['Publisher'],
                      book_prize=data['book_prize'], user_id=current_user.id)
    db.session.add(new_books)
    db.session.commit()
    return jsonify({'message': 'new books created'})


@app.route('/books', methods=['GET'])
@token_required
def get_books(current_user):

    books = Books.query.filter_by(user_id=current_user.id).all()
    output = []
    for book in books:
        book_data = {}
        book_data['id'] = book.id
        book_data['name'] = book.name
        book_data['Author'] = book.Author
        book_data['Publisher'] = book.Publisher
        book_data['book_prize'] = book.book_prize
        output.append(book_data)

    return jsonify({'list_of_books': output})


@app.route('/books/<book_id>', methods=['DELETE'])
@token_required
def delete_book(current_user, book_id):

    book = Books.query.filter_by(id=book_id, user_id=current_user.id).first()
    if not book:
        return jsonify({'message': 'book does not exist'})

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})


@app.route('/')
def hello():
    return {"message": "hello world"}


@app.route('/cars', methods=["POST", "GET"])
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
            {"id": car.id,
                "name": car.name,
                "model": car.model,
                "doors": car.doors
             } for car in cars]

        return {"count": len(results), "cars": results}


@app.route('/cars/<car_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_car(car_id):
    car = CarsModel.query.get_or_404(car_id)

    if request.method == 'GET':
        response = {
            "name": car.name,
            "model": car.model,
            "doors": car.doors
        }
        return {"message": "success", "car": response}

    elif request.method == 'PUT':
        data = request.json
        car.name = data['name']
        car.model = data['model']
        car.doors = data['doors']
        db.session.add(car)
        db.session.commit()
        return {"message": f"car {car.name} successfully updated"}

    elif request.method == 'DELETE':
        db.session.delete(car)
        db.session.commit()
        return {"message": f"Car {car.name} successfully deleted."}


if __name__ == '__main__':
    app.run(debug=True)
