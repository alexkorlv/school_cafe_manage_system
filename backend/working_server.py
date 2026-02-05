from flask import Flask, jsonify, request, make_response, g
from flask_cors import CORS
import sqlite3
import hashlib
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'school-cafe-secret-key-2024'
CORS(app,
     resources={r"/api/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


DATABASE = 'school_cafe_full.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users (
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            username TEXT UNIQUE NOT NULL,
                                                            password_hash TEXT NOT NULL,
                                                            full_name TEXT NOT NULL,
                                                            role INTEGER NOT NULL DEFAULT 0,
                                                            class_name TEXT,
                                                            balance REAL DEFAULT 0.0,
                                                            allergies TEXT,
                                                            dietary_preferences TEXT,
                                                            email TEXT,
                                                            phone TEXT,
                                                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       )
                       ''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS dishes (
                                                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                             name TEXT NOT NULL,
                                                             description TEXT,
                                                             category TEXT NOT NULL,
                                                             price REAL NOT NULL,
                                                             ingredients TEXT,
                                                             allergens TEXT,
                                                             calories INTEGER,
                                                             is_available BOOLEAN DEFAULT 1,
                                                             quantity INTEGER DEFAULT 0,
                                                             rating REAL DEFAULT 0.0,
                                                             rating_count INTEGER DEFAULT 0,
                                                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       )
                       ''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS orders (
                                                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                             user_id INTEGER NOT NULL,
                                                             dish_id INTEGER NOT NULL,
                                                             dish_name TEXT NOT NULL,
                                                             price REAL NOT NULL,
                                                             meal_type TEXT,
                                                             payment_type TEXT,
                                                             status TEXT DEFAULT 'pending',
                                                             order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                             served_at TIMESTAMP,
                                                             FOREIGN KEY (user_id) REFERENCES users (id),
                           FOREIGN KEY (dish_id) REFERENCES dishes (id)
                           )
                       ''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS purchase_requests (
                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                        created_by INTEGER NOT NULL,
                                                                        dish_id INTEGER,
                                                                        dish_name TEXT NOT NULL,
                                                                        quantity INTEGER NOT NULL,
                                                                        reason TEXT,
                                                                        status TEXT DEFAULT 'pending',
                                                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                                        processed_at TIMESTAMP,
                                                                        processed_by INTEGER,
                                                                        FOREIGN KEY (created_by) REFERENCES users (id),
                           FOREIGN KEY (processed_by) REFERENCES users (id)
                           )
                       ''')

        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            def hash_pw(pwd):
                return hashlib.sha256(pwd.encode()).hexdigest()

            users = [
                ('student1', hash_pw('password123'), 'Иванов Иван', 0, '10А', 1000.0, 'орехи, молоко', 'вегетарианец', 'ivan@school.ru', '+79161234567'),
                ('student2', hash_pw('password123'), 'Петрова Мария', 0, '9Б', 500.0, 'глютен', None, 'petrova@school.ru', '+79162345678'),
                ('cook1', hash_pw('password123'), 'Смирнов Алексей', 1, None, 0.0, None, None, 'cook@school.ru', '+79163456789'),
                ('admin1', hash_pw('password123'), 'Козлова Анна', 2, None, 0.0, None, None, 'admin@school.ru', '+79164567890'),
            ]

            cursor.executemany('''
                               INSERT INTO users (username, password_hash, full_name, role, class_name, balance, allergies, dietary_preferences, email, phone)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                               ''', users)

            dishes = [
                ('Омлет с овощами', 'Свежий омлет с помидорами и зеленью', 'завтрак', 150.0, 'яйца, помидоры, лук, молоко', 'яйца, молоко', 250, 1, 5, 4.5, 20),
                ('Каша гречневая', 'Гречневая каша с маслом', 'завтрак', 80.0, 'гречка, вода, масло', 'глютен', 180, 1, 3, 4.2, 15),
                ('Суп куриный', 'Наваристый куриный суп с лапшой', 'обед', 120.0, 'курица, лапша, морковь, лук', 'глютен', 200, 1, 2, 4.7, 25),
                ('Плов', 'Узбекский плов с бараниной', 'обед', 180.0, 'рис, баранина, морковь, лук', None, 350, 1, 0, 4.8, 18),
                ('Компот', 'Ягодный компот', 'напиток', 30.0, 'вода, ягоды, сахар', None, 50, 1, 10, 4.0, 30),
            ]

            cursor.executemany('''
                               INSERT INTO dishes (name, description, category, price, ingredients, allergens, calories, is_available, quantity, rating, rating_count)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                               ''', dishes)

            requests = [
                (3, 4, 'Плов', 20, 'Закончился на складе', 'pending'),
                (3, None, 'Курица для супа', 10, 'Необходимо для приготовления', 'pending'),
            ]

            cursor.executemany('''
                               INSERT INTO purchase_requests (created_by, dish_id, dish_name, quantity, reason, status)
                               VALUES (?, ?, ?, ?, ?, ?)
                               ''', requests)

        db.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_from_token():
    """Получение пользователя из токена"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    try:
        token = auth_header.split(' ')[1]
        parts = token.split('-')

        if len(parts) >= 2:
            username = parts[1]

            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            if user:
                return user

        return None
    except:
        return None


@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        role = data.get('role', 0)
        class_name = data.get('class_name', '').strip()

        print(f"📝 Регистрация: username={username}, full_name={full_name}, role={role}")

        if not username or not password or not full_name:
            return jsonify({'error': 'Заполните все обязательные поля'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Пароль должен быть не менее 6 символов'}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            return jsonify({'error': 'Пользователь с таким логином уже существует'}), 400

        password_hash = hash_password(password)
        cursor.execute('''
                       INSERT INTO users (username, password_hash, full_name, role, class_name, balance)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', (username, password_hash, full_name, role, class_name, 0.0))

        user_id = cursor.lastrowid
        db.commit()

        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        token = f'token-{user["username"]}-{datetime.now().timestamp()}'

        return jsonify({
            'success': True,
            'message': 'Регистрация успешна!',
            'access_token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role'],
                'class_name': user['class_name'],
                'balance': user['balance']
            }
        }), 201

    except Exception as e:
        print(f"🔥 Ошибка регистрации: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Ошибка регистрации'}), 500


@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'error': 'Введите логин и пароль'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Неверный логин или пароль'}), 401

        if user['password_hash'] != hash_password(password):
            return jsonify({'error': 'Неверный логин или пароль'}), 401

        token = f'token-{user["username"]}-{datetime.now().timestamp()}'

        return jsonify({
            'success': True,
            'message': 'Вход выполнен успешно',
            'access_token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role'],
                'class_name': user['class_name'],
                'balance': user['balance'],
                'allergies': user['allergies'],
                'dietary_preferences': user['dietary_preferences'],
                'email': user['email'],
                'phone': user['phone']
            }
        })

    except Exception as e:
        print(f"Ошибка входа: {e}")
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

