import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/activity_registration.db'
db = SQLAlchemy(app)


# 活动表单
class ActivityTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), nullable=False)  # 姓名
    sex = db.Column(db.String(50), nullable=False)  # 性别
    province = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    degree = db.Column(db.String(50), nullable=False)
    marital_status = db.Column(db.String(50), nullable=False)
    occupation = db.Column(db.String(50), nullable=False)  # 职业
    monthly_salary = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.String(50), nullable=False)


# 定义用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    wx = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'wx': self.wx
        }


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    participants = db.relationship('User', secondary='activity_user', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S')
        }


# 定义用户和活动的关联表
activity_user = db.Table('activity_user',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                         db.Column('activity_id', db.Integer, db.ForeignKey('activity.id'), primary_key=True)
                         )

# 创建数据库表
db.create_all()


# 获取所有活动
@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    return jsonify([activity.to_dict() for activity in activities])


# 获取特定活动的报名用户
@app.route('/activities/<int:activity_id>/participants', methods=['GET'])
def get_activity_participants(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    participants = [user.to_dict() for user in activity.participants.all()]
    return jsonify(participants)


# 用户报名活动
@app.route('/activities/<int:activity_id>/register', methods=['POST'])
def register_for_activity(activity_id):
    data = request.get_json()
    user_id = data.get('user_id')
    row = dict(
        name=data.get('name'),
        sex=data.get('sex'),
        province=data.get('province'),
        city=data.get('city'),
        age=data.get('age'),
        degree=data.get('degree'),
        marital_status=data.get('marital_status'),
        occupation=data.get('occupation'),
        monthly_salary=data.get('monthly_salary'),
        phone=data.get('phone'))

    datetime_now = str(datetime.datetime.now())

    if not user_id:
        return jsonify({'error': 'User ID required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404

    if user in activity.participants:
        return jsonify({'error': 'User is already registered for this activity'}), 409

    new_activity_table_record = ActivityTable(user_id=user_id, activity_id=activity_id, datetime=datetime_now, **row)
    db.session.add(new_activity_table_record)
    db.session.commit()
    activity.participants.append(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})


# 用户取消报名活动
@app.route('/activities/<int:activity_id>/unregister', methods=['POST'])
def unregister_from_activity(activity_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404

    if user not in activity.participants:
        return jsonify({'error': 'User is not registered for this activity'}), 409
    activity.participants.remove(user)
    db.session.commit()
    return jsonify({'message': 'User unregistered successfully'})


# 创建活动
@app.route('/activities', methods=['POST'])
def create_activity():
    data = request.get_json()
    name = data.get('name')
    date_str = data.get('date')
    if not name or not date_str:
        return jsonify({'error': 'Name and date are required'}), 400

    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400

    new_activity = Activity(name=name, date=date)
    db.session.add(new_activity)
    db.session.commit()
    return jsonify(new_activity.to_dict()), 201


# 获取单个活动
@app.route('/activities/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    return jsonify(activity.to_dict())


# 更新活动
@app.route('/activities/<int:activity_id>', methods=['PUT'])
def update_activity(activity_id):
    data = request.get_json()
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404

    name = data.get('name')
    if name:
        activity.name = name

    date_str = data.get('date')
    if date_str:
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            activity.date = date
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400

    db.session.commit()
    return jsonify(activity.to_dict())


# 删除活动
@app.route('/activities/<int:activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404

    db.session.delete(activity)
    db.session.commit()
    return jsonify({'message': 'Activity deleted successfully'})


# 创建用户
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    wx = data.get('wx')
    password = data.get('password')

    if not all([username, wx, password]):
        return jsonify({'error': 'Username, wx, and password are required'}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(wx=wx).first():
        return jsonify({'error': 'Username or email already exists'}), 400

    new_user = User(username=username, wx=wx)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201


# 获取所有用户
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


# 获取单个用户
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())


# 删除用户
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
