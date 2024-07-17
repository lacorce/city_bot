import sqlite3 as sq

db = sq.connect('database/databases.db')
cur = db.cursor()


def create_table():
    cur.execute('CREATE TABLE IF NOT EXISTS users('
                'name TEXT,'
                'balls TEXT)')

    cur.execute('CREATE TABLE IF NOT EXISTS application('
                'id integer primary key autoincrement,'
                'name TEXT,'
                'status TEXT)')

    db.commit()


async def add_user(first_name):
    result = cur.execute('select * from users where name = ?',(first_name,)).fetchall()
    if not result:
        print('yes')
        cur.execute('insert into users (name,balls) values (?,?)',(first_name,0))
        db.commit()

async def add_statistic(first_name, balls):
    cur.execute('select balls from users where name = ?', (first_name,))
    result = cur.fetchone()
    if result is None:
        cur.execute('insert into users (name, balls) values (?, ?)', (first_name, balls))
    else:
        cur.execute('update users set balls = balls + ? where name = ?', (balls, first_name))
    db.commit()

async def get_statistic():
    cur.execute('SELECT * FROM users')
    return cur.fetchall()

async def get_top_statistic(count=5):
    cur.execute('SELECT name, balls FROM users ORDER BY balls DESC LIMIT ?', (count,))
    return cur.fetchall()

async def add_application(name):
    cur.execute('INSERT INTO application (name, status) VALUES (?, ?)', (name, '0'))
    print('11111')
    db.commit()

async def send_application():
    cur.execute('SELECT * FROM application WHERE status = 0')
    applications = cur.fetchall()
    return applications

async def check_app(id):
    cur.execute('select * from application WHERE id = ?',(id,))
    result = cur.fetchone()
    return result
async def delete_application(id):
    cur.execute('DELETE FROM application WHERE id = ?', (id,))
    db.commit()
