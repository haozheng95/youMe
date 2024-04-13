import datetime

from flask import Flask, request, jsonify, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required

app = Flask(__name__)
app.secret_key = 'your-secret-key'
login_manager = LoginManager()
login_manager.init_app(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/activity_registration.db'
db = SQLAlchemy(app)


# 活动表单
class ActivityTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    number_of_participants = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.String(50), nullable=False)


# 定义用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    nickname = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(50), nullable=False)  # 姓名
    sex = db.Column(db.String(50), nullable=False)  # 性别
    province = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.String(50), nullable=False)
    degree = db.Column(db.String(50), nullable=False)
    marital_status = db.Column(db.String(50), nullable=False)
    occupation = db.Column(db.String(50), nullable=False)  # 职业
    monthly_salary = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.String(50), nullable=False)
    # option
    purpose_of_making_friends = db.Column(db.String(50), nullable=True)
    living_conditions = db.Column(db.String(50), nullable=True)
    car = db.Column(db.String(50), nullable=True)
    travel_experience = db.Column(db.String(50), nullable=True)
    postnuptial_plan = db.Column(db.String(50), nullable=True)
    evaluation_of_appearance = db.Column(db.String(50), nullable=True)
    personality_type = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'sex': self.sex,
            'province': self.province,
            'city': self.city,
            'age': self.age,
            'degree': self.degree,
        }


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    minimum_number_of_participants = db.Column(db.Integer, nullable=False)
    maximum_number_of_participants = db.Column(db.Integer, nullable=False)
    price = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    participants = db.relationship('User', secondary='activity_user', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'minimum_number_of_participants': self.minimum_number_of_participants,
            'maximum_number_of_participants': self.maximum_number_of_participants,
            'price': self.price,
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
    number_of_participants = data.get('number_of_participants')
    total_price = data.get('total_price')

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

    new_activity_table_record = ActivityTable(user_id=user_id, activity_id=activity_id, datetime=datetime_now,
                                              number_of_participants=number_of_participants, total_price=total_price)
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
    description = data.get('description')
    address = data.get('address')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    minimum_number_of_participants = data.get('minimum_number_of_participants')
    maximum_number_of_participants = data.get('maximum_number_of_participants')
    price = data.get('price')
    date_str = data.get('date')
    if not name or not date_str:
        return jsonify({'error': 'Name and date are required'}), 400

    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400

    new_activity = Activity(name=name, description=description, address=address, start_date=start_date,
                            end_date=end_date, minimum_number_of_participants=minimum_number_of_participants,
                            maximum_number_of_participants=maximum_number_of_participants, price=price, date=date)
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
    phone = data.get('phone')
    name = data.get('name')
    nickname = data.get('nickname')
    sex = data.get('sex')
    province = data.get('province')
    city = data.get('city')
    age = data.get('age')
    height = data.get('height')
    weight = data.get('weight')
    degree = data.get('degree')
    marital_status = data.get('marital_status')
    occupation = data.get('occupation')
    monthly_salary = data.get('monthly_salary')
    datetime_now = str(datetime.datetime.now())

    if not all([phone, name, nickname, sex, province, city, age, height, weight, degree, marital_status, occupation,
                monthly_salary]):
        return jsonify(
            {
                'error': 'phone, name, nickname, sex, province, city, age, height, weight, '
                         'degree, occupation, monthly_salary and marital_status are required'}), 400

    if User.query.filter_by(phone=phone).first():
        return jsonify({'error': 'phone already exists'}), 400

    new_user = User(phone=phone, nickname=nickname, name=name, sex=sex, province=province, city=city, age=age,
                    datetime=datetime_now, height=height, weight=weight,
                    degree=degree, marital_status=marital_status, occupation=occupation, monthly_salary=monthly_salary)
    # add options
    new_user.purpose_of_making_friends = data.get('purpose_of_making_friends')
    new_user.living_conditions = data.get('living_conditions')
    new_user.car = data.get('car')
    new_user.travel_experience = data.get('travel_experience')
    new_user.postnuptial_plan = data.get('postnuptial_plan')
    new_user.evaluation_of_appearance = data.get('evaluation_of_appearance')
    new_user.personality_type = data.get('personality_type')

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


@app.route('/verificationcode', methods=['POST'])
def get_verification_code():
    data = request.get_json()
    telephone = data.get('telephone')
    print(telephone)
    # verification_code = data.get('verification_code')
    return jsonify({'message': 'send verification code successfully'})


@app.route('/verificationcode/verify', methods=['POST'])
def verify_verification_code():
    data = request.get_json()
    telephone = data.get('telephone')
    print(telephone)
    verification_code = data.get('verification_code')
    print(verification_code)

    # 查找用户
    user = User.query.filter_by(phone=telephone).first()

    # 验证密码
    if user:
        login_user(user)  # 登录用户，设置 session
    else:
        flash('Invalid username or password')
    return jsonify({'message': 'send verification code successfully'})


@login_manager.user_loader
def load_user(user_id):
    # 根据 user_id 从数据库加载用户
    return User.query.get(int(user_id))


# ====================== view
@app.route('/', methods=['GET'])
def view_index():
    return render_template('index.html')


@app.route('/view/login', methods=['GET'])
def view_login():
    return render_template('login.html')

@app.route('/view/profile', methods=['GET'])
def view_profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
