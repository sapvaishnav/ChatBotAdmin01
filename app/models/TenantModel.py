import datetime
import random
import string
import logging
from app.models.Database import Database
import pymysql

# Configure logging
logging.basicConfig(level=logging.INFO)

class TenantModel:
    @staticmethod
    def generate_tenant_key(length=16):
        """Generate a random alphanumeric tenant key."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=length))

    @staticmethod
    def add_tenant(tenant_name: str, tenant_address: str, tenant_emailid: str, 
                   tenant_contact: str, tenant_city: str = None, 
                   tenant_country: str = None, tenant_postcode: str = None, 
                   tenant_GSTNNo: str = None, tenant_PAN: str = None) -> int:
        tenant_key = TenantModel.generate_tenant_key()  # Generate dynamic tenant key
        created_at = datetime.datetime.now()
        updated_at = created_at  # Set initial update time
        tenant_emailid_verify = 0  # Assuming default is not verified
        del_flg = 0  # Assuming default is not deleted

        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO chatbot_tenants 
                (tenant_name, tenant_key, tenant_address, tenant_emailid, tenant_contact,
                 tenant_city, tenant_country, tenant_postcode, tenant_GSTNNo, tenant_PAN,
                 created_at, updated_at, tenant_emailid_verify, del_flg)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    tenant_name, tenant_key, tenant_address, tenant_emailid, tenant_contact,
                    tenant_city, tenant_country, tenant_postcode, tenant_GSTNNo, tenant_PAN,
                    created_at, updated_at, tenant_emailid_verify, del_flg
                ))
            connection.commit()

            # Return the tenant ID of the newly created tenant
            return cursor.lastrowid  # This returns the last inserted ID
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return None  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while adding tenant: {e}")
            return None  # Indicate failure
        finally:
            connection.close()

    @staticmethod
    def update_tenant(tenant_id: int, tenant_name: str = None, 
                      tenant_address: str = None, tenant_emailid: str = None, 
                      tenant_contact: str = None, tenant_city: str = None,
                      tenant_country: str = None, tenant_postcode: str = None, 
                      tenant_GSTNNo: str = None, tenant_PAN: str = None) -> bool:
        updated_at = datetime.datetime.now()  # Update timestamp

        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE chatbot_tenants SET updated_at = %s"
                params = [updated_at]

                if tenant_name is not None:
                    sql += ", tenant_name = %s"
                    params.append(tenant_name)
                if tenant_address is not None:
                    sql += ", tenant_address = %s"
                    params.append(tenant_address)
                if tenant_emailid is not None:
                    sql += ", tenant_emailid = %s"
                    params.append(tenant_emailid)
                if tenant_contact is not None:
                    sql += ", tenant_contact = %s"
                    params.append(tenant_contact)
                if tenant_city is not None:
                    sql += ", tenant_city = %s"
                    params.append(tenant_city)
                if tenant_country is not None:
                    sql += ", tenant_country = %s"
                    params.append(tenant_country)
                if tenant_postcode is not None:
                    sql += ", tenant_postcode = %s"
                    params.append(tenant_postcode)
                if tenant_GSTNNo is not None:
                    sql += ", tenant_GSTNNo = %s"
                    params.append(tenant_GSTNNo)
                if tenant_PAN is not None:
                    sql += ", tenant_PAN = %s"
                    params.append(tenant_PAN)

                sql += " WHERE tenant_id = %s"
                params.append(tenant_id)
                print(f"SQL =  {sql}")
                cursor.execute(sql, params)
            connection.commit()
            return True  # Indicate successful update
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return False  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while updating tenant: {e}")
            return False  # Indicate failure
        finally:
            connection.close()

    @staticmethod
    def get_tenant(tenant_id: int):
        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT tenant_id, tenant_name, tenant_key, tenant_address, 
                       tenant_emailid, tenant_contact, created_at, 
                       updated_at, tenant_emailid_verify, tenant_GSTNNo, 
                       tenant_PAN, del_flg, tenant_city, 
                       tenant_country, tenant_postcode
                FROM chatbot_tenants
                WHERE del_flg=0 and tenant_id = %s
                """
                cursor.execute(sql, (tenant_id,))
                tenant = cursor.fetchone()
                return tenant  # Return tenant information
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return None  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while getting tenant: {e}")
            return None  # Indicate failure
        finally:
            connection.close()
