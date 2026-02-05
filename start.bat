     @echo off
     chcp 65001 > nul
     echo ========================================
     echo    ШКОЛЬНАЯ СТОЛОВАЯ - СИСТЕМА УПРАВЛЕНИЯ
     echo ========================================
     echo.

     echo [1/3] Проверяем Python...
     python --version
     if errorlevel 1 (
         echo ОШИБКА: Python не установлен или не добавлен в PATH
         pause
         exit /b 1
     )

     echo.
     echo [2/3] Запуск бэкенда (API сервера)...
     cd backend
     start "Бэкенд сервер" cmd /k "python app.py"
     cd ..

     echo.
     echo [3/3] Ожидание запуска сервера (5 секунд)...
     timeout /t 5 /nobreak > nul

     echo.
     echo [4/4] Запуск фронтенда (веб-сервера)...
     start "Веб-сервер" cmd /k "python -m http.server 8000"

     timeout /t 3 /nobreak > nul

     echo.
     echo ========================================
     echo            СИСТЕМА ЗАПУЩЕНА!
     echo ========================================
     echo API сервер:    http://localhost:5000
     echo Веб-интерфейс: http://localhost:8000
     echo.
     echo Тестовые аккаунты:
     echo   Ученик:  student1 / password123 (1000 руб.)
     echo   Повар:   cook1 / password123
     echo   Админ:   admin1 / password123
     echo ========================================
     echo.

     :menu
     echo Выберите действие:
     echo   1. Открыть систему в браузере
     echo   2. Проверить работу API
     echo   3. Остановить все серверы
     echo   4. Выход
     echo.
     set /p choice="Введите номер (1-4): "

     if "%choice%"=="1" (
         start http://localhost:8000
         goto menu
     )

     if "%choice%"=="2" (
         start http://localhost:5000/api/health
         goto menu
     )

     if "%choice%"=="3" (
         taskkill /f /im python.exe 2>nul
         taskkill /f /im cmd.exe 2>nul
         echo Все серверы остановлены
         pause
         exit
     )

     if "%choice%"=="4" (
         exit
     )

     echo Неверный выбор!
     goto menu