"""Blogly application."""

from flask import Flask, render_template, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, PostTag, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'folke'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def home_page():

    return redirect('/users') 

@app.route('/users')
def user_list():
    """Shows list of users in db"""
    users = User.query.all()
    posts = Post.query.all()
    return render_template('index.html', users=users)

@app.route('/users/new')
def show_add_user():
    return render_template('users/add.html')


@app.route('/users/new', methods=['POST'])
def add_user():
    """Add a user"""

    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    image_url = request.form.get('image_url', None)

    user = User(first_name=first_name, last_name=last_name, image_url=image_url)

    db.session.add(user)
    db.session.commit()
    return redirect('/users')

@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    """Show details about individual users"""

    user = User.query.get_or_404(user_id)
    posts = Post.query.filter(Post.author_id == user_id).all()
    return render_template('/users/user.html', user=user, posts=posts)

@app.route('/users/<int:user_id>/edit')
def show_edit_user_details(user_id):
    """Edit user details"""

    user = User.query.get_or_404(user_id)

    return render_template('/users/edit.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def edit_user_details(user_id):
    """Edit user details"""

    user = User.query.get(user_id)

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    image_url = request.form['image_url']

    if user.first_name != first_name:
        user.first_name = first_name
    
    if user.last_name != last_name:
        user.last_name = last_name

    if user.image_url != image_url:
        user.image_url = image_url    

    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete user"""

    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>/posts/new')
def show_new_post_form(user_id):
    """Show new post form"""

    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    return render_template('posts/new.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def add_new_post(user_id):
    """Add a new blog post"""

    title = request.form.get('title')
    content = request.form.get('content')
    tags = request.form.getlist('tags')

    # Create a list with PostTags from selected tags

    tag_list = [PostTag(tag_id=tag_id) for tag_id in tags]

    post = Post(title=title, content=content, author_id=user_id, tags=tag_list)
    
    db.session.add(post)
    db.session.commit()

    return redirect(f'/users/{user_id}')

@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """ Show blog post """

    post = Post.query.get_or_404(post_id)
    tags = post.tags

    return render_template('posts/post.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=['POST', 'GET'])
def edit_post(post_id):

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    tag_ids = post.tag_ids

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.getlist('tags')
        
        tag_list = [PostTag(post_id=post_id, tag_id=tag_id) for tag_id in tags]

        post.title = title
        post.content = content
        PostTag.query.filter_by(post_id=post_id).delete()
        db.session.commit()
        post.tags = tag_list
        db.session.commit()

        return redirect(f'/posts/{post_id}')
    else: 
        return render_template('/posts/edit.html', post=post, tags=tags, tag_ids=tag_ids)

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Delete user"""

    post = Post.query.get_or_404(post_id)
    print(post_id)
    
    PostTag.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()

    return redirect(f'/users')

@app.route('/tags')
def show_tags():
    """Show tags"""

    tags = Tag.query.all()

    return render_template('tags/tags.html', tags=tags)

@app.route('/tags/<int:tag_id>')
def show_tag(tag_id):
    """Show specific tag and its posts"""

    tag = Tag.query.get_or_404(tag_id)
    posts = tag.posts

    return render_template('tags/tag.html', tag=tag, posts=posts)

@app.route('/tags/new', methods=['POST', 'GET'])
def add_tag():
    """Add a tag"""
    if request.method == 'POST':
        name = request.form.get('name')
        print('tag name', name)
        tag = Tag(name=name)

        db.session.add(tag)
        db.session.commit()

        return redirect('/tags')

    return render_template('tags/new.html')

@app.route('/tags/<int:tag_id>/edit', methods=['POST', 'GET'])
def edit_tag(tag_id):
    tag = Tag.query.get(tag_id)

    if request.method == 'POST':
        name = request.form.get('name')

        tag.name = name
        db.session.commit()
        print('YES!')

        return redirect(f'/tags/{tag_id}')

    return render_template('tags/edit.html', tag=tag)