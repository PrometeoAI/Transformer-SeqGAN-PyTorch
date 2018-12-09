#import the Flask class from the flask module
from flask import Flask, render_template, request

# create the application object
app = Flask(__name__)

# use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods = ['POST'])
def generate_output():
    sentence = request.form['email']
    print("$"*80,sentence)
    

# @app.route('/welcome')
# def welcome():
#     return render_template('welcome.html')  # render a template

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)