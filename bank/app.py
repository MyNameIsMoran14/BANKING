from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/small_business')
def small_business():
    return render_template('small_business.html')

@app.route('/big_business')
def big_business():
    return render_template('big_business.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)