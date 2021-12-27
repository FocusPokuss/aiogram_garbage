import psycopg2
from psycopg2.sql import SQL, Identifier


class Database:
    def __init__(
            self,
            DATABASE_HOST,
            DATABASE_USERNAME,
            DATABASE_PASSWORD,
            DATABASE_NAME,
            DATABASE_PORT,
            admin_id,
        ):
        self.host = DATABASE_HOST
        self.username = DATABASE_USERNAME
        self.pwd = DATABASE_PASSWORD
        self.name = DATABASE_NAME
        self.port = DATABASE_PORT
        self.admin_id = admin_id
        self.conn = None

    def connect(self):
        """Connect to postgres SQL database."""
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    user=self.username,
                    dbname=self.name,
                    password=self.pwd,
                    port=5432,
                )
                self.conn.autocommit = True
            except psycopg2.DatabaseError as e:
                print(e)
                raise e
            else:
                print('Connected successfully!')

    def is_admin(self, user_id):
        return str(user_id) == self.admin_id

    def is_in_db(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute('''
            SELECT user_id FROM users WHERE user_id=%s
            ''', (user_id,))
            return cur.fetchone() is not None

    def is_same_choose(self, user_id, file_name, choose):
        decision = choose == 'like'
        with self.conn.cursor() as cur:
            cur.execute('''
            SELECT is_liked FROM files_rating WHERE fk_user_id = %s AND fk_file_name = %s  
            ''', (user_id, file_name))
            res = cur.fetchone()
            return (res[0] == decision) if res is not None else False

    def get_user_data(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute('''
            SELECT * FROM users WHERE user_id=%s;
            ''', (user_id,))
            return ', '.join(str(f) for f in cur.fetchone())

    def add_message(self, user_id, text, current_time):
        with self.conn.cursor() as cur:
            cur.execute('''
            INSERT INTO messages (fk_user_id, text, time) VALUES (%s, %s, %s);
            ''', (user_id, text, current_time))

    def add_user(self, user_id, username, first_name, is_admin):
        with self.conn.cursor() as cur:
            cur.execute('''
            INSERT INTO users (user_id, username, first_name, is_admin) VALUES (%s, %s, %s, %s);
            ''', (user_id, username, first_name, is_admin))

    def set_file_rating(self, user_id, file_name, is_liked):
        with self.conn.cursor() as cur:
            cur.execute('''
            INSERT INTO files_rating
            SELECT %(user_id)s, file_id, %(file_name)s, %(is_liked)s FROM files WHERE file_name=%(file_name)s
            ON CONFLICT (fk_user_id, fk_file_name) DO UPDATE
            SET is_liked = %(is_liked)s WHERE excluded.fk_file_name = files_rating.fk_file_name; 
            ''', {'user_id': user_id, 'file_name': file_name, 'is_liked': is_liked})

    def change_rating(self, user_id, file_name, is_liked):
        other = 'dislikes' if is_liked else 'likes'
        target = 'likes' if is_liked else 'dislikes'
        with self.conn.cursor() as cur:
            cur.execute(SQL('''
            UPDATE files
            SET {target} = CASE
            WHEN EXISTS (SELECT 1 FROM files_rating WHERE fk_file_name=%(file_name)s AND fk_user_id=%(user_id)s)
            THEN {target} + 1 ELSE {target} + 1 END,
            {other} = CASE
            WHEN EXISTS (SELECT 1 FROM files_rating WHERE fk_file_name=%(file_name)s AND fk_user_id=%(user_id)s)
            THEN {other} - 1 ELSE {other} END WHERE file_name = %(file_name)s;
            ''').format(target=Identifier(target), other=Identifier(other)),
                        {'file_name': file_name, 'user_id': user_id})

    def upload_sample(self, file_name, file, user_id):
        with self.conn.cursor() as cur:
            cur.execute('''
            INSERT INTO files (file_name, file_data, fk_user_id)
            VALUES (%s, %s, %s);
            ''', (file_name, file, user_id))

    def show_avaliable(self):
        with self.conn.cursor() as cur:
            cur.execute('''
            SELECT file_name FROM files;
            ''')
            return (res[0] for res in cur.fetchall())

    def get_rating(self, file_name):
        with self.conn.cursor() as cur:
            cur.execute('''
            SELECT likes, dislikes FROM files WHERE file_name = %s;
            ''', (file_name,))
            return cur.fetchone()

    def get_photo(self, file_name):
        with self.conn.cursor() as cur:
            cur.execute('''
            SELECT file_data, file_name FROM files WHERE file_name=%s;
            ''', (file_name,))
            return cur.fetchone()
