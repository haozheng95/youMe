import datetime
import json
import logging
from functools import wraps

import xmltodict
from flask import Flask, request, jsonify, render_template, flash, session as flask_session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager

from alibaba import Sample
from utils import generate_captcha, send_smscode, generate_token, verify_token, get_wx_info
from AREA import AREA, provinces_and_cities
from wx_pay import create_wx_pay_body, wx_pay, wx_payment

# 配置日志格式
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s %(levelname)s: %(message)s',
#                     filename='app.log',  # 日志文件名称
#                     filemode='a')  # 写入模式，“w”会覆盖文件，“a”会追加到文件

# 或者你也可以设置日志输出到控制台
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

app = Flask(__name__)
# 创建一个日志记录器，可以针对不同的模块或组件使用不同的记录器
logger = logging.getLogger(__name__)
app.secret_key = 'your-secret-key'
login_manager = LoginManager()
login_manager.init_app(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/activity_registration.db'
db = SQLAlchemy(app)


# 装饰器：用于保护需要认证的路由
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            logger.info("Authorization header: %s", request.headers['Authorization'])
            token = request.headers['Authorization'].split()[1]
        if not token:
            return jsonify({'error': 'Missing token. Authorization header required.', 'code': 0}), 401
        if not verify_token(token):
            return jsonify({'error': 'Invalid token.', 'code': 0}), 401
        return f(*args, **kwargs)

    return decorated


class TelephoneVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telephone = db.Column(db.String(20), unique=True, nullable=False)
    code = db.Column(db.String(20), nullable=False)


# 活动表单
class ActivityTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    number_of_participants = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.String(50), nullable=False)
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
    # option
    purpose_of_making_friends = db.Column(db.String(50), nullable=True)
    living_conditions = db.Column(db.String(50), nullable=True)
    car = db.Column(db.String(50), nullable=True)
    travel_experience = db.Column(db.String(50), nullable=True)
    postnuptial_plan = db.Column(db.String(50), nullable=True)
    evaluation_of_appearance = db.Column(db.String(50), nullable=True)
    personality_type = db.Column(db.String(50), nullable=True)


# 定义用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    open_id = db.Column(db.String(50), unique=True, nullable=False)
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
            'open_id': self.open_id
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
    banner = db.Column(db.Integer, nullable=False)  # 1 设置为banner 0 为普通活动
    img_link = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    activity_type = db.Column(db.Integer, nullable=False)  # 1 线下活动 2 过关立见 3 随机匹配
    participants = db.relationship('User', secondary='activity_user', lazy='dynamic')

    def get_deadline_for_registration(self):
        reference_date = datetime.datetime.now()
        return (self.end_date - reference_date).days

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'start_date': self.start_date.strftime("%Y-%m-%d %H:%M"),
            'end_date': self.end_date.strftime("%Y-%m-%d %H:%M"),
            'minimum_number_of_participants': self.minimum_number_of_participants,
            'maximum_number_of_participants': self.maximum_number_of_participants,
            'price': self.price,
            'img_link': self.img_link,
            'banner': self.banner,
            'activity_type': self.activity_type,
            'deadline_for_registration': self.get_deadline_for_registration()
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
    tmp_activities = [activity.to_dict() for activity in activities]
    all_activities = [x for x in tmp_activities if x["deadline_for_registration"] > 0]
    banner_list = [x for x in all_activities if x["banner"] == 1]
    activity_list = [x for x in all_activities if x["banner"] == 0]
    data = {"code": 1, "banner_list": banner_list, "activity_list": activity_list}
    return jsonify(data)


