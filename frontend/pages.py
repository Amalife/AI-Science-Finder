import streamlit as st
import requests


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
    
    # Кнопка для перехода на страницу поиска
    if st.button("Перейти к поиску статей"):
        st.session_state.page = "search"
        st.rerun()

    if st.button("Выйти из аккаунта"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = None
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
