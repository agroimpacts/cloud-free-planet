from MappingCommon import MappingCommon

mapc = MappingCommon()
params = mapc.parseYaml("config.yaml")

# *****************************
# Environment specific settings
# *****************************

# DO NOT use "DEBUG = True" in production environments
DEBUG = params['mapper']['DEBUG']

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
SECRET_KEY = params['mapper']['SECRET_KEY']

# SQLAlchemy settings
db_production_name = params['mapper']['db_production_name']
db_name = params['mapper']['db_sandbox_name']
db_user = params['mapper']['db_username']
db_password = params['mapper']['db_password']
db_url= params['mapper']['db_url']
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=db_user,pw=db_password,url=db_url,db=db_name)
SQLALCHEMY_DATABASE_URI = DB_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids a SQLAlchemy Warning

# Flask-Mail settings
# For smtp.gmail.com to work, you MUST set "Allow less secure apps" to ON in Google Accounts.
# Change it in https://myaccount.google.com/security#connectedapps (near the bottom).
MAIL_SERVER = params['mapper']['MAIL_SERVER']
MAIL_PORT = params['mapper']['MAIL_PORT']
MAIL_USE_SSL = params['mapper']['MAIL_USE_SSL']
MAIL_USE_TLS = params['mapper']['MAIL_USE_TLS']
MAIL_USERNAME = params['mapper']['MAIL_USERNAME']
MAIL_PASSWORD = params['mapper']['MAIL_PASSWORD']

MAIL_DEFAULT_SENDER = '"AgroImpacts Administrator" <lestes@clarku.edu>'
ADMINS = [
    '"AgroImpacts Administrator" <lestes@clarku.edu>',
    ]
