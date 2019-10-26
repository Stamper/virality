from itsdangerous import Signer, BadSignature
from uuid import uuid4
from os import path

from flask import render_template, request, url_for, redirect, abort
from flask_login import login_user, logout_user, login_required, current_user
from flask_paginate import Pagination, get_page_parameter

from . import app, db
from .forms import LoginForm, SignUpForm, ProfileForm
from .models import User, Invite, Image
from .exceptions import IntegrityErrorException


@app.route('/', methods=['GET'])
def index():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    users = User.query.all()
    pagination = Pagination(page=page, total=User.query.count(), search=False, record_name='users')

    return render_template('index.html', users=users, pagination=pagination)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileForm(description=current_user.description)
    if request.method == 'POST':
        desc = form.description.data
        if current_user.description != desc:
            current_user.description = desc
            db.session.commit()

        image_name = form.image.data.filename
        if image_name:
            _, file_type = path.splitext(image_name)
            file_name = ''.join((uuid4().hex[:16], file_type))
            form.image.data.save(path.join(app.config.get('UPLOAD_FOLDER'), file_name))
            db.session.add(Image(file_name=file_name))
            db.session.commit()

    return render_template('profile.html', form=form, images=current_user.images)


@app.route('/details/<int:user_id>', methods=['GET'])
def details(user_id):
    try:
        user = User.query.get(user_id)
        return render_template('details.html', description=user.description, images=user.images)

    except:
        abort(404)


@app.route('/invite', methods=['GET'])
@login_required
def invite():
    new_invite = Invite()
    db.session.add(new_invite)
    db.session.commit()

    return render_template('invite.html',
                           invite_link=url_for('invitation', _external=True, code=new_invite.code,
                                               token=new_invite.token))


@app.route('/invitation', methods=['GET'])
def invitation():
    code = request.args.get('code')
    token = request.args.get('token')

    if not code or not token:
        abort(404)

    if token != Invite.get_token(code):
        abort(400)

    invite = Invite.query.filter_by(code=code).first()
    if invite:
        if invite.redeemed:
            abort(400)

        if current_user.is_authenticated:
            logout_user()

        invite_id = Signer(app.config.get('CONFIRMATION_SECRET')).sign(str(invite.id)).decode('ascii')
        form = SignUpForm(invite=invite_id)
        return render_template('signup.html', form=form)

    else:
        abort(404)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if not user or not user.valid_password(form.password.data):
                return render_template('error.html', message='Incorrect email or password')

            login_user(user)
            return redirect(url_for('index'))

        else:
            return render_template('error.html', message='Check correctness of the inputted data')

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.password.data != form.password2.data:
                return render_template('error.html', message='Passwords mismatch')

            new_user = User(email=form.email.data, raw_password=form.password.data)

            invite = None
            if form.invite.data:
                try:
                    invite_id = Signer(app.config.get('CONFIRMATION_SECRET')).unsign(form.invite.data).decode('ascii')
                    invite = Invite.query.get(invite_id)

                except BadSignature:
                    abort(400)

            try:
                new_user.register(invite)
                login_user(new_user)

                return redirect(url_for('index'))

            except IntegrityErrorException:
                return render_template('error.html', message='This email address has been taken before')
        else:
            return render_template('error.html', message='Check correctness of the inputted data')

    return render_template('signup.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))
