from hashlib import sha256
from uuid import uuid4
import random
import string
import json
import math
import time
from datetime import datetime, timedelta
from conn_db import *
from flask import Flask \
                , render_template \
                , redirect \
                , url_for \
                , request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def start():
    return redirect(url_for('register_form'))

@app.route('/register', methods=['GET'])
def register_form():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    if not name:
        return render_template('fail_registration.html', reason='Empty login not allowed.')

    password = request.form['password']
    if len(password) < 6:
        return render_template('fail_registration.html', reason='Password is too short')

    email = request.form['email']
    phone = request.form['phone']

    if user_exist(phone):
        return render_template('fail_registration.html', reason='User already exists.'.format(phone))

    insert_user(name, password, phone, email)

    return render_template('registration_ok.html', name=request.form['name'])



@app.route('/films/', methods=['GET'])
def get_films():
    try:
        per_page = int(request.args.get('per_page', 20))
        if per_page < 20 or per_page > 100:
            raise Exception()
        page = int(request.args.get('page', 0))
        lendb = len_db()
        if lendb % per_page > 0:
            b = 1
        else:
            b = 0
        if page < 0 or page > lendb / per_page + b:
            raise Exception()
    except:
        return '', 400

    items = []
    items = films_from_db(page, per_page)
    return json.dumps({
        'items': items,
        'per_page': per_page,
        'page': page,
        'page_count': math.ceil(lendb / per_page + b)
    }, indent=4),200, {
        'Content-Type': 'application/json;charset=UTF-8',
    }

@app.route('/me/', methods=['GET'])
def me():
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = get_me(access_token)
    return json.dumps({
            'name': row.name.decode(encoding='ISO-8859-1', errors='strict'),
            'email': row.mail,
            'phone': row.phone
        }, indent=4), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/films/<id>', methods=['GET'])
