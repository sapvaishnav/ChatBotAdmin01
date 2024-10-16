import pymysql
from decouple import config
import hashlib

class Database:
    def __init__(self):
        self.host ="localhost" #config('DBHOST', default='localhost')
        self.user = "root" #config('MYSQL_USER', default='root')
        self.password ="ZAQ!xsw2CDE#" # config('MYSQL_PASS', default='ZAQ!xsw2CDE#')
        self.database = "db_ai_chatbot" #config('MYSQL_DB_NAME', default='db_ai_chatbot')

    def get_connection(self):
        """Establish and return a new database connection."""
        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except pymysql.MySQLError as e:
            print(f"Error connecting to the database: {e}")
            return None

class PasswordHasher:
    @staticmethod
    def hash_password(password):
        """Return a hashed version of the password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password, hashed_password):
        """Verify the provided password against the hashed password."""
        return PasswordHasher.hash_password(password) == hashed_password
