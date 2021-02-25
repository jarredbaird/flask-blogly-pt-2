"""Blogly application."""

from flask import Flask, render_template, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'echnidna_eggs'
debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def list_users():
    return redirect('/users')

@app.route('/users')
def display_users():
    users = User.query.all()
    return render_template('list.html', users=users, heading="All Users")

@app.route('/users/<int:id>')
def display_user(id):
    user = User.query.get(id)
    return render_template('user.html', user=user)

@app.route("/users/family/<last>")
def display_family(last):
    family = User.get_users_by_last_name(last)
    return render_template('list.html', users=family, heading=f'The {last} Family')

@app.route('/users/new')
def show_add_user_form():
    return render_template('new-user.html')

@app.route('/users/edit/<int:id>')
def show_edit_user_form(id):
    user = User.query.get(id)
    return render_template("edit-user.html", user=user)

@app.route('/users/change/<int:id>', methods=["POST"])
def change_user(id):
    changed_user = User.query.get(id)
    first = request.form['first']
    if first:
        changed_user.first = first
    last = request.form['last']
    if last:
        changed_user.last = last
    image_url = request.form["image_url"]
    if image_url:
        changed_user.image_url = image_url

    db.session.add(changed_user)
    db.session.commit()

    return redirect(f'/users/{changed_user.id}')

@app.route('/users/delete/<int:id>', methods=["POST"])
def delete_user(id):
    deleted_user = User.query.filter_by(id=id).delete()
    db.session.commit()

    return redirect('/users')
    
@app.route('/users/add', methods=["POST"])
def add_user():
    first = request.form['first']
    last = request.form["last"]
    image_url = request.form["image_url"]
    image_url = str(image_url) if image_url else None

    new_user = User(first=first, last=last, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()

    return redirect(f'/users/{new_user.id}')

@app.route('/users/<int:id>/posts/new')
def display_post_form(id):
    user = User.query.get(id)
    return render_template('post-form.html', user=user)

@app.route('/users/<int:id>/posts/new', methods=["POST"])
def add_post(id):
    title = request.form['title']
    content = request.form["content"]

    new_post = Post(title=title, content=content, user_id=id)
    db.session.add(new_post)
    db.session.commit()
    return redirect(f'/users/{id}')

@app.route('/posts/<int:post_id>')
def show_post(post_id):
    post = Post.query.get(post_id)
    return render_template("post.html", post=post, user=post.user)

@app.route('/posts/<int:post_id>/edit')
def display_edit_post_form(post_id):
    post = Post.query.get(post_id)

    return render_template('edit-post.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def edit_post(post_id):
    changed_post = Post.query.get(post_id)
    title = request.form['title']
    if title:
        changed_post.title = title
    content = request.form['content']
    if content:
        changed_post.content = content

    db.session.add(changed_post)
    db.session.commit()

    return redirect(f'/posts/{post_id}')

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    user_id = Post.query.get(post_id).user.id
    Post.query.filter_by(post_id=post_id).delete()
    db.session.commit()

    return redirect(f'/users/{user_id}')
