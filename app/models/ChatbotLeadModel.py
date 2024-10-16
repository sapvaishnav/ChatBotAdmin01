import datetime
import logging
import pymysql
from app.models.Database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)

class ChatbotLeadModel:
    @staticmethod
    def add_lead(username: str, email: str, phone_number: str, 
                 tenant_id: int, all_http_details: dict, 
                 last_active: datetime.datetime = None) -> int:
        created_at = datetime.datetime.now()
        updated_at = created_at  # Set initial update time
        del_flg = 0  # Assuming default is not deleted

        db = Database()
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO chatbot_lead 
                (username, email, phone_number, last_active, created_at, updated_at, 
                 tenant_id, del_flg, all_http_details)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    username, email, phone_number, last_active, created_at, 
                    updated_at, tenant_id, del_flg, all_http_details
                ))
            connection.commit()

            # Return the lead ID of the newly created lead
            return cursor.lastrowid  # This returns the last inserted ID
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return None  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while adding lead: {e}")
            return None  # Indicate failure
        finally:
            connection.close()

 
    @staticmethod
    def get_all_leads(tenant_id: int):
        db = Database()  # Assuming Database is a defined class managing connections
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
            SELECT  
    c.conversation_id, 
    c.chat_summary, 
    c.started_at, 
    c.ended_at, 
    c.transferred_at, 
    c.agent_id, 
    l.user_id, 
    l.username, 
    l.email, 
    l.phone_number, 
    l.ip,
    CONCAT(DATE(l.last_active), ' ', CONCAT(LPAD(HOUR(l.last_active), 2, '0'), ':', LPAD(SECOND(l.last_active), 2, '0'))) AS last_active_combined
FROM 
    chatbot_lead l
LEFT JOIN 
    db_ai_chatbot.chatbot_conversation c ON l.user_id = c.user_id 
WHERE 
    l.del_flg = 0 AND l.tenant_id = %s;

            """
              
               
                cursor.execute(sql, (tenant_id,))
                leads = cursor.fetchall()
                
                # Debug: Log the number of leads retrieved
                logging.debug(f"Number of leads retrieved: {len(leads)}")
                
                return leads  # Return lead information
        except pymysql.MySQLError as e:
            logging.error(f"MySQL Error: {e}")
            return None  # Indicate failure
        except Exception as e:
            logging.error(f"Error occurred while getting leads: {e}")
            return None  # Indicate failure
        finally:
            connection.close()  # Ensure connection is closed

