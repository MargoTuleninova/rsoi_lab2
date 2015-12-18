import pyodbc
from datetime import datetime, timedelta

def films_db_conn():
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=Lenovo-Margo;DATABASE=Films;')
    cursor = cnxn.cursor()
    return cursor;

def users_db_conn():
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=Lenovo-Margo;DATABASE=users;')
    cursor = cnxn.cursor()
    return cursor;

def user_exist(phone):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.UsersInfo where phone='" + phone+"'")
    row = cursor.fetchone()
    if row:
        return 1
    else:
        return 0

def client_exist(client_id):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.apps where client_id='" + client_id+"'")
    row = cursor.fetchone()
    if row:
        return 1
    else:
        return 0

def insert_user(name, password, phone, email):
    cursor = users_db_conn()
    cursor.execute("insert into dbo.UsersInfo values ('"+phone+"','"+name+"','"+email+"','','"+password+"','','','')")
    cursor.commit()
    return 0;

def len_db():
    cursor = films_db_conn()
    cursor.execute("select count(*) from dbo.main")
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return 0;

def films_from_db(page, per_page):
    items = []
    cursor = films_db_conn()
    cursor.execute("select * from dbo.main")
    rows = cursor.fetchall()
    i = 0
    for row in rows:
        if i < page * per_page:
            text = row.title.decode(encoding='ISO-8859-1', errors='strict')
            items.append({
            'id': row.id,
            'id_director': row.id_director,
            'title': text,
            'kinopoisk_rating': float(row.kinopoisk_rating),
            })
            i += 1
        if i >= (page + 1) * per_page:
            i += 1
            break
    return items;

def film_by_id(id):
    cursor = films_db_conn()
    cursor.execute("select * from dbo.main where id=" + id)
    row = cursor.fetchone()
    if row:
        return row
    else:
        return 0;

def len_db_dirs():
    count = 0;
    cursor = films_db_conn()
    cursor.execute("select * from dbo.directors")
    cursor1= films_db_conn()
    cursor1.execute("select * from dbo.main")
    rows = cursor.fetchall()
    rows1 = cursor1.fetchall()
    for row in rows:
        for row1 in rows1:
            if row1.id_director==row.id_director:
                count += 1
    return count;

def directors_from_db(page, per_page):
    cursor = films_db_conn()
    cursor.execute("select * from dbo.directors")
    cursor1 = films_db_conn()
    cursor1.execute("select * from dbo.main")
    rows = cursor.fetchall()
    rows1 = cursor1.fetchall()
    i = 0
    items= []
    for row1 in rows1:
        for row in rows:
            if row1.id_director==row.id_director:
                if i < page * per_page:
                    items.append({
                    'id_director': row.id_director,
                    'name': row.name.decode(encoding='ISO-8859-1', errors='strict'),
                    'title': row1.title.decode(encoding='ISO-8859-1', errors='strict'),
                    })
                    i += 1
                if i >= (page + 1) * per_page:
                    i += 1
                    break
    return items;

def director_by_id(id):
    cursor = films_db_conn()
    cursor.execute("select * from dbo.directors where id_director=" + id)
    row = cursor.fetchone()
    if row:
        return row
    else:
        return 0;

def insert_film(id, id_director, title, duration, year, genre, kinopoisk_rating):
    cursor = films_db_conn()
    try:
        cursor.execute("insert into dbo.main values ("+id+", "+id_director+",'"+title+"','"+duration+"', "+year+", '"+genre+"', "+kinopoisk_rating+")")
        cursor.commit()
    except pyodbc.IntegrityError:
        return 0
    return 1

def insert_director(id, name, birthday, country):
    cursor = films_db_conn()
    try:
        cursor.execute("insert into dbo.directors values ("+id+", '"+name+"', '"+birthday+"', '"+country+"')")
        cursor.commit()
    except pyodbc.IntegrityError:
        return 0
    return 1