@app.route('/api/user/profile', methods=['GET', 'OPTIONS'])
def get_profile():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Неавторизован'}), 401

        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'full_name': user['full_name'],
            'role': user['role'],
            'class_name': user['class_name'],
            'balance': user['balance'],
            'allergies': user['allergies'],
            'dietary_preferences': user['dietary_preferences'],
            'email': user['email'],
            'phone': user['phone'],
            'created_at': user['created_at']
        })

    except Exception as e:
        print(f"Ошибка получения профиля: {e}")
        return jsonify({'error': 'Ошибка получения профиля'}), 500

@app.route('/api/menu', methods=['GET', 'OPTIONS'])
def get_menu():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        category = request.args.get('category')

        db = get_db()
        cursor = db.cursor()

        if category:
            cursor.execute('SELECT * FROM dishes WHERE category = ? AND is_available = 1 ORDER BY price', (category,))
        else:
            cursor.execute('SELECT * FROM dishes WHERE is_available = 1 ORDER BY category, price')

        dishes = cursor.fetchall()

        return jsonify([dict(dish) for dish in dishes])

    except Exception as e:
        print(f"Ошибка получения меню: {e}")
        return jsonify({'error': 'Ошибка получения меню'}), 500



@app.route('/api/dishes', methods=['GET', 'POST', 'OPTIONS'])
def manage_dishes():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Неавторизован'}), 401


        if request.method == 'GET':
            if user['role'] != 2:
                return jsonify({'error': 'Недостаточно прав'}), 403

            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM dishes ORDER BY category, name')
            dishes = cursor.fetchall()

            return jsonify([dict(dish) for dish in dishes])

        # POST - добавление нового блюда
        elif request.method == 'POST':
            if user['role'] != 2:
                return jsonify({'error': 'Только администратор может добавлять блюда'}), 403

            data = request.get_json()

            required_fields = ['name', 'category', 'price']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Поле "{field}" обязательно'}), 400

            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            category = data.get('category', '').strip()
            price = float(data.get('price', 0))
            ingredients = data.get('ingredients', '').strip()
            allergens = data.get('allergens', '').strip()
            calories = data.get('calories')
            quantity = data.get('quantity', 0)

            if price <= 0:
                return jsonify({'error': 'Цена должна быть положительной'}), 400

            if quantity < 0:
                return jsonify({'error': 'Количество не может быть отрицательным'}), 400

            db = get_db()
            cursor = db.cursor()

            cursor.execute('SELECT id FROM dishes WHERE name = ?', (name,))
            if cursor.fetchone():
                return jsonify({'error': 'Блюдо с таким названием уже существует'}), 400

            cursor.execute('''
                           INSERT INTO dishes (name, description, category, price, ingredients, allergens,
                                               calories, quantity, is_available)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ''', (name, description, category, price, ingredients, allergens,
                                 calories, quantity, 1 if quantity > 0 else 0))

            dish_id = cursor.lastrowid
            db.commit()

            cursor.execute('SELECT * FROM dishes WHERE id = ?', (dish_id,))
            dish = cursor.fetchone()

            print(f"✅ Администратор {user['username']} добавил блюдо: {name}")

            return jsonify({
                'success': True,
                'message': f'Блюдо "{name}" добавлено в меню',
                'dish': dict(dish)
            }), 201

    except ValueError as e:
        return jsonify({'error': 'Неверный формат данных'}), 400
    except Exception as e:
        print(f"Ошибка управления блюдами: {e}")
        return jsonify({'error': 'Ошибка управления блюдами'}), 500

