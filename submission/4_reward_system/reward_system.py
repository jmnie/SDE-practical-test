import pymysql
from decimal import Decimal, InvalidOperation
import datetime
import os 
from dotenv import load_dotenv
import logging 
# load the configuration in .env file 
load_dotenv(".env")

# using os to load the environment variables
db_config = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE'),
    'charset': os.getenv('DB_CHARSET')
}
def get_db_connection():
    connection = pymysql.connect(
        host=db_config['host'],
        port=int(db_config['port']),
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        charset=db_config['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# get order details
def get_order_details(order_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM orders WHERE order_id = %s"
            cursor.execute(sql, (order_id,))
            order = cursor.fetchone()
        logging.info(f"[Reward Service]: Retrieved order from id:{order_id}")
        return order
    except Exception as e:
        logging.error(f"[Reward Service]: Retrieving order from id:{order_id} details met exception: {str(e)}")
        return None
    finally:
        connection.close()

# insert reward points intp the table
def insert_reward_points(customer_id, points, expiry_date):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO reward_points (customer_id, points, expiry_date, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            """
            cursor.execute(sql, (customer_id, points, expiry_date))
        connection.commit()
        logging.info(f"[Reward Service]: Inserted reward points for customer_id:{customer_id}")
    except Exception as e:
        logging.error(f"[Reward Service]: Inserting reward points for customer_id:{customer_id} met exception: {str(e)}")
        connection.rollback()
    finally:
        connection.close()

# fetech the avaiable reward points
def get_available_points(customer_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            SELECT SUM(points) as total_points
            FROM reward_points
            WHERE customer_id = %s AND expiry_date > NOW()
            """
            cursor.execute(sql, (customer_id,))
            result = cursor.fetchone()
            return result['total_points'] if result['total_points'] else 0
    except Exception as e:
        logging.error(f"[Reward Service]: Fetching available reward points for customer_id:{customer_id} met exception: {str(e)}")
        return 0
    finally:
        connection.close()

# decuct points 
def deduct_points(customer_id, points_to_deduct):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # get remaining reward points
            sql_select = """
            SELECT point_id, points
            FROM reward_points
            WHERE customer_id = %s AND expiry_date > NOW() AND points > 0
            ORDER BY expiry_date ASC
            """
            cursor.execute(sql_select, (customer_id,))
            records = cursor.fetchall()
            
            remaining_points = points_to_deduct
            for record in records:
                if remaining_points <= 0:
                    break
                point_id = record['point_id']
                available_points = record['points']
                if available_points <= remaining_points:
                    # deduct points 
                    sql_update = "UPDATE reward_points SET points = 0 WHERE point_id = %s"
                    cursor.execute(sql_update, (point_id,))
                    remaining_points -= available_points
                    logging.info(f"[Reward Service]: customer_id:{customer_id}, deducted points: {available_points} remaining points: {remaining_points}")
                else:
                    # deduct points
                    sql_update = "UPDATE reward_points SET points = points - %s WHERE point_id = %s"
                    cursor.execute(sql_update, (remaining_points, point_id))
                    remaining_points = 0
        connection.commit()
    except Exception as e:
        logging.error(f"[Reward Service]: Deducting reward points for customer_id:{customer_id} met exception: {str(e)}")
        connection.rollback()
    finally:
        connection.close()

def get_exchange_rate_from_api():
    pass 

# convert currency 
def convert_to_usd(amount, currency):
    """
    exchange_rates = {
        'EUR': 1.1,  # 1 EUR = 1.1 USD
        'GBP': 1.3,  # 1 GBP = 1.3 USD
        # 
    }
    """
    exchange_rates = get_exchange_rate_from_api()
    if currency in exchange_rates:
        return amount * Decimal(exchange_rates[currency])
    else:
        raise ValueError(f"Unsupported ：{currency}")

# calcualte reward point
def credit_reward_points(order_id):
    """
    Calculate and credit reward points to a user's account.

    :param order_id: The unique identifier of the order
    :raises ValueError: If the order does not exist or is not in the 'Delivered' status
    :raises Exception: If an unexpected error occurs
    """
    try:
        # Retrieve order details
        order = get_order_details(order_id)
        if not order:
            logging.error(f"Order ID {order_id} does not exist.")
            raise ValueError(f"Order ID {order_id} does not exist.")
        
        # Check if the order is in the 'Delivered' status
        if order['status'] != 'Delivered':
            logging.error(f"[Reward Service]: Order ID {order_id} is not in 'Delivered' status.")
            raise ValueError(f"[Reward Service]: Order ID {order_id} is not in 'Delivered' status.")
        
        # Extract customer ID and order amount
        customer_id = order['customer_id']
        amount = Decimal(order['amount'])
        currency = order['currency']
        logging.info(f"[Reward Service]: Processing order ID {order_id} for customer ID {customer_id} with amount {amount} {currency}.")
        
        # Convert the order amount to USD if it is not already in USD
        if currency != 'USD':
            amount = convert_to_usd(amount, currency)
            logging.info(f"[Reward Service]: Converted amount to USD: {amount}.")

        # Calculate reward points (1 USD = 1 point)
        points = int(amount)
        logging.info(f"[Reward Service]: Calculated reward points: {points}.")

        # Set the expiry date for the reward points (1 year from today)
        expiry_date = datetime.date.today() + datetime.timedelta(days=365)
        logging.info(f"[Reward Service]: Reward points expiry date: {expiry_date}.")

        # Insert the reward points into the database
        insert_reward_points(customer_id, points, expiry_date)
        logging.info(f"[Reward Service]: Successfully credited {points} reward points to customer ID {customer_id}.")

    except Exception as e:
        # Log and raise unexpected errors
        logging.error(f"[Reward Service]: Unexpected error processing order ID {order_id}: {e}")
        raise