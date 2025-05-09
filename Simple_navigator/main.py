import ttkbootstrap as ttk
from tkinter import messagebox
from db_utils import connect_to_database, register_user, login_user, history_save_db
from route_logic import calculate_route
from PIL import Image, ImageTk

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")



class StartWindow(ttk.Window):
    def __init__(self, db_path):
        super().__init__(title="Добро пожаловать!")
        self.db_path = db_path
        self.conn = None
        center_window(self, 300, 200)
        self.resizable(False, False)

        # Лэйбл заголовка
        ttk.Label(self, text="Выберите действие", font=("Arial", 14), anchor="center").grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")

        # Кнопка регистрации
        reg_button = ttk.Button(self, text="Регистрация", command=self.show_registration)
        reg_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Кнопка авторизации
        auth_button = ttk.Button(self, text="       Вход       ", command=self.show_login)
        auth_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Кнопка для выхода
        exit_button = ttk.Button(self, text="Выйти", command=self.exit_program, bootstyle="danger-outline")
        exit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)  # Изменено columnspan

        # Настройка строк и столбцов для адаптивности
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_registration(self):
        self.destroy()
        reg_window = RegistrationWindow(self.db_path)
        reg_window.mainloop()

    def show_login(self):
        self.destroy()
        login_window = LoginWindow(self.db_path)
        login_window.mainloop()

    def exit_program(self):
        self.destroy()

    def on_closing(self):
        if self.conn:
            self.conn.close()
            print("Соединение с БД закрыто.")
        self.destroy()

