import logging
from app.models.Database import Database
import pymysql
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

class BotConfigurationModel:
    @staticmethod
    def get_configuration(tenant_id: int):
        """Retrieve the configuration for a given tenant."""
        connection = Database().get_connection()  # Use Database class for connection
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT config_id, tenant_id, model_name, model_key, creativity, threshold, 
                       bot_name, bot_avatar, bot_workspace, short_term_memory_length, 
                       max_matching_knowledge, greeting_message, static_message, 
                       integration_url, integration_script, created_at, updated_at, del_flg
                FROM chatbot_botconfig
                WHERE tenant_id = %s AND del_flg = 0
                """
                cursor.execute(sql, (tenant_id,))
                config = cursor.fetchone()  # Fetch one configuration record
                return config  # Return the configuration details as a tuple
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return None  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while retrieving configuration: {e}")
            return None  # Indicate failure
        finally:
            connection.close()

    @staticmethod
    def add_configuration(tenant_id: int, model_name: str, model_key: str, creativity: float, 
                          threshold: float, bot_name: str, bot_avatar: str, bot_workspace: str, 
                          short_term_memory_length: int, max_matching_knowledge: int, 
                          greeting_message: str, static_message: str, integration_url: str, 
                          integration_script: str):
        """Add a new bot configuration."""
        created_at = datetime.datetime.now()
        updated_at = created_at
        del_flg = 0  # Assuming new entries are not deleted

        connection = Database().get_connection()  # Use Database class for connection
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO db_ai_chatbot.chatbot_botconfig 
                (tenant_id, model_name, model_key, creativity, threshold, bot_name, bot_avatar, 
                 bot_workspace, short_term_memory_length, max_matching_knowledge, greeting_message, 
                 static_message, integration_url, integration_script, created_at, updated_at, del_flg)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    tenant_id, model_name, model_key, creativity, threshold, bot_name, bot_avatar, 
                    bot_workspace, short_term_memory_length, max_matching_knowledge, greeting_message, 
                    static_message, integration_url, integration_script, created_at, updated_at, del_flg
                ))
            connection.commit()

            # Return the ID of the newly created configuration
            return cursor.lastrowid
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return None  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while adding configuration: {e}")
            return None  # Indicate failure
        finally:
            connection.close()

    @staticmethod
    def update_configuration(tenant_id: int, model_name: str = None, model_key: str = None, creativity: float = None, 
                             threshold: float = None, bot_name: str = None, bot_avatar: str = None, 
                             bot_workspace: str = None, short_term_memory_length: int = None, 
                             max_matching_knowledge: int = None, greeting_message: str = None, 
                             static_message: str = None ) -> bool:
        """Update an existing bot configuration."""
        updated_at = datetime.datetime.now()

        connection = Database().get_connection()  # Use Database class for connection
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE db_ai_chatbot.chatbot_botconfig SET updated_at = %s"
                params = [updated_at]

                if model_name is not None:
                    sql += ", model_name = %s"
                    params.append(model_name)
                if model_key is not None:
                    sql += ", model_key = %s"
                    params.append(model_key)
                if creativity is not None:
                    sql += ", creativity = %s"
                    params.append(creativity)
                if threshold is not None:
                    sql += ", threshold = %s"
                    params.append(threshold)
                if bot_name is not None:
                    sql += ", bot_name = %s"
                    params.append(bot_name)
                if bot_avatar is not None:
                    sql += ", bot_avatar = %s"
                    params.append(bot_avatar)
                if bot_workspace is not None:
                    sql += ", bot_workspace = %s"
                    params.append(bot_workspace)
                if short_term_memory_length is not None:
                    sql += ", short_term_memory_length = %s"
                    params.append(short_term_memory_length)
                if max_matching_knowledge is not None:
                    sql += ", max_matching_knowledge = %s"
                    params.append(max_matching_knowledge)
                if greeting_message is not None:
                    sql += ", greeting_message = %s"
                    params.append(greeting_message)
                if static_message is not None:
                    sql += ", static_message = %s"
                    params.append(static_message)
               

                sql += " WHERE tenant_id = %s"
                params.append(tenant_id)

                cursor.execute(sql, params)
            connection.commit()
            return True  # Indicate successful update
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return False  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while updating configuration: {e}")
            return False  # Indicate failure
        finally:
            connection.close()

    @staticmethod
    def delete_configuration(config_id: int) -> bool:
        """Mark a configuration as deleted (soft delete)."""
        updated_at = datetime.datetime.now()
        del_flg = 1  # Soft delete

        connection = Database().get_connection()  # Use Database class for connection
        try:
            with connection.cursor() as cursor:
                sql = """
                UPDATE db_ai_chatbot.chatbot_botconfig 
                SET updated_at = %s, del_flg = %s 
                WHERE config_id = %s
                """
                cursor.execute(sql, (updated_at, del_flg, config_id))
            connection.commit()
            return True  # Indicate successful deletion
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return False  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while deleting configuration: {e}")
            return False  # Indicate failure
        finally:
            connection.close()