def update_director(id, str, value):
    cursor = films_db_conn()
    try:
        cursor.execute("update dbo.directors set "+str+"='"+value+"' where id_director="+id)
        cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1

def update_film(id, str, value):
    cursor = films_db_conn()
    try:
        if str == 'title' or str == 'duration' or str == 'genre':
            cursor.execute("update dbo.main set "+str+"='"+value+"' where id="+id)
            cursor.commit()
        else:
            cursor.execute("update dbo.main set "+str+"="+value+" where id="+id)
            cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1

def del_film(id):
    cursor = films_db_conn()
    cursor.execute("delete from dbo.main where id="+id)
    cursor.commit()

def read_redirect(client_id):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.apps where client_id='" + client_id+"'")
    row = cursor.fetchone()
    if row:
        return row.redirect_uri
    return 0;

def user_pass_check(phone, password):
    cursor = users_db_conn()
    print phone
    cursor.execute("select * from dbo.UsersInfo where phone='" + phone+"'")
    row = cursor.fetchone()
    print row.parol
    if row.parol.find(password)!=-1:
        return 1
    return 0;

def code_insert(code, phone):
    try:
        cursor = users_db_conn()
        cursor.execute("update dbo.UsersInfo set code='"+code+"' where phone='" + phone+"'")
        cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1;

def client_secret_check(client_id, secret_id):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.apps where client_id='" + client_id+"'")
    row = cursor.fetchone()
    if row.secret_id.find(secret_id)!=-1:
        return 1
    return 0;

def code_check(code):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.UsersInfo where code='" + code+"'")
    row = cursor.fetchone()
    if row:
        return row.phone
    return 0;

def refresh_token_check(refresh_token):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.UsersInfo where refresh_token='" + refresh_token+"'")
    row = cursor.fetchone()
    if row:
        return row.phone
    return 0;

def insert_token(phone, access_token, expire_time, refresh_token):
    cursor = users_db_conn()
    cursor.execute("update dbo.UsersInfo set refresh_token='"+refresh_token+"' where phone='" + phone+"'")
    cursor.execute("update dbo.UsersInfo set access_token='"+access_token+"' where phone='" + phone+"'")
    cursor.execute("update dbo.UsersInfo set expired='"+str(expire_time)+"' where phone='" + phone+"'")
    cursor.commit()
    return 1;

def expired_check(refresh_token):
    cursor = users_db_conn()
    print refresh_token
    cursor.execute("select * from dbo.UsersInfo where refresh_token='" + refresh_token+"'")
    row = cursor.fetchone()
    if row:
        print datetime.now()
        if datetime.strptime(row.expired[:26], '%Y-%m-%d %H:%M:%S.%f') > datetime.now():
            return 2
        if datetime.strptime(row.expired[:26], '%Y-%m-%d %H:%M:%S.%f') < datetime.now():
            return 1
    return 0

def expired_check1(access_token):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.UsersInfo where access_token='" + access_token+"'")
    row = cursor.fetchone()
    time30 = timedelta(minutes=0)
    if row:
        print datetime.now()
        try:
            if datetime.strptime(row.expired[:26], '%Y-%m-%d %H:%M:%S.%f')-datetime.now() > time30:
                print datetime.strptime(row.expired[:26], '%Y-%m-%d %H:%M:%S.%f')
                return 2
            if datetime.strptime(row.expired[:26], '%Y-%m-%d %H:%M:%S.%f')-datetime.now() < time30:
                return 1
        except TypeError:
            return 2
    return 0

def expired_refresh(refresh_token):
    cursor = users_db_conn()
    expire_time = datetime.now() + timedelta(minutes=10)
    cursor.execute("update dbo.UsersInfo set expired='"+str(expire_time)+"' where refresh_token='" + refresh_token+"'")
    cursor.commit()
    return 1;

def get_me(access_token):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.UsersInfo where access_token='" + access_token+"'")
    row = cursor.fetchone()
    if row:
        return row