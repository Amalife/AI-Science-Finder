# AI Science Finder

## Установка
1. Склонируйте репозиторий
2. Создайте чистое python окружение и подключитесь к нему
3. Установите зависимости
```bash
pip install -U pip
pip install -r requirements.txt
```

4. Создать копию файла .env.example и назвать .env. Добавить настройки доступа к GigaChat API:
```
MODEL_NAME=...
GIGACHAT_CREDENTIALS=...
GIGACHAT_SCOPE=...
GIGACHAT_VERIFY_SSL=...
```

DATA_CSV_FILENAME - Имя файла с данными в папке data 
DATA_MAPPING_FILENAME - Имя файла с маппингом для векторной БД в папке data

5. Заполнение векторной базы данных

5.1 Запуск векторной базы данных
```bash
docker compose -f docker-compose.yml up -d
```
5.2 Запуск скрипта заполения
```bash
python fill_vdb.py
```

5. Запуск сервиса

6.1 Запуск векторной базы данных
```bash
docker compose -f docker-compose.yml up -d
```
6.2 Запуск Бекэнда приложения
```bash
python main.py
```
6.3 Запуск Фронтэнда приложения (в новом терминале)
```bash
streamlit run frontend/main.py
```
6. Откройте в браузере http://localhost:8501/