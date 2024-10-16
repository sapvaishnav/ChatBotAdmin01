import datetime
import pymysql
import re
from app.models.Database import Database, PasswordHasher
from app.models.TenantModel import TenantModel
from flask import session
class UserModel:

    @staticmethod
    def validate_username(username):
        """
        Validate the username: 
        - Must not exceed 20 characters.
        - Must not contain spaces.
        """
        if len(username) > 20:
            return False  # Username too long
        if ' ' in username:
            return False  # Username contains spaces
        return True  # Username is valid

    @staticmethod
    def validate_password(password):
        """
        Validate the password:
        - Minimum 9 characters.
        - Must contain at least one uppercase letter, one lowercase letter, and one digit.
        """
        if len(password) < 9:
            return False  # Password too short
        if not re.search(r'[A-Z]', password):
            return False  # No uppercase letter
        if not re.search(r'[a-z]', password):
            return False  # No lowercase letter
        if not re.search(r'[0-9]', password):
            return False  # No digit
        return True  # Password is valid

    @staticmethod
    def user_exists(username, email):
        """
        Check if a user with the given username or email already exists.
        Returns True if the user exists, otherwise False.
        """
        db = Database()
        connection = db.get_connection()

        try:
            with connection.cursor() as cursor:
                sql = "SELECT login_id FROM chatbot_loginuser WHERE username = %s OR email = %s"
                cursor.execute(sql, (username, email))
                user = cursor.fetchone()
                return user is not None  # Returns True if user exists, False otherwise
        except pymysql.MySQLError as e:
            print(f"MySQL Error: {e}")
            return False  # Error occurred, assume user doesn't exist to avoid duplicate failure
        except Exception as e:
            print(f"Error occurred while checking user existence: {e}")
            return False
        finally:
            connection.close()

    @staticmethod
    def add_user(username, password, email):
        """
        Add a new user and associate the user with a tenant.
        - Validate the username and password.
        - Hash the password before storing it.
        - Create a new tenant associated with the user.
        """
        # Check if user already exists
        if UserModel.user_exists(username, email):
            print("User with this username or email already exists.")
            return None  # Indicate failure due to duplicate user

        # Validate username and password
        if not UserModel.validate_username(username):
            print("Invalid username. It should not contain spaces and must be less than 20 characters.")
            return None  # Username validation failed
        if not UserModel.validate_password(password):
            print("Invalid password. It must contain at least 1 uppercase letter, 1 lowercase letter, 1 digit, and be longer than 8 characters.")
            return None  # Password validation failed

        # Hash the password
        password_hash = PasswordHasher.hash_password(password)
        created_at = datetime.datetime.now()

        # Default tenant values
        tenant_name = username
        tenant_emailid = email

        # Add tenant and get tenant ID
        tenant_id = TenantModel.add_tenant(
            tenant_name=tenant_name,
            tenant_address="",
            tenant_emailid=tenant_emailid,
            tenant_contact="",
            tenant_city="",
            tenant_country="",
            tenant_postcode="",
            tenant_GSTNNo="",
            tenant_PAN=""
        )

        # If tenant creation failed, return None
        if tenant_id is None:
            print("Tenant creation failed.")
            return None  # Indicate failure in tenant creation

        # Establish database connection
        db = Database()
        connection = db.get_connection()

        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO chatbot_loginuser (username, password_hash, email, created_at, tenant_id, role)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (username, password_hash, email, created_at, tenant_id, "Admin"))
            connection.commit()
            return True  # User successfully added
        except pymysql.MySQLError as e:
            print(f"MySQL Error: {e}")
            return False  # Database operation failed
        except Exception as e:
            print(f"Error occurred while adding user: {e}")
            return False  # General error
        finally:
            connection.close()

    @staticmethod
    def verify_user(username, password):
        db = Database()
        connection = db.get_connection()

        try:
            with connection.cursor() as cursor:
                # Use parameterized queries to prevent SQL injection
                sql = "SELECT tenant_id,login_id,username, password_hash FROM chatbot_loginuser WHERE del_flg=0 and username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                print(f"user = {user}")

                if user is None:
                    return "Username does not exist"

                # Fetch the password hash from the tuple returned
                stored_password_hash = user['password_hash']
                # Verify the password hash
                if PasswordHasher.verify_password(password, stored_password_hash):
                    session['username'] = user['username']
                    session['login_id'] = user['login_id']
                    session['tenant_id'] = user['tenant_id']
                    
                    return True  # Successful verification
                else:
                    return "Invalid password"  # Password did not match

        except pymysql.MySQLError as e:
            print(f"MySQL Error: {e}")
            return f"Database error: {e}"
        except Exception as e:
            print(f"Unexpected error occurred while verifying user: {e}")
            return "Invalid Username or Password"
        finally:
            connection.close()