class RegistrationWindow(ttk.Window):
    def __init__(self, db_path):
        super().__init__(title="Регистрация")
        self.db_path = db_path
        center_window(self, 300, 250)
        self.resizable(False, False)

        # Лэйбл для имени пользователя
        ttk.Label(self, text="Имя пользователя:", anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Лэйбл для пароля
        ttk.Label(self, text="Пароль:", anchor="w").grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.password_entry = ttk.Entry(self, show="*")  # Маскируем пароль
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Лэйбл для подтверждения пароля
        ttk.Label(self, text="Подтвердите пароль:", anchor="w").grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.confirm_password_entry = ttk.Entry(self, show="*")  # Маскируем пароль
        self.confirm_password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Кнопка регистрации
        reg_button = ttk.Button(self, text="Зарегистрироваться", command=self.register, bootstyle="primary")
        reg_button.grid(row=3, column=0, columnspan=2, padx=10, pady=15, sticky="ew")

        # Кнопка назад
        back_button = ttk.Button(self, text="Назад", command=self.go_back, bootstyle="secondary-outline")
        back_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Настройка строк и столбцов для адаптивности
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def register(self):
      username = self.username_entry.get()
      password = self.password_entry.get()
      if not username or not password:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
        return
      conn = connect_to_database(self.db_path)
      if conn:
        user_id = register_user(conn, username, password)
        if user_id:
          messagebox.showinfo("Успех", "Регистрация прошла успешно!")
          conn.close()
          self.go_back()
        else:
          conn.close()
          messagebox.showerror("Ошибка", "Ошибка регистрации.")

    def go_back(self):
      self.destroy()
      start_window = StartWindow(self.db_path)
      start_window.mainloop()

class LoginWindow(ttk.Window):
    def __init__(self, db_path):
        super().__init__(title="Авторизация", themename="morph")
        self.db_path = db_path
        center_window(self, 300, 250)
        self.resizable(False, False)

        # Лэйбл для имени пользователя
        ttk.Label(self, text="Имя пользователя:", anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Лэйбл для пароля
        ttk.Label(self, text="Пароль:", anchor="w").grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Кнопка войти
        login_button = ttk.Button(self, text="Войти", command=self.login, bootstyle="success")
        login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=15, sticky="ew")

        # Кнопка назад
        back_button = ttk.Button(self, text="Назад", command=self.go_back, bootstyle="secondary-outline")
        back_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Настройка строк и столбцов для адаптивности
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        conn = connect_to_database(self.db_path)
        if conn:
            user_id = login_user(conn, username, password)
            if user_id:
                self.destroy()
                main_window = MainWindow(self.db_path, user_id)
                main_window.mainloop()
            else:
                conn.close()
                messagebox.showerror("Ошибка", "Неверный логин или пароль.")

    def go_back(self):
        self.destroy()
        start_window = StartWindow(self.db_path)
        start_window.mainloop()


class MainWindow(ttk.Window):
    def __init__(self, db_path, user_id):
        super().__init__(title="Главное окно", themename="morph")
        self.db_path = db_path
        self.user_id = user_id
        center_window(self, 1435, 800)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Фрейм для элементов (текста и кнопок)
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        welcome_label = ttk.Label(left_frame, text="NAVIGATOR3000", font=("Arial", 16, "bold"), anchor="center")
        welcome_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        try:
            image = Image.open("map_final.png")
            self.tk_image = ImageTk.PhotoImage(image)
            self.image_label = ttk.Label(self, image=self.tk_image)
            self.image_label.grid(row=0, column=1, padx=2, pady=16)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки изображения: {e}")

        # Фрейм для ввода данных
        frame = ttk.Frame(left_frame)
        frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        # Поля ввода и лейблы внутри frame
        ttk.Label(frame, text="Город отправления:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.from_city_entry = ttk.Entry(frame)
        self.from_city_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text="Город назначения:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.to_city_entry = ttk.Entry(frame)
        self.to_city_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text="Средняя скорость (км/ч):", anchor="w").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.speed_entry = ttk.Entry(frame)
        self.speed_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text="Расход топлива (л/100км):", anchor="w").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.fuel_consumption_entry = ttk.Entry(frame)
        self.fuel_consumption_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text="Объем бака (л):", anchor="w").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.fuel_tank_capacity_entry = ttk.Entry(frame)
        self.fuel_tank_capacity_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        frame.columnconfigure(1, weight=1)  # Растягиваем поле ввода

        # Кнопка расчета маршрута
        calc_button = ttk.Button(left_frame, text="Рассчитать маршрут", command=self.calculate_route,
                                 bootstyle="primary")
        calc_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Поле для вывода результата
        self.result_text = ttk.Text(left_frame, height=25, wrap="word", state="disabled")
        self.result_text.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        # Фрейм для кнопок "История" и "Выйти"
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        # Кнопка для выхода
        exit_button = ttk.Button(button_frame, text="Выйти", command=self.go_back, bootstyle="danger-outline")
        exit_button.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        # Кнопка истории
        history_button = ttk.Button(button_frame, text="История поездок", command=self.show_trip_history,
                                    bootstyle="info")
        history_button.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Настраиваем столбцы button_frame
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Настраиваем столбцы left_frame
        left_frame.columnconfigure(0, weight=1)

    def calculate_route(self):
        city_from = self.from_city_entry.get()
        city_to = self.to_city_entry.get()
        try:
            avg_speed = float(self.speed_entry.get())
            fuel_consumption = float(self.fuel_consumption_entry.get())
            fuel_tank_capacity = float(self.fuel_tank_capacity_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка",
                                 "Пожалуйста, введите корректные числовые значения для параметров автомобиля.")
            return

        conn = connect_to_database(self.db_path)
        try:
            if conn:
                route_data = calculate_route(conn, city_from, city_to, avg_speed, fuel_consumption, fuel_tank_capacity)
                if route_data:
                    self.display_route_data(route_data, city_from, city_to)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчета маршрута: {e}")
        finally:
            if conn:
              conn.close()



    def display_route_data(self, route_data, city_from, city_to):
        if not route_data:
            messagebox.showerror("Ошибка", "Маршрут не найден или произошла ошибка при расчёте.")
            return
        city_names, total_distance, total_time, stops_for_fuel, stops_for_sleep, infrastructure = route_data

        # Формируем текст для вывода
        output_text = f"Маршрут: {' -> '.join(city_names)}\n"
        output_text += f"Общее расстояние: {total_distance:.2f} км\n"
        output_text += f"Общее время в пути: {total_time:.2f} часов\n"

        history_text = f"{city_from} -> {city_to}\t"
        history_text += f"Расстояние: {total_distance:.2f} км\t"
        history_text += f"Общее время: {total_time:.2f} часов"

        if stops_for_fuel:
            output_text += "\nРекомендуемые остановки на заправку:\n"
            for station, address in stops_for_fuel:
                output_text += f"- {station} (км от ближайшего города: {address})\n"

        if stops_for_sleep:
            output_text += "\nРекомендуемые остановки на ночлег:\n"
            for hotel, address in stops_for_sleep:
                output_text += f"- {hotel} (км от ближайшего города: {address})\n"

        output_text += "\nОбъекты инфраструктуры на маршруте:\n"
        for obj_info in infrastructure:
            obj_type, obj_name, distance, start_end = obj_info
            output_text += f"- {obj_type}: {obj_name} (на {distance} км от начала маршрута, {start_end})\n"



        # Выводим результат в текстовое поле
        self.result_text.configure(state='normal')
        self.result_text.delete("1.0", ttk.END)
        self.result_text.insert(ttk.END, output_text)
        self.result_text.configure(state='disabled')

        # Сохраняем историю поездки
        def history_save(user, route_details):
            conn = connect_to_database(self.db_path)
            if conn:
                history_save_db(conn, user, route_details)

        history_save(self.user_id, history_text)

    # Добавить метод для перехода в окно истории
    def show_trip_history(self):
        self.destroy()
        history_window = TripHistoryWindow(self.db_path, self.user_id)
        history_window.mainloop()

    def go_back(self):
        self.destroy()
        start_window = StartWindow(self.db_path)
        start_window.mainloop()

    def exit_program(self):
        self.destroy()