@app.route('/api/dishes/<int:dish_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def manage_single_dish(dish_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user or user['role'] != 2:
            return jsonify({'error': 'Только администратор может управлять блюдами'}), 403

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM dishes WHERE id = ?', (dish_id,))
        dish = cursor.fetchone()

        if not dish:
            return jsonify({'error': 'Блюдо не найдено'}), 404

        if request.method == 'PUT':
            data = request.get_json()

            updates = []
            values = []

            if 'name' in data:
                new_name = data['name'].strip()
                if new_name != dish['name']:
                    # Проверяем уникальность нового названия
                    cursor.execute('SELECT id FROM dishes WHERE name = ? AND id != ?',
                                   (new_name, dish_id))
                    if cursor.fetchone():
                        return jsonify({'error': 'Блюдо с таким названием уже существует'}), 400
                    updates.append('name = ?')
                    values.append(new_name)

            if 'description' in data:
                updates.append('description = ?')
                values.append(data['description'].strip())

            if 'category' in data:
                updates.append('category = ?')
                values.append(data['category'].strip())

            if 'price' in data:
                price = float(data['price'])
                if price <= 0:
                    return jsonify({'error': 'Цена должна быть положительной'}), 400
                updates.append('price = ?')
                values.append(price)

            if 'ingredients' in data:
                updates.append('ingredients = ?')
                values.append(data['ingredients'].strip())

            if 'allergens' in data:
                updates.append('allergens = ?')
                values.append(data['allergens'].strip())

            if 'calories' in data:
                updates.append('calories = ?')
                values.append(data['calories'])

            if 'quantity' in data:
                quantity = int(data['quantity'])
                if quantity < 0:
                    return jsonify({'error': 'Количество не может быть отрицательным'}), 400
                updates.append('quantity = ?')
                updates.append('is_available = ?')
                values.append(quantity)
                values.append(1 if quantity > 0 else 0)

            if 'is_available' in data:
                updates.append('is_available = ?')
                values.append(1 if data['is_available'] else 0)

            if not updates:
                return jsonify({'error': 'Нет данных для обновления'}), 400

            values.append(dish_id)
            update_query = f'UPDATE dishes SET {", ".join(updates)} WHERE id = ?'
            cursor.execute(update_query, values)
            db.commit()

            cursor.execute('SELECT * FROM dishes WHERE id = ?', (dish_id,))
            updated_dish = cursor.fetchone()

            return jsonify({
                'success': True,
                'message': f'Блюдо "{updated_dish["name"]}" обновлено',
                'dish': dict(updated_dish)
            })

        elif request.method == 'DELETE':
            cursor.execute('SELECT COUNT(*) FROM orders WHERE dish_id = ? AND status = "pending"',
                           (dish_id,))
            active_orders = cursor.fetchone()[0]

            if active_orders > 0:
                return jsonify({
                    'error': f'Нельзя удалить блюдо, есть {active_orders} активных заказов',
                    'suggestion': 'Сначала отмените заказы или отметьте блюдо как недоступное'
                }), 400

            cursor.execute('DELETE FROM dishes WHERE id = ?', (dish_id,))
            db.commit()

            print(f"🗑️ Администратор {user['username']} удалил блюдо: {dish['name']}")

            return jsonify({
                'success': True,
                'message': f'Блюдо "{dish["name"]}" удалено из меню'
            })

    except ValueError as e:
        return jsonify({'error': 'Неверный формат данных'}), 400
    except Exception as e:
        print(f"Ошибка управления блюдом: {e}")
        return jsonify({'error': 'Ошибка управления блюдом'}), 500

@app.route('/api/dishes/<int:dish_id>/toggle', methods=['POST', 'OPTIONS'])
def toggle_dish_availability(dish_id):
    """Быстрое переключение доступности блюда"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user or user['role'] != 2:
            return jsonify({'error': 'Только администратор может управлять блюдами'}), 403

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM dishes WHERE id = ?', (dish_id,))
        dish = cursor.fetchone()

        if not dish:
            return jsonify({'error': 'Блюдо не найдено'}), 404

        # Переключаем доступность
        new_status = 0 if dish['is_available'] else 1
        cursor.execute('UPDATE dishes SET is_available = ? WHERE id = ?',
                       (new_status, dish_id))
        db.commit()

        status_text = "доступно" if new_status else "недоступно"

        return jsonify({
            'success': True,
            'message': f'Блюдо "{dish["name"]}" теперь {status_text}',
            'is_available': bool(new_status)
        })

    except Exception as e:
        print(f"Ошибка переключения доступности: {e}")
        return jsonify({'error': 'Ошибка переключения доступности'}), 500


@app.route('/api/orders', methods=['POST', 'OPTIONS'])
def create_order():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        print("=" * 50)
        print("📦 ЗАПРОС НА СОЗДАНИЕ ЗАКАЗА")

        user = get_user_from_token()
        print("Пользователь из токена:", user['username'] if user else 'Нет пользователя')

        if not user:
            print("❌ Ошибка: Неавторизован")
            return jsonify({'error': 'Неавторизован'}), 401

        if user['role'] != 0:
            print(f"❌ Ошибка: Роль {user['role']} не может создавать заказы")
            return jsonify({'error': 'Только ученики могут создавать заказы'}), 403

        data = request.get_json()
        print("Данные заказа:", data)

        dish_id = data.get('dish_id')
        meal_type = data.get('meal_type', 'обед')
        payment_type = data.get('payment_type', 'разовый')

        if not dish_id:
            print("❌ Ошибка: Нет dish_id")
            return jsonify({'error': 'Укажите блюдо'}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM dishes WHERE id = ? AND is_available = 1 AND quantity > 0', (dish_id,))
        dish = cursor.fetchone()

        if not dish:
            print("❌ Ошибка: Блюдо недоступно")
            return jsonify({'error': 'Блюдо недоступно'}), 400

        if user['balance'] < dish['price']:
            print(f"❌ Ошибка: Недостаточно средств. Баланс: {user['balance']}, Цена: {dish['price']}")
            return jsonify({'error': 'Недостаточно средств'}), 400

        cursor.execute('''
                       INSERT INTO orders (user_id, dish_id, dish_name, price, meal_type, payment_type, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       ''', (user['id'], dish_id, dish['name'], dish['price'], meal_type, payment_type, 'pending'))

        order_id = cursor.lastrowid

        cursor.execute('UPDATE dishes SET quantity = quantity - 1 WHERE id = ?', (dish_id,))
        cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (dish['price'], user['id']))

        db.commit()

        print(f"✅ Заказ создан успешно, ID: {order_id}")
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': 'Заказ создан успешно'
        })

    except Exception as e:
        print(f"🔥 Ошибка создания заказа: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Ошибка создания заказа'}), 500

@app.route('/api/orders/my', methods=['GET', 'OPTIONS'])
def get_my_orders():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Неавторизован'}), 401

        db = get_db()
        cursor = db.cursor()

        if user['role'] == 0:
            cursor.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC', (user['id'],))
        elif user['role'] == 1:
            cursor.execute('''
                           SELECT o.*, u.full_name as user_name, u.class_name
                           FROM orders o
                                    JOIN users u ON o.user_id = u.id
                           WHERE o.status = 'pending'
                           ORDER BY o.order_date
                           ''')
        else:
            cursor.execute('''
                           SELECT o.*, u.full_name as user_name, u.class_name
                           FROM orders o
                                    JOIN users u ON o.user_id = u.id
                           ORDER BY o.order_date DESC
                           ''')

        orders = cursor.fetchall()

        return jsonify([dict(order) for order in orders])

    except Exception as e:
        print(f"Ошибка получения заказов: {e}")
        return jsonify({'error': 'Ошибка получения заказов'}), 500

@app.route('/api/orders/<int:order_id>/cancel', methods=['POST', 'OPTIONS'])
def cancel_order(order_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Неавторизован'}), 401

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()

        if not order:
            return jsonify({'error': 'Заказ не найден'}), 404

        if user['role'] == 0 and order['user_id'] != user['id']:
            return jsonify({'error': 'Недостаточно прав'}), 403

        if user['role'] == 1 and order['status'] != 'pending':
            return jsonify({'error': 'Повар может отменять только ожидающие заказы'}), 400

        if order['status'] != 'pending':
            return jsonify({'error': 'Можно отменять только ожидающие заказы'}), 400

        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', ('cancelled', order_id))

        if order['status'] == 'pending':
            cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?',
                           (order['price'], order['user_id']))
            cursor.execute('UPDATE dishes SET quantity = quantity + 1 WHERE id = ?',
                           (order['dish_id'],))

        db.commit()

        return jsonify({
            'success': True,
            'message': f'Заказ #{order_id} отменен'
        })

    except Exception as e:
        print(f"Ошибка отмены заказа: {e}")
        return jsonify({'error': 'Ошибка отмены заказа'}), 500



@app.route('/api/orders/<int:order_id>/serve', methods=['POST', 'OPTIONS'])
def serve_order(order_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user or user['role'] != 1:
            return jsonify({'error': 'Только повар может отмечать заказы как выданные'}), 403

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()

        if not order:
            return jsonify({'error': 'Заказ не найден'}), 404

        if order['status'] != 'pending':
            return jsonify({'error': 'Заказ уже обработан'}), 400

        cursor.execute('UPDATE orders SET status = ?, served_at = CURRENT_TIMESTAMP WHERE id = ?',
                       ('served', order_id))

        db.commit()

        return jsonify({
            'success': True,
            'message': f'Заказ #{order_id} отмечен как выданный'
        })

    except Exception as e:
        print(f"Ошибка отметки заказа: {e}")
        return jsonify({'error': 'Ошибка отметки заказа'}), 500




@app.route('/api/balance/topup', methods=['POST', 'OPTIONS'])
def topup_balance():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Неавторизован'}), 401

        if user['role'] != 0:
            return jsonify({'error': 'Только ученики могут пополнять баланс'}), 403

        data = request.get_json()
        amount = data.get('amount', 0)

        if amount <= 0:
            return jsonify({'error': 'Сумма должна быть положительной'}), 400

        if amount > 10000:
            return jsonify({'error': 'Сумма не может превышать 10000 руб.'}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user['id']))
        db.commit()

        cursor.execute('SELECT * FROM users WHERE id = ?', (user['id'],))
        updated_user = cursor.fetchone()

        return jsonify({
            'success': True,
            'message': f'Баланс пополнен на {amount} руб.',
            'new_balance': updated_user['balance']
        })

    except Exception as e:
        print(f"Ошибка пополнения баланса: {e}")
        return jsonify({'error': 'Ошибка пополнения баланса'}), 500



@app.route('/api/purchases', methods=['GET', 'OPTIONS'])
def get_purchases():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user or user['role'] not in [1, 2]:
            return jsonify({'error': 'Недостаточно прав'}), 403

        db = get_db()
        cursor = db.cursor()

        if user['role'] == 1:
            cursor.execute('''
                           SELECT pr.*, u.full_name as created_by_name
                           FROM purchase_requests pr
                                    JOIN users u ON pr.created_by = u.id
                           WHERE pr.created_by = ?
                           ORDER BY pr.created_at DESC
                           ''', (user['id'],))
        else:
            cursor.execute('''
                           SELECT pr.*, u1.full_name as created_by_name, u2.full_name as processed_by_name
                           FROM purchase_requests pr
                                    JOIN users u1 ON pr.created_by = u1.id
                                    LEFT JOIN users u2 ON pr.processed_by = u2.id
                           ORDER BY pr.status, pr.created_at DESC
                           ''')

        requests = cursor.fetchall()

        return jsonify([dict(req) for req in requests])

    except Exception as e:
        print(f"Ошибка получения заявок: {e}")
        return jsonify({'error': 'Ошибка получения заявок'}), 500

@app.route('/api/purchases', methods=['POST', 'OPTIONS'])
def create_purchase():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user or user['role'] != 1:
            return jsonify({'error': 'Только повар может создавать заявки'}), 403

        data = request.get_json()
        dish_id = data.get('dish_id')
        dish_name = data.get('dish_name', '').strip()
        quantity = data.get('quantity', 1)
        reason = data.get('reason', '').strip()

        if not dish_name:
            return jsonify({'error': 'Укажите название блюда/продукта'}), 400

        if quantity <= 0:
            return jsonify({'error': 'Количество должно быть положительным'}), 400

        db = get_db()
        cursor = db.cursor()

        if dish_id:
            cursor.execute('SELECT * FROM dishes WHERE id = ?', (dish_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Блюдо не найдено'}), 404

        cursor.execute('''
                       INSERT INTO purchase_requests (created_by, dish_id, dish_name, quantity, reason, status)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', (user['id'], dish_id, dish_name, quantity, reason, 'pending'))

        request_id = cursor.lastrowid
        db.commit()

        return jsonify({
            'success': True,
            'request_id': request_id,
            'message': 'Заявка на закупку создана'
        })

    except Exception as e:
        print(f"Ошибка создания заявки: {e}")
        return jsonify({'error': 'Ошибка создания заявки'}), 500

@app.route('/api/purchases/<int:request_id>/approve', methods=['POST', 'OPTIONS'])
def approve_purchase(request_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user or user['role'] != 2:
            return jsonify({'error': 'Только админ может утверждать заявки'}), 403

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM purchase_requests WHERE id = ?', (request_id,))
        request_data = cursor.fetchone()

        if not request_data:
            return jsonify({'error': 'Заявка не найдена'}), 404

        if request_data['status'] != 'pending':
            return jsonify({'error': 'Заявка уже обработана'}), 400

        cursor.execute('''
                       UPDATE purchase_requests
                       SET status = ?, processed_at = CURRENT_TIMESTAMP, processed_by = ?
                       WHERE id = ?
                       ''', ('approved', user['id'], request_id))

        if request_data['dish_id']:
            cursor.execute('''
                           UPDATE dishes
                           SET quantity = quantity + ?
                           WHERE id = ?
                           ''', (request_data['quantity'], request_data['dish_id']))

        db.commit()

        return jsonify({
            'success': True,
            'message': 'Заявка утверждена'
        })

    except Exception as e:
        print(f"Ошибка утверждения заявки: {e}")
        return jsonify({'error': 'Ошибка утверждения заявки'}), 500

@app.route('/api/purchases/<int:request_id>/reject', methods=['POST', 'OPTIONS'])
def reject_purchase(request_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user or user['role'] != 2:
            return jsonify({'error': 'Только админ может отклонять заявки'}), 403

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM purchase_requests WHERE id = ?', (request_id,))
        request_data = cursor.fetchone()

        if not request_data:
            return jsonify({'error': 'Заявка не найдена'}), 404

        if request_data['status'] != 'pending':
            return jsonify({'error': 'Заявка уже обработана'}), 400

        cursor.execute('''
                       UPDATE purchase_requests
                       SET status = ?, processed_at = CURRENT_TIMESTAMP, processed_by = ?
                       WHERE id = ?
                       ''', ('rejected', user['id'], request_id))

        db.commit()

        return jsonify({
            'success': True,
            'message': 'Заявка отклонена'
        })

    except Exception as e:
        print(f"Ошибка отклонения заявки: {e}")
        return jsonify({'error': 'Ошибка отклонения заявки'}), 500


@app.route('/api/reports/summary', methods=['GET', 'OPTIONS'])
def get_reports_summary():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user or user['role'] != 2:
            return jsonify({'error': 'Только администратор может просматривать отчеты'}), 403

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT COUNT(*) as total_users FROM users')
        total_users = cursor.fetchone()['total_users']

        cursor.execute('SELECT COUNT(*) as total_orders FROM orders')
        total_orders = cursor.fetchone()['total_orders']

        cursor.execute('SELECT COUNT(*) as total_dishes FROM dishes')
        total_dishes = cursor.fetchone()['total_dishes']

        # Финансовая статистика
        cursor.execute('SELECT SUM(price) as total_revenue FROM orders WHERE status = "served"')
        total_revenue = cursor.fetchone()['total_revenue'] or 0

        cursor.execute('SELECT SUM(balance) as total_balance FROM users')
        total_balance = cursor.fetchone()['total_balance'] or 0

        cursor.execute('''
                       SELECT status, COUNT(*) as count
                       FROM orders
                       GROUP BY status
                       ''')
        orders_by_status = dict(cursor.fetchall())

        cursor.execute('''
                       SELECT d.category, COUNT(o.id) as order_count, SUM(o.price) as revenue
                       FROM orders o
                                JOIN dishes d ON o.dish_id = d.id
                       WHERE o.status = "served"
                       GROUP BY d.category
                       ''')
        categories_data = cursor.fetchall()

        cursor.execute('''
                       SELECT d.name, COUNT(o.id) as order_count, SUM(o.price) as revenue
                       FROM orders o
                                JOIN dishes d ON o.dish_id = d.id
                       WHERE o.status = "served"
                       GROUP BY d.id
                       ORDER BY order_count DESC
                           LIMIT 10
                       ''')
        popular_dishes = cursor.fetchall()

        cursor.execute('''
                       SELECT u.username, u.full_name, COUNT(o.id) as order_count, SUM(o.price) as total_spent
                       FROM orders o
                                JOIN users u ON o.user_id = u.id
                       WHERE o.status = "served"
                       GROUP BY u.id
                       ORDER BY total_spent DESC
                           LIMIT 10
                       ''')
        active_users = cursor.fetchall()

        cursor.execute('''
                       SELECT
                           DATE(order_date) as date,
                           COUNT(*) as order_count,
                           SUM(price) as daily_revenue
                       FROM orders
                       WHERE order_date >= DATE('now', '-7 days')
                       GROUP BY DATE(order_date)
                       ORDER BY date
                       ''')
        daily_stats = cursor.fetchall()

        cursor.execute('SELECT COUNT(*) as total_requests FROM purchase_requests')
        total_requests = cursor.fetchone()['total_requests']

        cursor.execute('''
                       SELECT status, COUNT(*) as count
                       FROM purchase_requests
                       GROUP BY status
                       ''')
        requests_by_status = dict(cursor.fetchall())

        return jsonify({
            'summary': {
                'total_users': total_users,
                'total_orders': total_orders,
                'total_dishes': total_dishes,
                'total_revenue': float(total_revenue),
                'total_balance': float(total_balance),
                'total_requests': total_requests
            },
            'orders': {
                'by_status': orders_by_status,
                'daily_stats': [dict(day) for day in daily_stats]
            },
            'categories': [dict(cat) for cat in categories_data],
            'popular_dishes': [dict(dish) for dish in popular_dishes],
            'active_users': [dict(user) for user in active_users],
            'purchase_requests': {
                'by_status': requests_by_status
            },
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Ошибка получения отчетов: {e}")
        return jsonify({'error': 'Ошибка получения отчетов'}), 500

@app.route('/api/reports/detailed', methods=['GET', 'OPTIONS'])
def get_detailed_report():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user or user['role'] != 2:
            return jsonify({'error': 'Только администратор может просматривать отчеты'}), 403

        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
                       SELECT
                           o.id,
                           o.order_date,
                           o.dish_name,
                           o.price,
                           o.status,
                           o.meal_type,
                           o.payment_type,
                           u.username,
                           u.full_name,
                           u.class_name
                       FROM orders o
                                JOIN users u ON o.user_id = u.id
                       ORDER BY o.order_date DESC
                           LIMIT 100
                       ''')
        detailed_orders = cursor.fetchall()

        cursor.execute('''
                       SELECT
                           u.id,
                           u.username,
                           u.full_name,
                           u.role,
                           u.class_name,
                           u.balance,
                           u.created_at,
                           COUNT(o.id) as total_orders,
                           SUM(CASE WHEN o.status = "served" THEN o.price ELSE 0 END) as total_spent
                       FROM users u
                                LEFT JOIN orders o ON u.id = o.user_id
                       GROUP BY u.id
                       ORDER BY u.created_at DESC
                       ''')
        detailed_users = cursor.fetchall()

        cursor.execute('''
                       SELECT
                           d.id,
                           d.name,
                           d.category,
                           d.price,
                           d.quantity,
                           d.rating,
                           d.rating_count,
                           COUNT(o.id) as order_count,
                           SUM(CASE WHEN o.status = "served" THEN o.price ELSE 0 END) as revenue
                       FROM dishes d
                                LEFT JOIN orders o ON d.id = o.dish_id
                       GROUP BY d.id
                       ORDER BY order_count DESC
                       ''')
        detailed_dishes = cursor.fetchall()

        return jsonify({
            'orders': [dict(order) for order in detailed_orders],
            'users': [dict(user) for user in detailed_users],
            'dishes': [dict(dish) for dish in detailed_dishes],
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Ошибка получения детального отчета: {e}")
        return jsonify({'error': 'Ошибка получения отчета'}), 500

@app.route('/api/reports/export', methods=['GET', 'OPTIONS'])
def export_reports():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        user = get_user_from_token()
        if not user or user['role'] != 2:
            return jsonify({'error': 'Только администратор может экспортировать отчеты'}), 403

        format_type = request.args.get('format', 'json')

        if format_type == 'csv':
            return jsonify({
                'success': True,
                'message': 'Экспорт в CSV будет реализован позже',
                'url': '#'
            })
        else:
            # Возвращаем JSON с данными
            return get_reports_summary()

    except Exception as e:
        print(f"Ошибка экспорта отчетов: {e}")
        return jsonify({'error': 'Ошибка экспорта отчетов'}), 500



@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM dishes')
        dish_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM orders')
        order_count = cursor.fetchone()[0]

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': {
                'users': user_count,
                'dishes': dish_count,
                'orders': order_count
            },
            'server': 'full_features'
        })

    except Exception as e:
        print(f"Ошибка health check: {e}")
        return jsonify({'error': 'Database error'}), 500





if __name__ == '__main__':
    init_db()

    print("=" * 60)
    print("🚀 ПОЛНЫЙ СЕРВЕР СО ВСЕМИ ФУНКЦИЯМИ")
    print("=" * 60)
    print("📡 Сервер запущен на http://localhost:5000")
    print("💾 База данных:", DATABASE)
    print("")
    print("👤 Тестовые аккаунты:")
    print("  • Ученик:   student1 / password123 (1000 руб.)")
    print("  • Повар:    cook1 / password123")
    print("  • Админ:    admin1 / password123")
    print("")
    print("📋 Функции по ролям:")
    print("  👨‍🎓 Ученик: заказ блюд, просмотр заказов, пополнение баланса")
    print("  👨‍🍳 Повар:   просмотр заказов, отметка выдачи, заявки на закупку")
    print("  👨‍💼 Админ:   все функции + управление заявками")
    print("=" * 60)

    app.run(debug=True, port=5000, host='0.0.0.0')