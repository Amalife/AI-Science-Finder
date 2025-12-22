import streamlit as st
from auth import init_db, check_credentials, register_user
from pages import show_description_page, show_search_page


def main():
    # Настройка страницы
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.set_page_config(layout="wide")
    else:
        st.set_page_config(layout="centered")

    # Добавление CSS для фона и светлого текста
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://raw.githubusercontent.com/dmshipov/streamlit-apps/main/ai_science_finder/orig-scaled.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: #FFFFFF;  /* Светлый цвет текста для видимости на фоне */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("AI Science Finder")
    
    # Инициализация БД
    init_db()
    
    # Инициализация сессии
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = None

    # Если пользователь вошёл, показываем страницу
    if st.session_state.logged_in:
        if st.session_state.page == "search":
            
            show_search_page()
        else:  # description
            # Кнопка "Выход" на странице описания

            
            show_description_page()
        return

    # Tabs для входа и регистрации
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])

    with tab1:
        st.subheader("Вход в систему")
        username = st.text_input("Логин", key="login_username")
        password = st.text_input("Пароль", type="password", key="login_password")
        
        if st.button("Войти"):
            if check_credentials(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "description"
                st.success("Успешный вход! Перенаправление...")
                st.rerun()
            else:
                st.error("Неверный логин или пароль.")

    with tab2:
        st.subheader("Регистрация нового пользователя")
        reg_username = st.text_input("Логин", key="reg_username")
        reg_password = st.text_input("Пароль", type="password", key="reg_password")
        confirm_password = st.text_input("Подтвердите пароль", type="password", key="confirm_password")
        
        if st.button("Зарегистрироваться"):
            if reg_password != confirm_password:
                st.error("Пароли не совпадают.")
            else:
                success, message = register_user(reg_username, reg_password)
                if success:
                    st.success(message)
                    st.info("Теперь перейдите во вкладку 'Вход' и авторизуйтесь.")
                else:
                    st.error(message)

if __name__ == "__main__":
    main()
