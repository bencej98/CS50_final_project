from flask import Flask

# Configure application
app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD']=True
@app.route('/')

