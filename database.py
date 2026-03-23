import sqlite3

class DataBase:

    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None


    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON;")
        return self.connection
    
    
    def create_tables(self):
        self.connect()
        cursor = self.connection.cursor()

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories(
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL UNIQUE
                )""")
        
### here - done
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions(
                    t_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    t_date DATETIME,
                    amount_in_paise INTEGER NOT NULL,
                    t_type TEXT CHECK(t_type IN('cr', 'db')),
                    category_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id)
                )""")
        
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )""")   
        
        self.connection.commit()

# ----- users -----

    def add_user(self, username, email, password_hash):
        self.connect()
        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))
        
            self.connection.commit()
            return True 
    
        except sqlite3.IntegrityError:
            return False
            
    
    def get_user_by_username(self, username):
        self.connect()
        cursor = self.connection.cursor()

        cursor.execute(" SELECT * FROM users WHERE username = ? ", (username,))
        return cursor.fetchone()
    
    
    def get_user_by_id(self, user_id):
        self.connect()
        cursor = self.connection.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

# categories---

    def get_categories(self):
        " Returns the table as a list of Row_obj. [row1, col2] "

        self.connect()
        cursor = self.connection.cursor()

        cursor.execute("SELECT * FROM categories ORDER BY category")
        categories = cursor.fetchall()
        return categories


    def add_new_category(self, new_category):
        self.connect()
        cursor = self.connection.cursor()



        try:
            cursor.execute(" INSERT INTO categories(category) VALUES (?)", (new_category,))
            self.connection.commit()

        except sqlite3.IntegrityError:
            return "Category already exist"
        
        else:
            return "Category added"
        


    def delete_category(self, id):
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM categories WHERE category_id = ?", (id,))
            self.connection.commit()
            return "catagory deleted" # Success
        
        except sqlite3.IntegrityError:
            return "error occured" # Failure (Foreign Key Constraint)


# transactions--

    def get_transactions_count(self, user_id):
        self.connect()
        cursor = self.connection.cursor()

        cursor.execute(" SELECT COUNT(*) AS row_count FROM transactions WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row["row_count"]
    

    def get_transactions(self, user_id, sort_by="t.t_date", sort_order="DESC", limit=30, offset=0):
        " Returns the table as a list of Row_obj. [row1, col2] "

        order = sort_order.upper()
        query = f""" SELECT t.t_id,
                        DATE(t.t_date) as date,
                        TIME(t.t_date) as time,
                        t.amount_in_paise,
                        t.t_type,
                        c.category,
                        t.description,
                        t.created_at
                    FROM transactions t JOIN categories c
                    ON t.category_id = c.category_id
                    WHERE user_id = ?
                    ORDER BY {sort_by} {order}, t.created_at DESC
                    LIMIT {limit} OFFSET {offset}; 
                    """

        self.connect()
        cursor = self.connection.cursor()

        cursor.execute(query, (user_id,))
        transactions = cursor.fetchall()
        return transactions


    def add_transaction(self, data):
        self.connect()
        cursor = self.connection.cursor()
### here
        try: 
            cursor.execute("""
                    INSERT INTO transactions (user_id, t_date, amount_in_paise, t_type, category_id, description)       
                        VALUES (:user_id, :t_datetime, :amount_in_paise, :t_type, :category_id, :description)   
            """, data)

            self.connection.commit()

        except sqlite3.IntegrityError:
            return "Error occured"
        
        else:
            return "transaction added"


    def delete_transaction(self, id):
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute(" DELETE FROM transactions WHERE t_id = ? ",(id,))
            self.connection.commit()
            return "transaction deleted"
        except:
            return "error occured"


#  Analytics part

    #  total report
    def _get_total(self, t_type, user_id):

        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT SUM(amount_in_paise) AS total FROM transactions WHERE user_id = ? AND t_type = ?", (user_id, t_type,))
        result = cursor.fetchone()["total"]
        return result or 0

    def get_total_income(self, user_id):
        return self._get_total("cr", user_id=user_id)

    def get_total_expense(self, user_id):
        return self._get_total("db", user_id=user_id)
    
    # monthly report
    def get_monthly_report(self, user_id):

        self.connect()
        cursor = self.connection.cursor()

        query = """
                        SELECT strftime('%Y', t_date) AS year, 
                            strftime('%m', t_date) AS month,
                            SUM(CASE WHEN t_type = "cr" THEN amount_in_paise ELSE 0 END) as m_income,
                            SUM(CASE WHEN t_type = "db" THEN amount_in_paise ELSE 0 END) as m_expense
                        FROM transactions
                        WHERE user_id = ?
                        GROUP BY year, month
                        ORDER BY year DESC, month DESC;
                    """
        
        cursor.execute(query, (user_id,))

        result = cursor.fetchall()
        return result or 0

    def get_report_by_categories(self, user_id):

        self.connect()
        cursor = self.connection.cursor()

        query = """
                        SELECT c.category AS category,
                        SUM(CASE WHEN t_type = 'cr' THEN t.amount_in_paise ELSE 0 END) AS income,
                        SUM(CASE WHEN t_type = 'db' THEN t.amount_in_paise ELSE 0 END) AS expense
                        FROM transactions t JOIN categories c
                        ON t.category_id = c.category_id
                        WHERE t.user_id = ?
                        GROUP BY t.category_id
                        HAVING income > 0 OR expense > 0;
                    """
        
        cursor.execute(query, (user_id,))

        result = cursor.fetchall()
        return result or 0
    

#  