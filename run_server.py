import subprocess
import sys
import os

def run_backend():

    print("🚀 Запуск бэкенда Flask...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')


    if os.path.exists(os.path.join(backend_dir, 'venv')):
        if sys.platform == 'win32':
            activate_script = os.path.join(backend_dir, 'venv', 'Scripts', 'activate')
            python_exe = os.path.join(backend_dir, 'venv', 'Scripts', 'python')
        else:
            activate_script = os.path.join(backend_dir, 'venv', 'bin', 'activate')
            python_exe = os.path.join(backend_dir, 'venv', 'bin', 'python')
    else:
        python_exe = sys.executable


    os.chdir(backend_dir)
    subprocess.Popen([python_exe, 'working_server.py'])
    print("✅ Бэкенд запущен на http://localhost:5000")

def open_frontend():
    print("\n🌐 Открытие фронтенда...")
    index_file = os.path.join(os.path.dirname(__file__), 'index.html')

    if os.path.exists(index_file):
        import webbrowser

        print("📁 Запуск локального сервера для статических файлов...")

        frontend_dir = os.path.dirname(__file__)
        os.chdir(frontend_dir)


        http_server = subprocess.Popen([sys.executable, '-m', 'http.server', '8000'])

        webbrowser.open('http://localhost:8000')
        print("✅ Фронтенд открыт в браузере")

        return http_server
    else:
        print("❌ Файл index.html не найден")
        return None

def main():

    print("=" * 60)
    print("🏫 ШКОЛЬНАЯ СТОЛОВАЯ - СИСТЕМА УПРАВЛЕНИЯ")
    print("=" * 60)

    try:

        run_backend()


        import time
        time.sleep(2)


        http_server = open_frontend()

        print("\n" + "=" * 60)
        print("✅ Система запущена!")
        print("🔗 Бэкенд: http://localhost:5000")
        print("🔗 Фронтенд: http://localhost:8000")
        print("👤 Тестовый аккаунт: student1 / password123")
        print("=" * 60)
        print("\nДля остановки нажмите Ctrl+C")


        if http_server:
            http_server.wait()

    except KeyboardInterrupt:
        print("\n👋 Остановка системы...")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == '__main__':
    main()