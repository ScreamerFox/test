Запуск произовдится из файла main.py в папке app.
модели и схемы лежат в файле models,
для для запуска приложения нужно создать файл .env в корне проекта с переменной DATABASE_URL=postgresql+asyncpg://"USERNAME":"PASSWORD"@localhost:5432/wallet_db, заменить username и password на соответствующие.
