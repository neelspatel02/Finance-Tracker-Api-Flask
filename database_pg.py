import psycopg2
from psycopg2.extras import RealDictCursor


class DataBase:

    def __init__(self, db_url):
        # db_url is the full postgres connection string from environment variable
        # e.g. postgresql://user:password@host:5432/dbname
        self.db_url = db_url
        self.connection = None


    def connect(self):
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(self.db_url)
        return self.connection


# ==================== CREATING TABLES ====================

    def create_tables(self):
        self.connect()
        # RealDictCursor makes rows behave like dicts — same as sqlite3.Row
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories(
                category_id SERIAL PRIMARY KEY,
                category TEXT NOT NULL UNIQUE
            )""")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                t_id SERIAL PRIMARY KEY,
                user_id INTEGER,
                t_date TIMESTAMP,
                amount_in_paise INTEGER NOT NULL,
                t_type TEXT CHECK(t_type IN('cr', 'db')),
                category_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )""")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date_id ON transactions(t_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, t_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(t_type)")

        self.connection.commit()


# ==================== USERS ====================

    def add_user(self, username, email, password_hash):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
            """, (username, email, password_hash))
            self.connection.commit()

        except psycopg2.IntegrityError:
            self.connection.rollback()  # must rollback before next query after an error in postgres
            raise ValueError("User or email already exists")


    def get_user_by_username(self, username):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()


    def get_user_by_id(self, user_id):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return cursor.fetchone()


# ==================== CATEGORIES ====================

    def get_categories(self):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM categories ORDER BY category")
        return cursor.fetchall()


    def add_new_category(self, new_category):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute("INSERT INTO categories(category) VALUES (%s)", (new_category,))
            self.connection.commit()

        except psycopg2.IntegrityError:
            self.connection.rollback()
            raise ValueError("Category already exists")


    def delete_category(self, id):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute("DELETE FROM categories WHERE category_id = %s", (id,))
            self.connection.commit()

        except psycopg2.IntegrityError:
            self.connection.rollback()
            raise ValueError("Category is in use and cannot be deleted")


# ==================== TRANSACTIONS ====================

    def get_transactions_count(self, user_id):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT COUNT(*) AS row_count FROM transactions WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        return row["row_count"]


    def get_transactions(self, user_id, filters,
                            sort_by="t.t_date",
                            sort_order="DESC",
                            limit=30,
                            offset=0):

        order = sort_order.upper()

        # DATE() and TIME() are SQLite functions.
        # Postgres equivalent: t_date::date and t_date::time
        query = f"""SELECT t.t_id,
                        t.t_date::date AS date,
                        t.t_date::time AS time,
                        t.amount_in_paise,
                        t.t_type,
                        c.category,
                        t.description,
                        t.created_at
                    FROM transactions t JOIN categories c
                    ON t.category_id = c.category_id
                    WHERE t.user_id = %s"""

        query_end = f""" ORDER BY {sort_by} {order}, t.created_at DESC
                    LIMIT {limit} OFFSET {offset}"""

        params = [user_id]

        if filters.get("start_date"):
            query += " AND t.t_date >= %s"
            params.append(filters["start_date"])
        if filters.get("end_date"):
            query += " AND t.t_date <= %s"
            params.append(filters["end_date"])
        if filters.get("t_type"):
            query += " AND t.t_type = %s"
            params.append(filters["t_type"])

        query += query_end

        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, tuple(params))
        return cursor.fetchall()


    def add_transaction(self, data):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        try:
            # SQLite used named params (:key) — Postgres uses %(key)s for named style
            cursor.execute("""
                INSERT INTO transactions (user_id, t_date, amount_in_paise, t_type, category_id, description)
                VALUES (%(user_id)s, %(t_datetime)s, %(amount_in_paise)s, %(t_type)s, %(category_id)s, %(description)s)
            """, data)
            self.connection.commit()

        except psycopg2.IntegrityError:
            self.connection.rollback()
            raise ValueError("Invalid category")


    def delete_transaction(self, transaction_id):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute("DELETE FROM transactions WHERE t_id = %s", (transaction_id,))
            self.connection.commit()

        except Exception:
            self.connection.rollback()
            raise ValueError("Transaction not found")


# ==================== ANALYSIS ====================

    def _query_maker(self, query, params, start_date=None, end_date=None):
        if start_date:
            query += " AND t_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND t_date <= %s"
            params.append(end_date)
        return query, params


    def _get_total(self, t_type, user_id, start_date=None, end_date=None):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        params = [user_id, t_type]
        query = "SELECT SUM(amount_in_paise) AS total FROM transactions WHERE user_id = %s AND t_type = %s"

        query, params = self._query_maker(query, params, start_date, end_date)
        cursor.execute(query, tuple(params))
        result = cursor.fetchone()["total"]
        return result or 0

    def get_total_income(self, user_id, start_date=None, end_date=None):
        return self._get_total("cr", user_id, start_date, end_date)

    def get_total_expense(self, user_id, start_date=None, end_date=None):
        return self._get_total("db", user_id, start_date, end_date)


# YEARLY REPORT
    def get_yearly_report(self, user_id, start_date=None, end_date=None):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        params = [user_id]
        # strftime('%Y', ...) → TO_CHAR(..., 'YYYY') in Postgres
        query = """
            SELECT TO_CHAR(t_date, 'YYYY') AS year,
                SUM(CASE WHEN t_type = 'cr' THEN amount_in_paise ELSE 0 END) AS income,
                SUM(CASE WHEN t_type = 'db' THEN amount_in_paise ELSE 0 END) AS expense
            FROM transactions
            WHERE user_id = %s"""

        query_end = " GROUP BY year ORDER BY year DESC"

        new_query, params = self._query_maker(query, params, start_date, end_date)
        cursor.execute(new_query + query_end, tuple(params))
        result = cursor.fetchall()
        return result or 0


# MONTHLY REPORT
    def get_monthly_report(self, user_id, start_date=None, end_date=None):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        params = [user_id]
        query = """
            SELECT TO_CHAR(t_date, 'YYYY') AS year,
                TO_CHAR(t_date, 'MM') AS month,
                SUM(CASE WHEN t_type = 'cr' THEN amount_in_paise ELSE 0 END) AS income,
                SUM(CASE WHEN t_type = 'db' THEN amount_in_paise ELSE 0 END) AS expense
            FROM transactions
            WHERE user_id = %s"""

        query_end = " GROUP BY year, month ORDER BY year DESC, month DESC"

        new_query, params = self._query_maker(query, params, start_date, end_date)
        cursor.execute(new_query + query_end, tuple(params))
        result = cursor.fetchall()
        return result or 0


# WEEKLY REPORT
    def get_weekly_report(self, user_id, start_date=None, end_date=None):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        params = [user_id]
        # EXTRACT(YEAR/MONTH FROM ...) is the Postgres equivalent of strftime
        # week_of_month: same formula as SQLite — (day-1)/7 + 1
        query = """
            SELECT TO_CHAR(t_date, 'YYYY') AS year,
                TO_CHAR(t_date, 'MM') AS month,
                ((EXTRACT(DAY FROM t_date)::int - 1) / 7 + 1) AS week_of_month,
                SUM(CASE WHEN t_type = 'cr' THEN amount_in_paise ELSE 0 END) AS income,
                SUM(CASE WHEN t_type = 'db' THEN amount_in_paise ELSE 0 END) AS expense
            FROM transactions
            WHERE user_id = %s"""

        query_end = " GROUP BY year, month, week_of_month ORDER BY year DESC, month DESC, week_of_month DESC"

        new_query, params = self._query_maker(query, params, start_date, end_date)
        cursor.execute(new_query + query_end, tuple(params))
        result = cursor.fetchall()
        return result or 0


# CATEGORIAL REPORT
    def get_report_by_categories(self, user_id, start_date=None, end_date=None):
        self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)

        params = [user_id]
        query = """
            SELECT c.category AS category,
                SUM(CASE WHEN t_type = 'cr' THEN t.amount_in_paise ELSE 0 END) AS income,
                SUM(CASE WHEN t_type = 'db' THEN t.amount_in_paise ELSE 0 END) AS expense
            FROM transactions t JOIN categories c
            ON t.category_id = c.category_id
            WHERE t.user_id = %s"""

        query_end = """ GROUP BY c.category, t.category_id
                        HAVING SUM(CASE WHEN t_type = 'cr' THEN t.amount_in_paise ELSE 0 END) > 0
                            OR SUM(CASE WHEN t_type = 'db' THEN t.amount_in_paise ELSE 0 END) > 0"""

        if start_date:
            query += " AND t.t_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND t.t_date <= %s"
            params.append(end_date)

        cursor.execute(query + query_end, tuple(params))
        result = cursor.fetchall()
        return result or 0