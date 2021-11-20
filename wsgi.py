import os
from app import app
from dotenv import load_dotenv
load_dotenv()

DEBUG = os.environ.get("FLASK_ENV") == 'development'

if __name__ == '__main__':
    app.run(debug=DEBUG,host='0.0.0.0',port=80)