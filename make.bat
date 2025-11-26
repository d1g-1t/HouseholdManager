@echo off
REM Makefile.bat - Windows equivalent of Makefile for HouseholdManager
REM Usage: make.bat <command>

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="setup" goto setup
if "%1"=="docker-setup" goto docker-setup
if "%1"=="install" goto install
if "%1"=="dev-setup" goto dev-setup
if "%1"=="run" goto run
if "%1"=="celery-worker" goto celery-worker
if "%1"=="celery-beat" goto celery-beat
if "%1"=="flower" goto flower
if "%1"=="shell" goto shell
if "%1"=="migrate" goto migrate
if "%1"=="makemigrations" goto makemigrations
if "%1"=="createsuperuser" goto createsuperuser
if "%1"=="test" goto test
if "%1"=="test-cov" goto test-cov
if "%1"=="lint" goto lint
if "%1"=="format" goto format
if "%1"=="check" goto check
if "%1"=="docker-up" goto docker-up
if "%1"=="docker-down" goto docker-down
if "%1"=="docker-restart" goto docker-restart
if "%1"=="docker-logs" goto docker-logs
if "%1"=="docker-clean" goto docker-clean
if "%1"=="clean" goto clean
goto help

:help
echo.
echo [94mHouseholdManager - Available Commands[0m
echo.
echo [92mSetup ^& Installation:[0m
echo   make.bat setup              - Complete project setup (local)
echo   make.bat docker-setup       - Complete project setup (Docker)
echo   make.bat install            - Install Python dependencies only
echo   make.bat dev-setup          - Setup development tools
echo.
echo [92mDevelopment:[0m
echo   make.bat run                - Run Django development server
echo   make.bat celery-worker      - Run Celery worker
echo   make.bat celery-beat        - Run Celery beat scheduler
echo   make.bat flower             - Run Celery Flower monitoring
echo   make.bat shell              - Open Django shell
echo.
echo [92mDatabase:[0m
echo   make.bat migrate            - Run database migrations
echo   make.bat makemigrations     - Create new migrations
echo   make.bat createsuperuser    - Create Django superuser
echo.
echo [92mDocker:[0m
echo   make.bat docker-up          - Start all Docker services
echo   make.bat docker-down        - Stop all Docker services
echo   make.bat docker-restart     - Restart Docker services
echo   make.bat docker-logs        - Show Docker logs
echo   make.bat docker-clean       - Clean Docker volumes and images
echo.
echo [92mTesting ^& Quality:[0m
echo   make.bat test               - Run all tests
echo   make.bat test-cov           - Run tests with coverage
echo   make.bat lint               - Run linters
echo   make.bat format             - Format code
echo   make.bat check              - Run all quality checks
echo.
echo [92mUtilities:[0m
echo   make.bat clean              - Clean temporary files
echo.
goto end

:setup
echo [94mStarting complete project setup...[0m
call :check-dependencies
call :create-env
call :install-deps
call :create-dirs
call :migrate-db
call :collectstatic
call :setup-complete
goto end

:check-dependencies
echo [94mChecking dependencies...[0m
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [91mPython is not installed![0m
    exit /b 1
)
where poetry >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [93mPoetry not found. Installing...[0m
    curl -sSL https://install.python-poetry.org | python -
)
where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [93mWarning: PostgreSQL not found. Install it manually or use Docker.[0m
)
where redis-cli >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [93mWarning: Redis not found. Install it manually or use Docker.[0m
)
where tesseract >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [93mWarning: Tesseract OCR not found. Install it for receipt processing.[0m
)
exit /b 0

:create-env
echo [94mCreating environment file...[0m
if not exist .env (
    copy .env.example .env
    echo [92m✓ .env file created. Please update it with your configuration.[0m
) else (
    echo [93m✓ .env file already exists.[0m
)
exit /b 0

:install-deps
echo [94mInstalling Python dependencies...[0m
poetry install
echo [92m✓ Dependencies installed.[0m
exit /b 0

:create-dirs
echo [94mCreating necessary directories...[0m
if not exist media mkdir media
if not exist staticfiles mkdir staticfiles
if not exist logs mkdir logs
if not exist ml_models mkdir ml_models
if not exist credentials mkdir credentials
if not exist backups mkdir backups
echo [92m✓ Directories created.[0m
exit /b 0

:migrate-db
echo [94mRunning database migrations...[0m
poetry run python manage.py migrate
echo [92m✓ Migrations applied.[0m
exit /b 0

:collectstatic
echo [94mCollecting static files...[0m
poetry run python manage.py collectstatic --noinput
echo [92m✓ Static files collected.[0m
exit /b 0

:setup-complete
echo.
echo [92m═══════════════════════════════════════════════[0m
echo [92m  ✓ Setup completed successfully![0m
echo [92m═══════════════════════════════════════════════[0m
echo.
echo [94mNext steps:[0m
echo   1. Update .env file with your configuration
echo   2. Create superuser: make.bat createsuperuser
echo   3. Run development server: make.bat run
echo.
echo [94mOr use Docker:[0m
echo   make.bat docker-setup
echo.
exit /b 0

:docker-setup
echo [94mStarting Docker project setup...[0m
call :create-env
call :docker-build
call :docker-up
timeout /t 5 /nobreak >nul
call :docker-migrate
call :docker-superuser-prompt
call :docker-setup-complete
goto end

:docker-build
echo [94mBuilding Docker images...[0m
docker-compose build
echo [92m✓ Docker images built.[0m
exit /b 0

:docker-up
echo [94mStarting Docker services...[0m
docker-compose up -d
echo [92m✓ Docker services started.[0m
exit /b 0

:docker-migrate
echo [94mRunning migrations in Docker...[0m
docker-compose exec -T web python manage.py migrate
echo [92m✓ Migrations applied.[0m
exit /b 0

:docker-superuser-prompt
echo.
set /p answer="Would you like to create a superuser? (y/n): "
if /i "%answer%"=="y" (
    docker-compose exec web python manage.py createsuperuser
)
exit /b 0

:docker-setup-complete
echo.
echo [92m═══════════════════════════════════════════════[0m
echo [92m  ✓ Docker setup completed successfully![0m
echo [92m═══════════════════════════════════════════════[0m
echo.
echo [94mServices available at:[0m
echo   - API Docs:    http://localhost:8000/api/docs
echo   - Admin:       http://localhost:8000/admin
echo   - Flower:      http://localhost:5555
echo   - pgAdmin:     http://localhost:5050
echo   - Prometheus:  http://localhost:9090
echo   - Grafana:     http://localhost:3000
echo.
exit /b 0

:install
echo [94mInstalling dependencies...[0m
poetry install
goto end

:dev-setup
echo [94mSetting up development tools...[0m
poetry install --with dev
poetry run pre-commit install
echo [92m✓ Development tools installed.[0m
goto end

:run
echo [94mStarting Django development server...[0m
poetry run python manage.py runserver
goto end

:celery-worker
echo [94mStarting Celery worker...[0m
poetry run celery -A household_manager worker -l info -Q default,ocr,ml,notifications -c 4
goto end

:celery-beat
echo [94mStarting Celery beat scheduler...[0m
poetry run celery -A household_manager beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
goto end

:flower
echo [94mStarting Celery Flower...[0m
poetry run celery -A household_manager flower --port=5555
goto end

:shell
poetry run python manage.py shell_plus --ipython
goto end

:migrate
echo [94mRunning migrations...[0m
poetry run python manage.py migrate
echo [92m✓ Migrations applied.[0m
goto end

:makemigrations
echo [94mCreating migrations...[0m
poetry run python manage.py makemigrations
echo [92m✓ Migrations created.[0m
goto end

:createsuperuser
poetry run python manage.py createsuperuser
goto end

:test
echo [94mRunning tests...[0m
poetry run pytest
goto end

:test-cov
echo [94mRunning tests with coverage...[0m
poetry run pytest --cov=apps --cov-report=html --cov-report=term
echo [92m✓ Coverage report generated at htmlcov/index.html[0m
goto end

:lint
echo [94mRunning linters...[0m
poetry run ruff check apps household_manager
poetry run mypy apps household_manager
goto end

:format
echo [94mFormatting code...[0m
poetry run black apps household_manager
poetry run isort apps household_manager
echo [92m✓ Code formatted.[0m
goto end

:check
call :format
call :lint
call :test
echo [92m✓ All checks passed![0m
goto end

:docker-down
echo [94mStopping Docker services...[0m
docker-compose down
echo [92m✓ Docker services stopped.[0m
goto end

:docker-restart
echo [94mRestarting Docker services...[0m
docker-compose restart
echo [92m✓ Docker services restarted.[0m
goto end

:docker-logs
docker-compose logs -f
goto end

:docker-clean
echo [91mWarning: This will remove all containers, volumes, and images![0m
set /p answer="Are you sure? (y/n): "
if /i "%answer%"=="y" (
    docker-compose down -v --remove-orphans
    docker system prune -af --volumes
    echo [92m✓ Docker cleaned.[0m
) else (
    echo [94mCancelled.[0m
)
goto end

:clean
echo [94mCleaning temporary files...[0m
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r . %%f in (*.pyc *.pyo) do @if exist "%%f" del /q "%%f"
for /d /r . %%d in (*.egg-info) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.mypy_cache) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.ruff_cache) do @if exist "%%d" rd /s /q "%%d"
if exist htmlcov rd /s /q htmlcov
if exist .coverage del /q .coverage
echo [92m✓ Temporary files cleaned.[0m
goto end

:end
