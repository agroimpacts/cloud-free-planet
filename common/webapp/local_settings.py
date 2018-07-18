import os

# *****************************
# Environment specific settings
# *****************************

# DO NOT use "DEBUG = True" in production environments
DEBUG = True

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
SECRET_KEY = 'This is an UNSECURE Secret. CHANGE THIS for production environments.'

# SQLAlchemy settings
# *** TODO: TEMP definitions. Replace with central definitions. ***
db_name = 'AfricaSandbox'
db_user = '***REMOVED***'
db_password = '***REMOVED***'
db_url='127.0.0.1:5432'
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=db_user,pw=db_password,url=db_url,db=db_name)
SQLALCHEMY_DATABASE_URI = DB_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids a SQLAlchemy Warning

# Flask-Mail settings
# For smtp.gmail.com to work, you MUST set "Allow less secure apps" to ON in Google Accounts.
# Change it in https://myaccount.google.com/security#connectedapps (near the bottom).
MAIL_SERVER = 'smtp.cox.net'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False
MAIL_USERNAME = '***REMOVED***'
MAIL_PASSWORD = '***REMOVED***'
MAIL_DEFAULT_SENDER = '"AgroImpacts Administrator" <lestes@clarku.edu>'

ADMINS = [
    '"AgroImpacts Administrator" <dmcr@princeton.edu>',
    '"AgroImpacts Administrator" <lestes@clarku.edu>',
    ]
