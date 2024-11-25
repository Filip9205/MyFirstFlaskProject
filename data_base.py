import sqlite3  # Importing the SQLite3 library to interact with the SQLite database.


# A class to handle database operations.
class DataBase:
    # Constructor to initialize the database connection and cursor.
    def __init__(self):
        # Connecting to the SQLite database (creates the file if it doesn't exist).
        self.data = sqlite3.connect("users_vouchers.db", check_same_thread=False)
        self.cursor = self.data.cursor()  # Cursor object to execute SQL queries.

    # Method to retrieve all user information.
    def all_users(self):
        # Fetching all user details (user_id, name, email, age) from the user_info table.
        all_users = self.cursor.execute("""
                            SELECT user_id, name, email, age
                            FROM user_info
                            """).fetchall()
        return all_users  # Returning the list of users.

    # Method to get detailed information about a specific user by their ID.
    def user_info_by_id(self, user_id):
        # Query to fetch user details for a specific user ID.
        user = self.cursor.execute("""
                              SELECT ui.user_id, ui.name, ui.email, ui.age
                              FROM user_info as ui
                              WHERE ui.user_id =?
                              """, [user_id]).fetchone()
        try:
            return user  # Return the user details if found.
        except TypeError:
            return False  # Return False if no user is found.

    # Method to get total spending details of a user by their ID.
    def total_spend_by_user_id(self, user_id):
        # Query to join user_info and user_spending tables to fetch spending details.
        user = self.cursor.execute("""
            SELECT ui.user_id, ui.name, ui.email, ui.age, us.money_spent, year
            FROM user_info as ui
            JOIN user_spending as us ON ui.user_id = us.user_id
            WHERE ui.user_id = ?""", [user_id]).fetchall()

        try:
            # Extracting money spent details and creating a dictionary of user data.
            money_spent = [total[4] for total in user]
            user_dic = {
                "id": user[0][0],  # User ID
                "name": user[0][1],  # User name
                "mail": user[0][2],  # User email
                "age": user[0][3],  # User age
                "money_spent": money_spent,  # List of money spent
                "year": user[0][5],  # Year of spending
                "total_money_spent": round(sum(money_spent), 2)  # Total spending
            }
            return user_dic
        except IndexError:
            return False  # Return False if user spending data is not found.

    # Method to calculate average spending based on age groups.
    def avg_spend(self):
        data = self.cursor.execute(f"""
            SELECT
                CASE
                    WHEN age BETWEEN 18 AND 24 THEN '18-24'
                    WHEN age BETWEEN 25 AND 30 THEN '25-30'
                    WHEN age BETWEEN 31 AND 36 THEN '31-36'
                    WHEN age BETWEEN 37 AND 47 THEN '37-47'
                    WHEN age >= 48 THEN '47+'
                END AS age_group, 
                AVG(money_spent) AS avg_money_spent
            FROM user_info ui
            JOIN user_spending us ON ui.user_id = us.user_id
            GROUP BY age_group 
            ORDER BY age_group;
        """).fetchall()
        return data

    # Method to get a list of high spenders.
    def get_high_spenders(self):
        data = self.cursor.execute("""
            SELECT user_id, total_spending
            FROM high_spenders""").fetchall()
        return data  # Returning the list of high spenders.

    # Method to add a new high spender to the database.
    def add_new_high_spender(self, id, total_spent):
        # Inserting the user ID and total spending into the high_spenders table.
        self.cursor.execute("""
            INSERT INTO high_spenders (user_id, total_spending)
            VALUES (?, ?)""", (id, total_spent))
        self.data.commit()  # Committing the transaction to save changes.


# A class to structure user data.
class UsersData:
    # Constructor to initialize user attributes using keyword arguments.
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")  # User ID
        self.name = kwargs.get("name")  # User name
        self.mail = kwargs.get("mail")  # User email
        self.age = kwargs.get("age")  # User age
        try:
            # Rounding off the average spending value.
            self.average = round(kwargs.get("average"), 2)
        except TypeError:
            pass  # Skip if the average is not provided or invalid.
