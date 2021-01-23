from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email
from oauth import OAuthSignIn
from hashlib import md5


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.blog')
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.register'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    
    if current_user.is_authenticated:
        flash(_('Olá, %(username)s!', username=current_user.username ))
        return redirect(url_for('main.blog'))
      
    form = RegistrationForm()
    if form.validate_on_submit():
        digest = md5(form.email.data.lower().encode('utf-8')).hexdigest()
        picture= 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, 50)
        user = User(username=form.username.data, email=form.email.data,avatar=picture)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        usuario=current_user.username
        flash("Parabéns, %s ! Você está logado!" %usuario )
        return redirect(url_for('main.blog'))
   
    form2 = LoginForm()
    if form2.validate_on_submit():
        user = User.query.filter_by(username=form2.username.data).first()
        if user is None or not user.check_password(form2.password.data):
            flash(_('Nome inválido'))
            return redirect(url_for('auth.register'))
        login_user(user, remember=form2.remember_me.data)
        usuario=current_user.username
        flash("Bem vindo de volta, %s !" %usuario )
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.blog')
        return redirect(next_page)
    return render_template('auth/register.html', title=_('Register'),
                          form=form, form2=form2 )



@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.blog'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('blog'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@bp.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.blog'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, ide, picture = oauth.callback()
    dados=picture
    picture=(dados['data']['url'])
    
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('main.blog'))
    
    if picture is None:
        digest = md5(email.lower().encode('utf-8')).hexdigest()
        picture= 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, 50)
    user = User.query.filter_by(email=email).first()
    if not user:
        avatar=picture
        user = User(username=username,  email=email, avatar=avatar)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('main.blog', avatar=user.avatar))