# 获取特定活动的报名用户
@app.route('/activities/<int:activity_id>/participants', methods=['GET'])
def get_activity_participants(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found', 'code': 0}), 404
    participants = [user.to_dict() for user in activity.participants.all()]
    return jsonify({'participants': participants, 'code': 1})


# 用户报名活动
@app.route('/activities/<int:activity_id>/register', methods=['POST'])
@requires_auth
def register_for_activity(activity_id):
    data = request.get_json()
    user_id = data.get('user_id')
    # number_of_participants = data.get('number_of_participants')
    # total_price = data.get('total_price')
    # open_id = data.get('open_id', None)
    # if open_id is None or len(open_id) == 0:
    #     return jsonify({'error': 'open_id required', 'code': 0}), 400
    datetime_now = str(datetime.datetime.now())

    if not user_id:
        return jsonify({'error': 'User ID required', 'code': 0}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found', 'code': 0}), 404

    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found', 'code': 0}), 404

    if user in activity.participants:
        return jsonify({'error': 'User is already registered for this activity', 'code': 0}), 409
    total_price = activity.price
    new_activity_table_record = ActivityTable(user_id=user_id, activity_id=activity_id, datetime=datetime_now,
                                              number_of_participants=1, total_price=total_price,
                                              phone=user.phone, nickname=user.nickname, name=user.name, sex=user.sex,
                                              province=user.province, city=user.city, age=user.age, height=user.height,
                                              weight=user.weight, degree=user.degree,
                                              marital_status=user.marital_status,
                                              occupation=user.occupation, monthly_salary=user.monthly_salary,
                                              personality_type=user.personality_type, car=user.car,
                                              travel_experience=user.travel_experience,
                                              postnuptial_plan=user.postnuptial_plan,
                                              evaluation_of_appearance=user.evaluation_of_appearance,
                                              )
    db.session.add(new_activity_table_record)
    db.session.commit()
    activity.participants.append(user)
    db.session.commit()

    body = create_wx_pay_body(activity.description, user.open_id, int(float(total_price) * 100))
    r = wx_pay(body)
    if r.status_code != 200:
        return jsonify({'error': r.text, 'code': 0}), 400
    data = wx_payment(r.json()['prepay_id'])
    return jsonify({'message': 'User registered successfully', 'data': data, 'code': 1})


# 用户取消报名活动
@app.route('/activities/<int:activity_id>/unregister', methods=['POST'])
def unregister_from_activity(activity_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID required', 'code': 0}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found', 'code': 0}), 404

    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found', 'code': 0}), 404

    if user not in activity.participants:
        return jsonify({'error': 'User is not registered for this activity', 'code': 0}), 409
    activity.participants.remove(user)
    db.session.commit()
    return jsonify({'message': 'User unregistered successfully', 'code': 1})


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
    activity_type = data.get('activity_type')
    img_link = data.get('img_link')
    banner = data.get('banner')

    logger.info("Create activity")
    if not name or not date_str:
        return jsonify({'error': 'Name and date are required', 'code': 0}), 401

    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS', 'code': 0}), 402

    new_activity = Activity(name=name, description=description, address=address, start_date=start_date,
                            end_date=end_date, minimum_number_of_participants=minimum_number_of_participants,
                            maximum_number_of_participants=maximum_number_of_participants, price=price, date=date,
                            activity_type=activity_type, img_link=img_link, banner=banner)
    db.session.add(new_activity)
    db.session.commit()
    return jsonify({'new_activity': new_activity.to_dict(), 'code': 1})


# 获取单个活动
@app.route('/activities/<int:activity_id>', methods=['GET'])
@requires_auth
def get_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found', 'code': 0}), 404
    data = activity.to_dict()
    data["code"] = 1
    return jsonify(data)


# 更新活动
@app.route('/activities/<int:activity_id>', methods=['PUT'])
@requires_auth
def update_activity(activity_id):
    data = request.get_json()
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found', 'code': 0}), 404

    name = data.get('name')
    if name:
        activity.name = name

    date_str = data.get('date')
    if date_str:
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            activity.date = date
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS', 'code': 0}), 400

    db.session.commit()
    return jsonify(activity.to_dict())


# 删除活动
@app.route('/activities/<int:activity_id>', methods=['DELETE'])
@requires_auth
def delete_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'error': 'Activity not found', 'code': 0}), 404

    db.session.delete(activity)
    db.session.commit()
    return jsonify({'message': 'Activity deleted successfully', 'code': 0})


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
    temp_code = data.get('temp_code')

    if not all([phone, name, nickname, sex, province, city, age, height, weight, degree, marital_status, occupation,
                monthly_salary, temp_code]):
        return jsonify(
            {
                'error': 'phone, name, nickname, sex, province, city, age, height, weight, temp_code'
                         'degree, occupation, monthly_salary and marital_status are required', 'code': 0}), 400

    r = get_wx_info(temp_code)
    if r.status_code != 200:
        logger.info(r.text)
        return jsonify({'error': 'get openid fail', 'text': r.text, 'code': 0}), 400
    if User.query.filter_by(phone=phone).first():
        return jsonify({'error': 'phone already exists', 'code': 0}), 400

    open_id = r.json().get('openid')

    logger.info('open id  is %s' % open_id)
    if open_id is None:
        return jsonify({'error': 'get open id error', 'text': r.text, 'code': 0}), 400
    new_user = User(phone=phone, nickname=nickname, name=name, sex=sex, province=province, city=city, age=age,
                    datetime=datetime_now, height=height, weight=weight, open_id=open_id,
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
    data = new_user.to_dict()
    data["auth_token"] = generate_token(data["id"])
    data["code"] = 1
    return jsonify(data)


# 获取所有用户
@app.route('/users', methods=['GET'])
@requires_auth
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


# 获取单个用户
@app.route('/users/<int:user_id>', methods=['GET'])
@requires_auth
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found', 'code': 0}), 404
    return jsonify({'data': user.to_dict(), 'code': 1})


# 删除用户
@app.route('/users/<int:user_id>', methods=['DELETE'])
@requires_auth
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found', 'code': 0}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully', 'code': 1})