class TripHistoryWindow(ttk.Window):
    def __init__(self, db_path, user_id):
        super().__init__(title="История поездок", themename="morph")
        self.db_path = db_path
        self.user_id = user_id
        center_window(self, 800, 600)
        self.resizable(False, False)

        ttk.Label(self, text="История поездок", font=("Arial", 16), anchor="center").pack(pady=10)

        # Список для отображения маршрутов
        self.history_listbox = ttk.Treeview(
            self,
            columns=("ID", "Date", "Details"),
            show="headings",
            height=20
        )
        self.history_listbox.heading("ID", text="ID маршрута")
        self.history_listbox.heading("Date", text="Дата")
        self.history_listbox.heading("Details", text="Детали маршрута")
        self.history_listbox.column("ID", width=50, anchor="center")
        self.history_listbox.column("Date", width=150, anchor="center")
        self.history_listbox.column("Details", width=600, anchor="w")
        self.history_listbox.pack(padx=10, pady=10, fill="both", expand=True)

        # Загрузка данных истории
        self.load_trip_history()

        # Кнопка возврата
        back_button = ttk.Button(self, text="Назад", command=self.go_back, bootstyle="secondary-outline")
        back_button.pack(pady=10)

    def load_trip_history(self):
        conn = connect_to_database(self.db_path)
        if not conn:
            messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных.")
            return

        try:
            cursor = conn.cursor()
            query = "SELECT TripID, RouteDate, RouteDetails FROM TripsHistory WHERE UserID = ? ORDER BY RouteDate DESC"
            cursor.execute(query, (self.user_id,))
            trips = cursor.fetchall()

            # Очистить текущие записи
            for row in self.history_listbox.get_children():
                self.history_listbox.delete(row)

            # Добавить данные в список
            for trip in trips:
                trip_id, date, details = trip
                self.history_listbox.insert("", "end", values=(trip_id, date, details))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке истории поездок: {e}")
        finally:
            conn.close()

    def go_back(self):
        self.destroy()
        main_window = MainWindow(self.db_path, self.user_id)
        main_window.mainloop()

if __name__ == "__main__":
    MDB_PATH = r"..."  # Укажите путь к вашей БД
    start_window = StartWindow(MDB_PATH)
    start_window.mainloop()