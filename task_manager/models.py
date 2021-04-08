from task_manager import db, app, login_manager
from datetime import datetime
from flask_login import UserMixin #UserMixin class contains various common methods like is_authenticated, is_valid etc.
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader #decorator
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False) #hashing algorithm with convert the password into 60 characters long
    tasks = db.relationship('Todo', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Todo('{'<Task %r>' % self.id}','{self.content}')"
        # return f"Todo('{'<Task %r>' % self.id}', '{self.date_created}')"
        # return '<Task %r>' % self.id

# print(Todo.query.filter_by(content='April Coming').first().content)
#Postgresql command for restarting the index
# ALTER SEQUENCE seq RESTART WITH 1;
# UPDATE foo SET id = DEFAULT;