@app.route('/verificationcode', methods=['POST'])
def get_verification_code():
    data = request.get_json()
    telephone = data.get('telephone')
    captcha = generate_captcha(4)
    # response = send_smscode(captcha, telephone)
    response = Sample.main(telephone, captcha)
    logger.info("telephone: {}".format(telephone))
    logger.info("captcha: {}".format(captcha))
    logger.info("response: {}".format(response))
    if response["body"]["Message"] != "OK":
        return jsonify({'error': 'send verification code failed', 'text': json.dumps(response), 'code': 0}), 400
    record = TelephoneVerification.query.filter_by(telephone=telephone).first()
    if record:
        db.session.delete(record)
        db.session.commit()
    new_record = TelephoneVerification(telephone=telephone, code=captcha)
    db.session.add(new_record)
    db.session.commit()
    return jsonify({'message': 'send verification code successfully', 'code': 1})


@app.route('/verificationcode/verify', methods=['POST'])
def verify_verification_code():
    data = request.get_json()
    telephone = data.get('telephone')
    verification_code = data.get('verification_code')
    logger.info("receive --- >telephone: {}".format(telephone))
    logger.info("receive --- >verification_code: {}".format(verification_code))
    record = TelephoneVerification.query.filter_by(telephone=telephone).first()

    if record is None:
        return jsonify({'error': 'Invalid Telephone', 'code': 0}), 400

    logger.info("save -> code:{}   save -> telephone: {}".format(record.code, record.telephone))
    if verification_code != record.code:
        return jsonify({'error': 'Invalid Verification Code', 'code': 0}), 401
    db.session.delete(record)
    db.session.commit()
    # 查找用户
    user = User.query.filter_by(phone=telephone).first()
    # 验证密码
    if user:
        token = generate_token(user.id)
        return jsonify({'message': 'Successful verificationt and The user has filled in the personal information.',
                        'user_id': user.id, 'auth_token': token, 'code': 1, 'open_id': user.open_id}), 200
    return jsonify({'message': 'Successful verificationt,'
                               'However, you are an unregistered user and need to submit information to register',
                    'user_id': -1, 'auth_token': '', 'code': 1}), 200


@app.route('/provinces', methods=['GET'])
def get_provinces():
    """获取所有省份列表"""
    return jsonify({'provinces': list(provinces_and_cities.keys()), 'code': 1})


@app.route('/province/<province_name>/cities', methods=['GET'])
def get_cities_by_province(province_name):
    """根据省份名称获取对应的城市列表"""
    if province_name in provinces_and_cities:
        cities = provinces_and_cities[province_name]
        return jsonify({'cities': cities, 'code': 1})
    else:
        return jsonify({"error": "Province not found", 'code': 0}), 404


@app.route('/wechat_pay/notify', methods=['POST'])
def wechat_pay_notify():
    try:
        # 获取请求体内容
        xml_data = request.data.decode('utf-8')
        data = xmltodict.parse(xml_data)['xml']

        # 验证签名
        # signature = data.pop('sign')
        # if not verify_signature(data, signature):
        #     logger.info("verify signature failed")
        #     return 'verify signature failed', 400

        # 处理业务逻辑
        # 例如：更新订单状态、记录支付信息等

        # 返回处理结果给微信支付
        return_data = {
            'return_code': 'SUCCESS',  # 返回状态码
            'return_msg': 'OK'  # 返回信息
        }
        return xmltodict.unparse({'xml': return_data}), 200
    except Exception as e:
        logger.info("error: {}".format(e))
        return '处理通知时发生错误', 500


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
    app.run(debug=False, host='0.0.0.0', port=80)
