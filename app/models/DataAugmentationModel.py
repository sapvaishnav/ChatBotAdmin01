import datetime
import logging
import pymysql
from app.models.Database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)

class DataAugmentationModel:
    @staticmethod
    def get_all_documents(tenant_id) -> list:
        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM chatbot_documents WHERE del_flg = %s AND tenant_id = %s"
                cursor.execute(sql, (0, tenant_id))  # Only get non-deleted documents for the specific tenant
                result = cursor.fetchall()
                return [dict(row) for row in result]  # Convert to list of dictionaries
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return []  # Return empty list on failure
        except Exception as e:
            logging.error(f"Error occurred while fetching documents: {e}")
            return []  # Return empty list on failure
        finally:
            connection.close()

    @staticmethod
    def get_all_urls(tenant_id) -> list:
        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM chatbot_urls WHERE del_flg = %s AND tenant_id = %s"
                cursor.execute(sql, (0, tenant_id))  # Only get non-deleted URLs for the specific tenant
                result = cursor.fetchall()
                return [dict(row) for row in result]  # Convert to list of dictionaries
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return []  # Return empty list on failure
        except Exception as e:
            logging.error(f"Error occurred while fetching URLs: {e}")
            return []  # Return empty list on failure
        finally:
            connection.close()

    @staticmethod
    def get_all_db_connection(tenant_id):
        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM chatbot_database_connection WHERE del_flg = %s AND tenant_id = %s"
                cursor.execute(sql, (0, tenant_id))   
                result = cursor.fetchone()
                return result   
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return None  # Return None on failure
        except Exception as e:
            logging.error(f"Error occurred while fetching DB connections: {e}")
            return None  # Return None on failure
        finally:
            connection.close()
 
    @staticmethod
    def add_document(document_name: str, document_type: str, document_status: str, tenant_id: str) -> dict:
        created_at = datetime.datetime.now()
        del_flg = 0  # Default is not deleted

        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                # Check if the document already exists
                check_sql = """
                SELECT tenant_id FROM chatbot_documents 
                WHERE document_name = %s AND document_type = %s AND tenant_id = %s AND del_flg = %s
                """
                print(f"check_sql: {check_sql}")
                cursor.execute(check_sql, (document_name, document_type, tenant_id, del_flg))
                
                exists = cursor.fetchone()  
                print(f"exists: {exists}") 
                count = exists['tenant_id'] if exists else 0
                
                if exists:  
                    logging.info(f"Document '{document_name}' of type '{document_type}' already exists.")
                    return {'status': False, 'message': f'Document "{document_name}" already exists and was not uploaded.'}


                # Insert the new document
                insert_sql = """
                INSERT INTO chatbot_documents 
                (document_name, document_type, document_status, created_at, tenant_id, del_flg) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (document_name, document_type, document_status, created_at, tenant_id, del_flg))
            connection.commit()
            return {'success': True, 'message': f'Document "{document_name}" uploaded successfully.'}  # Return success message
     
        except Exception as e:
            logging.error(f"Error occurred while adding document: {str(e)}")
            return {'success': False, 'message': f'Error uploading document "{document_name}".'}  # Indicate failure
        finally:
            connection.close()  # Ensure the connection is closed

    @staticmethod
    def delete_document (document_id:int, tenant_id:int) -> bool:
        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE chatbot_documents SET del_flg = %s WHERE doc_id = %s and tenant_id = %s"
                cursor.execute(sql, (1, document_id,tenant_id))  # Set del_flg to 1 for deletion
            connection.commit()
            return True  # Indicate successful deletion
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return False  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while deleting document: {e}")
            return False  # Indicate failure
        finally:
            connection.close()

    def add_url_if_not_exists(url_link: str, url_status: str, tenant_id: str) -> dict:
        created_at = datetime.datetime.now()
        del_flg = 0  # Default is not deleted

        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                # Check if the URL already exists
                select_sql = """
                SELECT url_id FROM chatbot_urls 
                WHERE url_link = %s AND tenant_id = %s AND del_flg = 0
                """
                cursor.execute(select_sql, (url_link, tenant_id))
                result = cursor.fetchone()

                if result:
                    # URL already exists, do not insert
                    logging.info(f"URL already exists: {url_link}")
                    return {'success': False, 'message': f'URL already exists:"{url_link}".'}
                     
                else:
                    # URL does not exist, perform insert
                    insert_sql = """
                    INSERT INTO chatbot_urls 
                    (url_link, url_status, created_at,updated_at, tenant_id, del_flg) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (url_link, url_status, created_at,created_at, tenant_id, del_flg))
                    connection.commit()
                    logging.info(f'URL "{url_link}" added successfully.')
                    return {'success': True, 'message': f'URL "{url_link}" added successfully.'}

        except Exception as e:
            logging.error(f"Error occurred while adding URL: {e}")
            return {'success': False, 'message': f'Error adding URL "{url_link}".'}
        finally:
            connection.close()

    @staticmethod
    def delete_url(url_id:int, tenant_id:int) -> bool:
        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE chatbot_urls SET del_flg = %s WHERE url_id = %s and tenant_id = %s"
                cursor.execute(sql, (1, url_id,tenant_id))  # Set del_flg to 1 for deletion
            connection.commit()
            return True  # Indicate successful deletion
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return False  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while deleting URL: {e}")
            return False  # Indicate failure
        finally:
            connection.close()

    @staticmethod
    def upsert_db_connection(hostname: str, databasename: str, username: str, 
                            password: str, db_status: str, tenant_id: int, port: str = None) -> str:
        db = Database()
        connection = db.get_connection()
        print(f"hostname  {hostname}  databasename {databasename}   username {username}   db_status  {db_status}   tenant_id {str(tenant_id)}  port {port}")
        try:
            with connection.cursor() as cursor:
                # Check if the record exists based on hostname and tenant_id
                select_sql = """
                SELECT * FROM chatbot_database_connection 
                WHERE   tenant_id = %s AND del_flg = 0
                """
                print(f"select_sql   {select_sql}")
                cursor.execute(select_sql, ( tenant_id))
                result = cursor.fetchone()
                print(f"result   {result}")
                if result:
                    # Record exists, perform update
                     
                    created_at = datetime.datetime.now()
                    update_sql = """
                    UPDATE chatbot_database_connection 
                    SET hostname= %s,   databasename = %s, username = %s, password = %s, db_status = %s, port = %s, created_at = %s
                    WHERE tenant_id = %s
                    """
                    print(f"update_sql   {update_sql}")
                    cursor.execute(update_sql, (hostname,databasename, username, password, db_status, port, created_at, tenant_id))
                    connection.commit()
                    return tenant_id  
                else:
                    # Record does not exist, perform insert
                    created_at = datetime.datetime.now()
                    del_flg = 0  # Default is not deleted
                    insert_sql = """
                    INSERT INTO chatbot_database_connection 
                    (hostname, databasename, username, password, created_at, db_status, tenant_id, del_flg, port) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    print(f"insert_sql   {insert_sql}")
                    cursor.execute(insert_sql, (hostname, databasename, username, password, created_at, db_status, tenant_id, del_flg, port))
                    connection.commit()
                    return cursor.lastrowid  # Return the last inserted connection ID

        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return None  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred during DB connection upsert: {e}")
            return None  # Indicate failure
        finally:
            connection.close()


    @staticmethod
    def delete_db_connection(tenant_id: str) -> bool:
        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE chatbot_database_connection SET del_flg = %s WHERE tenant_id = %s"
                cursor.execute(sql, (1, tenant_id))  # Set del_flg to 1 for deletion
            connection.commit()
            return True  # Indicate successful deletion
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return False  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while deleting DB connection: {e}")
            return False  # Indicate failure
        finally:
            connection.close()
