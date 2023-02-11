APP_NAME = 'MySQLBackUp'
APP_PATH = '/PYTHON/' + APP_NAME
APP_LOG_PATH = APP_PATH + '/logs/debug.log'

GOOGLE_DRIVE_TOKEN_PATH = APP_PATH + '/input/GoogleDrive/token.json'
GOOGLE_DRIVE_CREDENTIAL_PATH = APP_PATH + '/input/GoogleDrive/credentials.json'

DB_HOST = '127.0.0.1'
DB_USER = ''
DB_PASSWORD = ''
DB_DATABASE = ''

GOOGLE_DRIVE_ROOT_ID = 'TODO'

SENDER_EMAIL = 'TODO'
SENDER_EMAIL_PASSWORD = 'TODO'
SMTP_SERVER = 'TODO'
RECEIVER_EMAIL = 'TODO'

DATABASE_TO_EXCLUDE = [
    'information_schema',
    'mysql',
    'performance_schema',
    'sys',
]
