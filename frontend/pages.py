import streamlit as st
import requests
import os


# Функция для страницы описания сервиса
def show_description_page():
    st.title("Добро пожаловать в систему поиска научных статей!")
    st.write(f"Привет, {st.session_state.username}!")
    
    st.subheader("Описание сервиса")
    st.write("""
    **Интеллектуальный поиск научных статей** с использованием семантического анализа и поиска на основе Elasticsearch.
    
    - Преобразует запрос в векторное представление для поиска по смыслу, а не по словам.
    - Фильтрация по дате, автору, тегам и типу контента.
    - Отображение результатов с аннотациями, метаданными и оценкой релевантности.
    - Поддержка пагинации и обработки edge-кейсов (пустые запросы, отсутствие результатов).
    - Оптимизации: асинхронная обработка, мониторинг.
    
    Процесс: предобработка текста, векторизация, поиск соседей и ранжирование.
    """)
    
        # Кнопки для перехода
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Перейти к поиску статей"):
            st.session_state.page = "search"
            st.rerun()
    with col2:
        if st.button("Перейти к загрузке файлов"):
            st.session_state.page = "upload"
            st.rerun()

    if st.button("Выйти из аккаунта"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = None
        st.rerun()

# Функция для страницы загрузки файлов
def show_upload_page():
    st.title("Загрузка файлов для анализа AI-агентом")
    st.write(f"Привет, {st.session_state.username}! Здесь вы можете загрузить файлы для анализа.")
    
    st.subheader("Загрузка файла")
    uploaded_file = st.file_uploader(
        "Выберите файл для загрузки (PDF)",
        type=['pdf'],  # Расширения файлов
        help="Файл будет временно сохранён и передан на анализ AI-агенту."
    )
    
    if uploaded_file is not None:
        # Сохранение файла в временную папку
        file_details = {"filename": uploaded_file.name, "filetype": uploaded_file.type, "filesize": uploaded_file.size}
        st.write("**Детали файла:**")
        st.json(file_details)
        
        # Сохранение файла
        os.makedirs("temp_uploads", exist_ok=True)
        temp_path = os.path.join("temp_uploads", uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Файл '{uploaded_file.name}' успешно загружен!")
        
        # Отправка файла на бэкэнд для обработки
        if st.button("Обработать и добавить в базу", key="process_btn"):
            with st.spinner("Обработка PDF и добавление в базу..."):
                try:
                    with open(temp_path, "rb") as f:
                        files = {"file": (uploaded_file.name, f, uploaded_file.type)}
                        response = requests.post("http://localhost:8000/upload_pdf", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(result["message"])
                        # Удаление временного файла
                        os.remove(temp_path)
                    else:
                        st.error(f"Ошибка обработки: {response.text}")
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
    
    # # Placeholder для анализа (поскольку бэкэнд агента добавят позже)
    # if st.button("Анализировать файл", key="analyze_btn"):
    #     st.info("Анализ файла запущен... (Бэкэнд AI-агента будет добавлен позже.)")
    #     # Здесь можно добавить placeholder-результаты
    #     st.subheader("Результаты анализа (пример)")
    #     st.write("""
    #     - **Сводка:** Документ описывает применение машинного обучения в медицине.
    #     - **Ключевые идеи:** Диагностика рака с помощью нейросетей, предсказание заболеваний.
    #     - **Рекомендации:** Проверьте статьи по теме 'ИИ в онкологии'.
    #     """)
    # Кнопка выхода или перехода
    if st.button("Вернуться к описанию", key="back_to_desc"):
        st.session_state.page = "description"
        st.rerun()
    if st.button("Выход", key="logout_upload"):
        st.session_state.logged_in = False
        st.session_state.page = None
        del st.session_state.username
        st.rerun()

# Функция для страницы поиска статей
def show_search_page():
    st.title("Поиск научных статей")
    st.write(f"Привет, {st.session_state.username}! Здесь вы можете искать статьи.")
    
    # Initialize session state for results
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    
    # Фильтры
    st.subheader("Фильтры")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        author_filter = st.text_input("Автор", key="author_filter")
    with col2:
        date_from = st.date_input("Дата от", value=None, key="date_from")
    with col3:
        date_to = st.date_input("Дата до", value=None, key="date_to")
    with col4:
        tags_filter = st.text_input("Теги", key="tags_filter")
    
    # Поиск
    st.subheader("Поиск")
    # Создаём два столбца, чтобы поле ввода занимало ширину одного столбца (в два раза меньше)
    col1, col2 = st.columns(2)
    with col1:
        query = st.text_input("Введите запрос (например, 'машинное обучение в медицине')", key="query")
    
    if st.button("Начать поиск", key="search_btn"):
        if query.strip():
            with st.spinner('ИИ анализирует базу знаний...'):
                try:
                    # Подготовка данных для API
                    payload = {
                        "query": query,
                        "top_k": 5,
                        "author_filter": author_filter if author_filter else None,
                        "date_from": str(date_from) if date_from else None,
                        "date_to": str(date_to) if date_to else None,
                        "tags_filter": tags_filter if tags_filter else None
                    }

                    # Запрос к Backend API
                    response = requests.post("http://localhost:8000/search", json=payload)
                    
                    if response.status_code == 200:
                        results = response.json()
                        st.success(f"Найдено результатов: {len(results)}")
                        
                        if results:
                            st.session_state.search_results = results
                        else:
                            st.info("По вашему запросу ничего не найдено в векторной базе.")
                    else:
                        st.error(f"Ошибка сервера: {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Не удалось подключиться к серверу поиска (Backend недоступен).")
                except Exception as e:
                    st.error(f"Произошла ошибка: {str(e)}")
        else:
            st.warning("Введите запрос для поиска.")
    
    if st.session_state.search_results:
        st.write("**Найденные статьи:**")
        for res in st.session_state.search_results:
            col1, col2 = st.columns([3, 1])
            with col1:
                score_percent = round(res['similarity_score'] * 100, 1) # Условная конвертация для наглядности
                st.link_button(res['title'], res['url'])
                st.caption(f"Релевантность: {res['similarity_score']:.4f}")
                st.write(f"✍️ {res['metadata']['author']} | 📅 {res['metadata']['published_date']}")
                st.write(f"🏷️Tags: {', '.join(res['metadata']['tags'])}")
            with col2:
                with st.expander("Аннотация"):
                    st.write(res['abstract'])
            st.divider()

    # Кнопка назад к описанию
    if st.button("Вернуться к описанию"):
        st.session_state.page = "description"
        st.rerun()

    # Кнопка выхода
    if st.button("Выйти из аккаунта", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.page = None
        del st.session_state.username
        st.rerun()
