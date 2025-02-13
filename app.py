from flask import Flask, request, render_template, redirect, url_for, abort, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Hardcoded admin credentials
ADMIN_USERNAME = "Kingori"
ADMIN_PASSWORD = "nice"

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

# Create table if it doesn't exist
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS blog_posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        image_url TEXT NOT NULL)''')
    conn.commit()
    conn.close()

create_table()  # Call this once when the app starts

# Route to display all blog posts
@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blog_posts ORDER BY id DESC")
    posts = cursor.fetchall()
    conn.close()
    return render_template('home.html', posts=posts)

# Route to add a new blog post

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if 'username' not in request.form or 'password' not in request.form:
            flash("Missing username or password.", "danger")
            return redirect(url_for('admin_login'))

        username = request.form.get('username')  # Using `.get()` prevents KeyError
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            flash("Login successful!", "success")
            return redirect(url_for('add_post'))
        else:
            flash("Invalid credentials!", "danger")
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if not session.get('admin'):
        flash("You must be an admin to add posts!", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_url = request.form['image_url']  # Ensure this is provided

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO blog_posts (title, content, image_url) VALUES (?, ?, ?)",
            (title, content, image_url),
        )
        conn.commit()
        conn.close()
        flash("Post added successfully!", "success")
        return redirect(url_for('home'))

    return render_template('add_post.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)  # Remove admin session
    flash("Logged out successfully.", "info")
    return redirect(url_for('home'))

@app.route('/post/<int:post_id>')
def get_blog_post(post_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # Allows accessing columns as dict keys
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blog_posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    conn.close()

    if post is None:
        abort(404)  # Show 404 error if post is not found

    print(dict(post))  # Debugging: Print the post data in the terminal
    return render_template('post.html', post=post)


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    # Check if admin is logged in
    if not session.get('admin'):
        flash("You must be an admin to delete posts!", "danger")
        return redirect(url_for('home'))  

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blog_posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    
    flash("Post deleted successfully!", "success")
    return redirect(url_for('home'))
  # Redirect to homepage after deleting

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'admin' not in session or not session['admin']:
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch post details
    cursor.execute("SELECT * FROM blog_posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    
    if not post:
        conn.close()
        flash("Post not found!", "danger")
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_url = request.form['image_url']

        if not title or not content:
            flash("Title and content cannot be empty!", "danger")
            return redirect(url_for('edit_post', post_id=post_id))

        # Update post
        cursor.execute("UPDATE blog_posts SET title = ?, content = ?, image_url = ? WHERE id = ?", 
                       (title, content, image_url, post_id))
        conn.commit()
        conn.close()
        
        flash("Post updated successfully!", "success")
        return redirect(url_for('home'))
    
    conn.close()
    return render_template('edit_post.html', post=post)

if __name__ == '__main__':
    app.run(debug=True)
