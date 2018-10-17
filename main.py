""" 
For /login page:

User enters a username that is stored in the database with the correct password and is redirected to 
the /newpost page with their username being stored in a session. X

User enters a username that is stored in the database with an incorrect password and is redirected 
to the /login page with a message that their password is incorrect. X

User tries to login with a username that is not stored in the database and is redirected to the 
/login page with a message that this username does not exist. X

User does not have an account and clicks "Create Account" and is directed to the /signup page. X

=====================================================================================================

For /signup page:

User enters new, valid username, a valid password, and verifies password correctly and is redirected 
to the '/newpost' page with their username being stored in a session. x

User leaves any of the username, password, or verify fields blank and gets an error message that one 
or more fields are invalid. X

User enters a username that already exists and gets an error message that username already exists. X

User enters different strings into the password and verify fields and gets an error message that the 
passwords do not match. X

User enters a password or username less than 3 characters long and gets either an invalid username 
or an invalid password message. X

=====================================================================================================

Functionality Check:

User is logged in and adds a new blog post, then is redirected to a page featuring the individual 
blog entry they just created (as in Build-a-Blog). X

User visits the /blog page and sees a list of all blog entries by all users. X

User clicks on the title of a blog entry on the /blog page and lands on the individual blog entry page. X

User clicks "Logout" and is redirected to the /blog page and is unable to access the /newpost page 
(is redirected to /login page instead) X

========================================================================================================

Create Dynamic User Pages:

User is on the / page ("Home" page) and clicks on an author's username in the list and lands on the 
individual blog user's page. X

User is on the /blog page and clicks on the author's username in the tagline and lands on the 
individual blog user's page. X

User is on the individual entry page (e.g., /blog?id=1) and clicks on the author's username in
the tagline and lands on the individual blog user's page X

"""


from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


db_name = 'blogs'
db_user = 'blogs'
db_pass = 'withoutaz'
db_server = 'localhost'
db_port = '8889'

app = Flask(__name__)
app.config['DEBUG'] = True      
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+db_user+':'+db_pass+'@'+db_server+':'+db_port+'/'+db_name
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'hellofriend'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['index', 'login', 'signup', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login') 

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', page_title= 'Blogz', users=users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/blog/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    return render_template('login.html')
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already in use', 'error')
        elif len(username) < 3 or len(password) < 3:
            flash('Invalid username or invalid password')
        elif password != verify:
            flash('Passwords do not match', 'error')
        elif not existing_user and password == verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog/newpost')
        
    return render_template('signup.html', username = username)
@app.route('/logout')
def logout():
    del session['username']
    flash('Logged out')
    return redirect('/blog')

@app.route('/blog/newpost', methods=['POST', 'GET'])
def newpost():
    title = ""
    title_error = ""
    body = ""
    body_error = ""
    owner = User.query.filter_by(username = session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not len(title) > 0:
            title_error = "Title must contain a value"
            
        if not len(body) > 0:
            body_error = "Body must contian a value"
         
        if not(title_error) and not(body_error):
            new_post = Blog(title = title, body = body, owner = owner )
            db.session.add(new_post)
            db.session.commit()
            db.session.refresh(new_post)
            return redirect('/blog?id='+ str(new_post.id))            
    
    return render_template('newpost.html', page_title = "Add A Post", title = title, 
        title_error = title_error, body = body, body_error = body_error) 

@app.route('/blog', methods=['GET'])
def blog():
    blogs = []
    view = 'default'
    if request.args:
        id = request.args.get('id')
        username = request.args.get('user')
        if id:
            blogs.append(Blog.query.get(id))
            view = 'single'
        elif username:
            owner = User.query.filter_by(username = username).first()
            blogs = Blog.query.filter_by(owner = owner).all()
    else:
        blogs = Blog.query.all()
    return render_template('blog.html', page_title='Blogz', blogs=blogs,view=view)

if __name__ == '__main__':
    app.run()