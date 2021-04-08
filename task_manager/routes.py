from flask import Flask, render_template, url_for, request, redirect, flash
from task_manager import db, app, bcrypt, mail
from task_manager.models import Todo, User
from flask_login import login_user, current_user, logout_user, login_required
from task_manager.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                     RequestResetForm, ResetPasswordForm)
from flask_mail import Message

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        if len(task_content) != 0 and Todo.query.filter_by(content=task_content).first() == None:
            new_task = Todo(content=task_content, author=current_user)

            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except:
                flash('There was an issue adding your task','info')
                return redirect(url_for('index'))
        else:
            flash('Task Already exists','danger') if len(task_content) != 0 else flash('Task should not be Empty','danger')
            return redirect(url_for('index'))

    else:
        if current_user.is_authenticated:
            tasks = Todo.query.filter_by(author=current_user).order_by(Todo.date_created.desc()).all()
            return render_template('index.html', tasks=tasks)
        else:
            return render_template('index.html')


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        flash('There was a problem deleting that task','info')
        return redirect(url_for('index'))


@app.route('/update/<int:id>', methods=['GET', 'POST']) # Do not give space between int and id otherwise it shows error.
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content =  request.form['content']
        if len(task.content) != 0:
            try:
                db.session.commit()
                return redirect('/')
            except:
                flash('There was an issue adding your task','info')
                return redirect(url_for('index'))
        else:
            flash('Task should not be Empty','danger')
            return redirect(url_for('index'))

    else:
        return render_template('update.html', task=task)

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # db.session.add(user)
        # db.session.commit()
        global a 
        a = user
        confirm_mail(user)
        flash('We have sent an email to '+user.email+'. Click on the link provided to finish signing up.', 'info')
        return redirect(url_for('login')) #home is the function of the route
    return render_template('register.html', title='Register', form=form)

@app.route('/confirm_mail', methods=['GET', 'POST'])
def confirm_mail(user):
    token = user.get_reset_token()
    msg = Message('Email Confirmation on Task Master',
                  sender='yashgoyalg400@gmail.com',
                  recipients=[user.email])
    msg.body = f'''Confirm your email address,

Thank you for signing up for Task Manager!

To confirm your account, visit the following link:

{url_for('confirm_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

a = ''

@app.route("/email_confirmed/<token>", methods=['GET', 'POST'])
def confirm_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    db.session.add(a)
    db.session.commit()
    flash('Your account has been created! You are now able to log in', 'success')
    return render_template('mail_confirmed.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='yashgoyalg400@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    print(user)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = current_user.email
        db.session.commit()
        flash('Your username has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)