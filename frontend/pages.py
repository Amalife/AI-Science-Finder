import streamlit as st
import requests


# Функция для страницы описания сервиса
def show_description_page():
    st.title("Добро пожаловать в систему поиска научных статей!")
    st.write(f"Привет, {st.session_state.username}!")
    
    st.subheader("Описание сервиса")
    st.write("""
    **Интеллектуальный поиск научных статей** с использованием семантического анализа и гибридного поиска на основе Elasticsearch.
    
    - Преобразует запрос в векторное представление для поиска по смыслу, а не по словам.
    - Комбинирует семантический и полнотекстовый поиск для высокой релевантности.
    - Фильтрация по дате, автору, тегам и типу контента.
    - Отображение результатов с аннотациями, метаданными и оценкой релевантности.
    - Поддержка пагинации и обработки edge-кейсов (пустые запросы, отсутствие результатов).
    - Оптимизации: кэширование эмбеддингов, асинхронная обработка, мониторинг.
    
    Процесс: предобработка текста, векторизация (Sentence-Transformers/BERT), поиск соседей и ранжирование.
    """)
    
    # Кнопка для перехода на страницу поиска
    if st.button("Перейти к поиску статей"):
        st.session_state.page = "search"
        st.rerun()

# Функция для страницы поиска статей
# def show_search_page():
#     st.title("Поиск научных статей")
#     st.write(f"Привет, {st.session_state.username}! Здесь вы можете искать статьи.")
    
#     # Фильтры
#     st.subheader("Фильтры")
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         author_filter = st.text_input("Автор", key="author_filter")
#     with col2:
#         date_from = st.date_input("Дата от", value=None, key="date_from")
#     with col3:
#         date_to = st.date_input("Дата до", value=None, key="date_to")
#     with col4:
#         title_filter = st.text_input("Название", key="title_filter")
    
#     # Простой поиск
#     st.subheader("Поиск")
#     query = st.text_input("Введите запрос (например, 'машинное обучение в медицине')", key="query")
#     if st.button("Найти", key="search_btn"):
#         if query.strip():
#             st.write(f"Результаты поиска по запросу: '{query}'")
            
#             # Пример результатов с ссылками
#             results = [
#                 {
#                     "id": "art_001",
#                     "title": "Применение глубокого обучения для диагностики рака",
#                     "url": "https://example.com/article1",
#                     "abstract": "Исследование показывает эффективность CNN...",
#                     "similarity_score": 0.92,
#                     "metadata": {
#                         "author": "Иванов А.И.",
#                         "published_date": "2023-05-15",
#                         "tags": ["медицина", "нейросети", "онкология"]
#                     }
#                 },
#                 {
#                     "id": "art_002",
#                     "title": "Машинное обучение в кардиологии",
#                     "url": "https://example.com/article2",
#                     "abstract": "Обзор методов предсказания сердечных заболеваний...",
#                     "similarity_score": 0.88,
#                     "metadata": {
#                         "author": "Петров Б.Б.",
#                         "published_date": "2023-07-20",
#                         "tags": ["медицина", "машинное обучение", "кардиология"]
#                     }
#                 },
#                 {
#                     "id": "art_003",
#                     "title": "ИИ в онкологии",
#                     "url": "https://example.com/article3",
#                     "abstract": "Новые подходы к использованию ИИ в лечении рака...",
#                     "similarity_score": 0.85,
#                     "metadata": {
#                         "author": "Сидоров В.В.",
#                         "published_date": "2024-01-10",
#                         "tags": ["онкология", "ИИ"]
#                     }
#                 }
#             ]
            
#             # Фильтрация результатов
#             filtered_results = []
#             for res in results:
#                 # Фильтр по автору
#                 if author_filter and author_filter.lower() not in res['metadata']['author'].lower():
#                     continue
#                 # Фильтр по датам
#                 pub_date = datetime.strptime(res['metadata']['published_date'], '%Y-%m-%d').date()
#                 if date_from and pub_date < date_from:
#                     continue
#                 if date_to and pub_date > date_to:
#                     continue
#                 # Фильтр по названию
#                 if title_filter and title_filter.lower() not in res['title'].lower():
#                     continue
#                 filtered_results.append(res)
            
#             # Отображение результатов
#             if filtered_results:
#                 st.write("**Найденные статьи:**")
#                 for res in filtered_results:
#                     col1, col2 = st.columns([3, 1])
#                     with col1:
#                         # Ссылка на статью
#                         st.markdown(f"**[{res['title']}]({res['url']})** (Релевантность: {res['similarity_score']})")
#                         st.write(f"Автор: {res['metadata']['author']}, Дата: {res['metadata']['published_date']}, Теги: {', '.join(res['metadata']['tags'])}")
#                     with col2:
#                         # Раскрывающаяся анотация
#                         with st.expander("Анотация"):
#                             st.write(res['abstract'])
#                     st.divider()
#             else:
#                 st.info("Нет результатов, соответствующих фильтрам.")
            
#             st.info("В реальном сервисе здесь будут актуальные результаты из базы данных.")
#         else:
#             st.warning("Введите запрос для поиска.")
    
#     # Кнопка выхода
#     if st.button("Выход", key="logout_btn"):
#         st.session_state.logged_in = False
#         st.session_state.page = None
#         del st.session_state.username
#         st.rerun()

# Функция для страницы поиска статей
def show_search_page():
    st.title("Поиск научных статей")
    st.write(f"Привет, {st.session_state.username}! Здесь вы можете искать статьи.")
    
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
        # Title filter пока реализуем на клиенте или нужно добавить в backend, 
        # для семантического поиска он менее актуален, но оставим поле.
        title_filter = st.text_input("Название (доп. фильтр)", key="title_filter")
    
    # Поиск
    st.subheader("Поиск")
    query = st.text_input("Введите запрос (например, 'машинное обучение в медицине')", key="query")
    
    if st.button("Найти", key="search_btn"):
        if query.strip():
            with st.spinner('ИИ анализирует базу знаний...'):
                try:
                    # Подготовка данных для API
                    payload = {
                        "query": query,
                        "top_k": 5,
                        "author_filter": author_filter if author_filter else None,
                        "date_from": str(date_from) if date_from else None,
                        "date_to": str(date_to) if date_to else None
                    }

                    # Запрос к Backend API
                    response = requests.post("http://localhost:8000/search", json=payload)
                    
                    if response.status_code == 200:
                        results = response.json()
                        st.success(f"Найдено результатов: {len(results)}")
                        
                        if results:
                            st.write("**Найденные статьи:**")
                            for res in results:
                                # Дополнительная клиентская фильтрация по названию (если нужно)
                                if title_filter and title_filter.lower() not in res['title'].lower():
                                    continue
                                    
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    score_percent = round(res['similarity_score'] * 100, 1) # Условная конвертация для наглядности
                                    st.markdown(f"**[{res['title']}]({res['url']})**")
                                    st.caption(f"Релевантность: {res['similarity_score']:.4f}")
                                    st.write(f"✍️ {res['metadata']['author']} | 📅 {res['metadata']['published_date']}")
                                    st.write(f"🏷️Tags: {', '.join(res['metadata']['tags'])}")
                                with col2:
                                    with st.expander("Аннотация"):
                                        st.write(res['abstract'])
                                st.divider()
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
    # Кнопка выхода
    if st.button("Выход", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.page = None
        del st.session_state.username
        st.rerun()