def get_film(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = film_by_id(id)
    print row
    if row == 0:
        return '', 404
    else:
        time.struct_time=row.duration
        return json.dumps({
            'id': row.id,
            'title': row.title.decode(encoding='ISO-8859-1', errors='strict'),
            'duration': time.struct_time,
            'year': row.year,
            'genre': row.genre.decode(encoding='ISO-8859-1', errors='strict'),
            'kinopoisk_rating': float(row.kinopoisk_rating)
        }, indent=4), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/directors/', methods=['GET'])
def get_directors():
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    try:
        per_page = int(request.args.get('per_page', 20))
        if per_page < 20 or per_page > 100:
            raise Exception()
        page = int(request.args.get('page', 0))
        lendb = len_db_dirs()
        print lendb
        if lendb % per_page > 0:
            b = 1
        else:
            b = 0
        if page < 0 or page > lendb / per_page + b:
            raise Exception()
    except:
        return '', 400

    items = []
    items = directors_from_db(page, per_page)
    return json.dumps({
        'items': items,
        'per_page': per_page,
        'page': page,
        'page_count': math.ceil(lendb / per_page + b)
    }, indent=4), 200, {
        'Content-Type': 'application/json;charset=UTF-8',
    }

@app.route('/directors/<id>', methods=['GET'])
def get_director(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = director_by_id(id)
    if row == 0:
        return '', 404
    else:
        return json.dumps({
            'id_director': row.id_director,
            'name': row.name.decode(encoding='ISO-8859-1', errors='strict'),
            'birthday': row.birthday,
            'country of birth': row.country
        }, indent=4), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/films/<id>', methods=['POST'])
def post_film(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    try:
        id_director = request.args.get('id_director')
        title = request.args.get('title')
        duration = request.args.get('duration')
        year = request.args.get('year')
        genre = request.args.get('genre')
        kinopoisk_rating = request.args.get('kinopoisk_rating')
        if id_director is None or year is None or kinopoisk_rating is None:
            raise Exception()
        if duration is None or title is None or genre is None:
            raise Exception()
    except:
        return '', 400

    i = insert_film(id, id_director, title, duration, year, genre, kinopoisk_rating)
    if i == 0:
        return '', 400
    s = '/films/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 201, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/directors/<id>', methods=['POST'])
def post_director(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    try:
        name = request.args.get('name')
        birthday = request.args.get('birthday')
        country = request.args.get('country')
        if name is None or birthday is None or country is None:
            raise Exception()
    except:
        return '', 400
    i = insert_director(id, name, birthday, country)
    if i == 0:
        return '', 400
    s = '/directors/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 201, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/directors/<id>', methods=['PUT'])
def put_director(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = director_by_id(id)
    if row == 0:
        return '', 404
    try:
        name = request.args.get('name')
        birthday = request.args.get('birthday')
        country = request.args.get('country')
        if name is None and birthday is None and country is None:
            raise Exception()
    except:
        return '', 400
    if name is not None:
        i = update_director(id, 'name', name)
    if birthday is not None:
        i = update_director(id, 'birthday', birthday)
    if country is not None:
        i = update_director(id, 'country', country)
    if i == 0:
        return '', 400
    s = '/directors/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/films/<id>', methods=['PUT'])
def put_film(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = film_by_id(id)
    if row == 0:
        return '', 404
    try:
        id_director = request.args.get('id_director')
        title = request.args.get('title')
        duration = request.args.get('duration')
        year = request.args.get('year')
        genre = request.args.get('genre')
        kinopoisk_rating = request.args.get('kinopoisk_rating')
        if id_director is None and year is None and kinopoisk_rating is None and duration is None and title is None and genre is None:
            raise Exception()
    except:
        return '', 400
    if id_director is not None:
        i = update_film(id, 'id_director', id_director)
    if title is not None:
        i = update_film(id, 'title', title)
    if duration is not None:
        i = update_film(id, 'duration', duration)
    if year is not None:
        i = update_film(id, 'year', year)
    if genre is not None:
        i = update_film(id, 'genre', genre)
    if kinopoisk_rating is not None:
        i = update_film(id, 'kinopoisk_rating', kinopoisk_rating)
    if i == 0:
        return '', 400
    s = '/films/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/films/<id>', methods=['DELETE'])
def delete_film(id):
    access_token = request.headers.get('Authorization', '')[len('OAUTH-TOKEN '):]
    print access_token
    i = expired_check1(access_token)
    if i==0:
        return json.dumps({'error': 'invalid_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    if i==1:
        return json.dumps({'error': 'expired_token'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8'}
    row = film_by_id(id)
    if row == 0:
        return '', 404
    del_film(id)
    s = '/films/{'+id+'}'
    return json.dumps({
        'Location': s
    }), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

@app.route('/oauth/authorize', methods=['GET'])
def authorize():
    response_type = request.args.get('response_type')
    client_id = request.args.get('client_id')
    state = request.args.get('state')
    if client_id is None:
        return render_template('fail_authorize.html', reason='Require client_id.')
    if client_exist(client_id)==0:
        return render_template('fail_authorize.html', reason='client_id is invalid.')
    s = read_redirect(client_id)
    if response_type is None:
        return redirect(s.decode(encoding='ISO-8859-1', errors='strict') + '?error=invalid_request' +
            ('' if state is None else '&state=' + state), code=302)
    if response_type != 'code':
        return redirect(s.decode(encoding='ISO-8859-1', errors='strict') + '?error=unsupported_response_type' +
            ('' if state is None else '&state=' + state), code=302)

    return render_template('authorize.html', state=state,
                                                  client_id=client_id,
                                                  client_name='Films')

@app.route('/oauth/authorize', methods=['POST'])
def authorize_films():
    client_id = str(request.form.get('client_id'))
    phone = str(request.form.get('phone'))
    password = str(request.form.get('password'))
    state = str(request.form.get('state'))
    if user_pass_check(phone, password) == 0:
        return redirect(read_redirect(client_id) + '?error=access_denied' + ('' if state is None else '&state=' + state), code=302)

    code = ''.join(random.choice(string.lowercase) for i in range(10))
    code_insert(code, phone)
    s = read_redirect(client_id)
    return redirect(s + '  ?code=' + code + ('' if state is None else '&state=' + state), code=302)


@app.route('/oauth/token', methods=['POST'])
def get_token():
    try:
        type = request.args.get('type')
        client_id = request.args.get('client_id')
        secret_id = request.args.get('secret_id')
    except KeyError:
        return json.dumps({'error': 'invalid_request'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8',
        }
    if client_id is None or type is None or secret_id is None:
        return json.dumps({'error': 'invalid_request'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8',
        }
    if client_exist(client_id)==0 or client_secret_check(client_id,secret_id)==0:
        return json.dumps({'error': 'invalid_client'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8',
        }
    if type == 'code':
        code = request.args.get('code')
        phone = code_check(code)
        if phone == 0:
            return json.dumps({'error': 'invalid_grant'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }

    elif type == 'refresh_token':
        try:
            refresh_token = request.args.get('refresh_token')
        except KeyError:
            return json.dumps({'error': 'invalid_request'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }

        phone = refresh_token_check(refresh_token)
        if phone == 0:
            return json.dumps({'error': 'invalid_grant'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }
        i = expired_check(refresh_token)
        if i==0:
            return json.dumps({'error': 'invalid_token'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }
        expired_refresh(refresh_token)
        return '', 200

    access_token = ''.join(random.choice(string.lowercase) for i in range(30))
    expire_time = datetime.now() + timedelta(minutes=10)
    refresh_token = ''.join(random.choice(string.lowercase) for i in range(30))
    insert_token(phone, access_token, expire_time, refresh_token)
    return json.dumps({
        'access_token': access_token,
        'token_type': 'bearer',
        'expires_in': 300,
        'refresh_token': refresh_token,
    }), 200, {
        'Content-Type': 'application/json;charset=UTF-8',
        'Cache-Control': 'no-store',
        'Pragma': 'no-cache',
    }


if __name__ == '__main__':
    app.run(port=5100, debug=True)