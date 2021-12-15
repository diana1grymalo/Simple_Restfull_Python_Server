from datetime import date, datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime, ForeignKey, VARCHAR, func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///driver_veh_sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Driver(db.Model):
    __tablename__ = 'drivers'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    first_name = Column(VARCHAR(50), nullable=False)
    last_name = Column(VARCHAR(80), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    driver_id = Column(Integer, ForeignKey(Driver.id), nullable=False)
    make = Column(VARCHAR())
    model = Column(VARCHAR())
    plate_number = Column(VARCHAR(20), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


@app.route('/init')
def hi_world():
    db.create_all()
    return "200"


@app.route('/drivers/driver/', methods=['GET'])
def show_drivers():
    drivers_query = Driver.query
    params = request.args
    for key, value in params.items():
        if 'created_at' in key:
            conditional_date = datetime.strptime(value, "%d-%m-%Y").strftime('%Y-%m-%d')
            if '__lte' in key:
                drivers_query = drivers_query.filter(Driver.created_at <= conditional_date)
            elif '__gte' in key:
                drivers_query = drivers_query.filter(Driver.created_at >= conditional_date)
        if 'last_name' in key:
            last_name_url = value
            if 'contains' in key:
                drivers_query = drivers_query.filter(Driver.last_name.contains(value))
    drivers = drivers_query.all()
    output = []
    for driver in drivers:
        driver_data = {'first_name': driver.first_name, 'last_name': driver.last_name,
                       'created_at': driver.created_at.strftime("%d/%m/%y")}
        output.append(driver_data)
    return {"drivers": output}


@app.route('/drivers/driver/<id>/', methods=['GET'])
def show_driver(id):
    driver = Driver.query.get_or_404(id)
    return {'first_name': driver.first_name, 'last_name': driver.last_name}


@app.route('/drivers/driver/', methods=['POST'])
def create_driver():
    driver = Driver(first_name=request.json['first_name'], last_name=request.json['last_name'])
    db.session.add(driver)
    db.session.commit()
    return {'first_name': driver.first_name, 'last_name': driver.last_name, 'id': driver.id}


@app.route('/drivers/driver/<id>', methods=['PUT'])
def update_driver(id):
    driver = Driver.query.get_or_404(id)
    if 'first_name' in request.json:
        driver.first_name = request.json['first_name']
    if 'last_name' in request.json:
        driver.last_name = request.json['last_name']
    db.session.add(driver)
    db.session.commit()
    return {'first_name': driver.first_name, 'last_name': driver.last_name, 'id': driver.id}


@app.route('/drivers/driver/<id>', methods=['DELETE'])
def delete_driver(id):
    driver = Driver.query.get_or_404(id)
    db.session.delete(driver)
    db.session.commit()
    return {'message': 'driver was deleted successfully'}


if __name__ == '__main__':
    app.run()
