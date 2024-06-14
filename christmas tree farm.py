# app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://your_username:your_password@localhost/your_database'
db = SQLAlchemy(app)

class Tree(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Integer)
    max_ornaments = db.Column(db.Integer)
    ornaments = db.relationship('Ornament', backref='tree', lazy=True)

class Ornament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    color = db.Column(db.String(50))
    ornament_type = db.Column(db.String(50))
    on_tree = db.Column(db.Boolean, default=False)
    tree_id = db.Column(db.Integer, db.ForeignKey('tree.id'), nullable=True)

@app.route('/trees', methods=['POST', 'PUT', 'GET'])
def manage_trees():
    if request.method == 'POST':
        data = request.json
        new_tree = Tree(height=data['height'], max_ornaments=data['max_ornaments'])
        db.session.add(new_tree)
        db.session.commit()
        return jsonify({'message': 'Tree added successfully'})

    elif request.method == 'PUT':
        data = request.json
        tree_id = data['id']
        tree = Tree.query.get(tree_id)
        if tree:
            tree.height = data['height']
            tree.max_ornaments = data['max_ornaments']
            db.session.commit()
            return jsonify({'message': 'Tree updated successfully'})
        else:
            return jsonify({'message': 'Tree not found'})

    elif request.method == 'GET':
        trees = Tree.query.all()
        tree_list = []
        for tree in trees:
            tree_data = {
                'id': tree.id,
                'height': tree.height,
                'max_ornaments': tree.max_ornaments,
                'ornaments': [ornament.id for ornament in tree.ornaments]
            }
            tree_list.append(tree_data)
        return jsonify({'trees': tree_list})

@app.route('/ornaments', methods=['POST', 'PUT', 'GET'])
def manage_ornaments():
    if request.method == 'POST':
        data = request.json
        new_ornament = Ornament(price=data['price'], color=data['color'], ornament_type=data['ornament_type'])
        db.session.add(new_ornament)
        db.session.commit()
        return jsonify({'message': 'Ornament added successfully'})

    elif request.method == 'PUT':
        data = request.json
        ornament_id = data['id']
        ornament = Ornament.query.get(ornament_id)
        if ornament:
            ornament.price = data['price']
            ornament.color = data['color']
            ornament.ornament_type = data['ornament_type']
            db.session.commit()
            return jsonify({'message': 'Ornament updated successfully'})
        else:
            return jsonify({'message': 'Ornament not found'})

    elif request.method == 'GET':
        ornaments = Ornament.query.all()
        ornament_list = []
        for ornament in ornaments:
            ornament_data = {
                'id': ornament.id,
                'price': ornament.price,
                'color': ornament.color,
                'ornament_type': ornament.ornament_type,
                'on_tree': ornament.on_tree,
                'tree_id': ornament.tree_id
            }
            ornament_list.append(ornament_data)
        return jsonify({'ornaments': ornament_list})

@app.route('/decorate', methods=['POST', 'PUT', 'DELETE'])
def decorate_tree():
    data = request.json
    ornament_id = data['ornament_id']
    tree_id = data['tree_id']

    ornament = Ornament.query.get(ornament_id)
    tree = Tree.query.get(tree_id)

    if not ornament or not tree:
        return jsonify({'message': 'Ornament or Tree not found'})

    if request.method == 'POST':
        if ornament.on_tree or len(tree.ornaments) >= tree.max_ornaments:
            return jsonify({'message': 'Ornament cannot be added to the tree'})

        ornament.on_tree = True
        ornament.tree_id = tree.id
        db.session.commit()
        return jsonify({'message': 'Ornament added to the tree successfully'})

    elif request.method == 'PUT':
        if not ornament.on_tree or ornament.tree_id != tree.id:
            return jsonify({'message': 'Ornament is not on the specified tree'})

        ornament.on_tree = False
        ornament.tree_id = None
        db.session.commit()
        return jsonify({'message': 'Ornament removed from the tree successfully'})

    elif request.method == 'DELETE':
        db.session.delete(ornament)
        db.session.commit()
        return jsonify({'message': 'Ornament deleted successfully'})

@app.route('/farm', methods=['GET'])
def get_farm():
    trees = Tree.query.all()
    farm_data = []
    for tree in trees:
        tree_data = {
            'id': tree.id,
            'height': tree.height,
            'ornaments': [{'id': ornament.id, 'price': ornament.price, 'color': ornament.color, 'type': ornament.ornament_type}
                          for ornament in tree.ornaments]
        }
        farm_data.append(tree_data)
    return jsonify({'farm': farm_data})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
