import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from core.utils import load_json, save_json
from core.models import User, Portfolio

USERS_FILE = "users.json"
PORTFOLIOS_FILE = "portfolios.json"

SALT = "haleluya2003"

def register(username, password):
    if not username:
        return "Ошибка: username не может быть пустым."
    if len(password) < 4:
        return "Ошибка: пароль должен быть длиной не менее 4 символов."
    
    user_data = load_json(USERS_FILE)
    if user_data:
        for i in user_data:
            if i['username'] == username:
                return f"Ошибка: пользователь '{username}' уже существует."
        
    user_id = len(user_data) + 1

    user_model = User(user_id=user_id, username=username, password=password, salt=SALT)
    
    user_model_data = {
        "user_id": user_model._user_id,
        "username": user_model._username,
        "hashed_password": user_model._hashed_password,
        "salt": user_model._salt,
        "registration_date": user_model._registration_date.isoformat()
    }
    user_data.append(user_model_data)
    
    
    portfolio_data = load_json(PORTFOLIOS_FILE)
    
    portfolio_model = Portfolio(user_id=user_id, wallets={})
    
    portfolio_model_data = {
        "user_id": portfolio_model._user_id,
        "wallets": {}
    }
    portfolio_data.append(portfolio_model_data)
    
    save_json(PORTFOLIOS_FILE, portfolio_data)
    save_json(USERS_FILE, user_data)
    
    msg = f"Пользователь '{user_model._username}' зарегистрирован (id={user_model._user_id}). Войдите: login --username {user_model._username} --password ****"
    return msg
