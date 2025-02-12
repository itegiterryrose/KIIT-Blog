from flask import Flask, request, render_template, redirect, url_for,abort
import sqlite3

app = Flask(__name__)

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
@app.route('/add', methods=['GET', 'POST'])
def add_blog_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_url = request.form['image_url']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO blog_posts (title, content, image_url) VALUES (?, ?, ?)",
                       (title, content, image_url))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))  # Redirect to homepage after adding post

    return render_template('add_post.html')  # Render the form

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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blog_posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('home'))  # Redirect to homepage after deleting

if __name__ == '__main__':
    app.run(debug=True)
