import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# --- Подключение к базе данных ---
conn = sqlite3.connect('altunin')
cursor = conn.cursor()

# --- Создание таблиц ---

# Таблица материалов с расширенными полями
cursor.execute('''
CREATE TABLE IF NOT EXISTS Materials (
    MaterialID INTEGER PRIMARY KEY AUTOINCREMENT,
    Type TEXT NOT NULL,
    Name TEXT NOT NULL UNIQUE,
    Description TEXT,
    UnitPrice REAL NOT NULL CHECK(UnitPrice >= 0),
    Unit TEXT NOT NULL,
    PackageQuantity INTEGER NOT NULL CHECK(PackageQuantity > 0),
    Quantity INTEGER NOT NULL CHECK(Quantity >= 0),
    MinQuantity INTEGER NOT NULL CHECK(MinQuantity >= 0)
);
''')

# Таблица продукции (офисная мебель)
cursor.execute('''
CREATE TABLE IF NOT EXISTS Products (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL UNIQUE,
    Description TEXT
);
''')

# Таблица связей материалов и продукции (какие материалы используются в каком продукте)
cursor.execute('''
CREATE TABLE IF NOT EXISTS ProductMaterials (
    ProductID INTEGER,
    MaterialID INTEGER,
    QuantityRequired INTEGER NOT NULL CHECK(QuantityRequired > 0),
    PRIMARY KEY (ProductID, MaterialID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE,
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID) ON DELETE CASCADE
);
''')

conn.commit()

# --- Функции для работы с базой данных ---

def get_all_materials():
    cursor.execute('SELECT MaterialID, Type, Name, Description, UnitPrice, Unit, PackageQuantity, Quantity, MinQuantity FROM Materials')
    return cursor.fetchall()

def add_material_db(material):
    try:
        cursor.execute('''
            INSERT INTO Materials (Type, Name, Description, UnitPrice, Unit, PackageQuantity, Quantity, MinQuantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', material)
        conn.commit()
        return True, f"Материал '{material[1]}' успешно добавлен."
    except sqlite3.IntegrityError:
        return False, f"Ошибка: материал с именем '{material[1]}' уже существует."

def update_material_db(material_id, material):
    try:
        cursor.execute('''
            UPDATE Materials SET Type=?, Name=?, Description=?, UnitPrice=?, Unit=?, PackageQuantity=?, Quantity=?, MinQuantity=?
            WHERE MaterialID=?
        ''', (*material, material_id))
        conn.commit()
        return True, f"Материал ID {material_id} успешно обновлен."
    except sqlite3.IntegrityError:
        return False, f"Ошибка: материал с именем '{material[1]}' уже существует."

def get_material_by_id(material_id):
    cursor.execute('''
        SELECT MaterialID, Type, Name, Description, UnitPrice, Unit, PackageQuantity, Quantity, MinQuantity
        FROM Materials WHERE MaterialID=?
    ''', (material_id,))
    return cursor.fetchone()

def add_product(name, description):
    try:
        cursor.execute('INSERT INTO Products (Name, Description) VALUES (?, ?)', (name, description))
        conn.commit()
        print(f"Продукция '{name}' добавлена.")
    except sqlite3.IntegrityError:
        print(f"Ошибка: продукция с именем '{name}' уже существует.")

def add_product_material(product_id, material_id, quantity_required):
    try:
        cursor.execute('''
            INSERT INTO ProductMaterials (ProductID, MaterialID, QuantityRequired) VALUES (?, ?, ?)
        ''', (product_id, material_id, quantity_required))
        conn.commit()
        print(f"Связь продукта ID {product_id} и материала ID {material_id} добавлена.")
    except sqlite3.IntegrityError:
        print("Ошибка: такая связь уже существует или неверные ID.")

def list_products_using_material(material_id):
    cursor.execute('''
        SELECT p.ProductID, p.Name, p.Description, pm.QuantityRequired
        FROM Products p
        JOIN ProductMaterials pm ON p.ProductID = pm.ProductID
        WHERE pm.MaterialID = ?
    ''', (material_id,))
    products = cursor.fetchall()
    if not products:
        print("Продукция с использованием данного материала не найдена.")
    else:
        print(f"Продукция, использующая материал ID {material_id}:")
        for p in products:
            print(f"ID: {p[0]}, Название: {p[1]}, Описание: {p[2]}, Кол-во материала: {p[3]}")

# --- GUI ---

class WarehouseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Склад материалов")
        self.geometry("900x450")
        self.resizable(False, False)
        self.frames = {}

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        for F in (MaterialsListPage, MaterialFormPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MaterialsListPage")

    def show_frame(self, page_name, **kwargs):
        frame = self.frames[page_name]
        if hasattr(frame, 'refresh'):
            frame.refresh(**kwargs)
        frame.tkraise()

class MaterialsListPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Список материалов на складе", font=("Arial", 16))
        label.pack(pady=10)

        columns = ("ID", "Тип", "Название", "Описание", "Цена за ед.", "Ед. изм.", "Кол-во в уп.", "На складе", "Мин. кол-во")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Описание":
                self.tree.column(col, width=250)
            else:
                self.tree.column(col, width=90, anchor='center')
        self.tree.pack(fill="both", expand=True, padx=10)

        self.tree.bind("<Double-1>", self.on_item_double_click)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        add_btn = ttk.Button(btn_frame, text="Добавить материал", command=self.on_add_material)
        add_btn.pack(side="left", padx=5)

        refresh_btn = ttk.Button(btn_frame, text="Обновить список", command=self.refresh)
        refresh_btn.pack(side="left", padx=5)

        self.refresh()

    def refresh(self, **kwargs):
        for item in self.tree.get_children():
            self.tree.delete(item)

        materials = get_all_materials()
        for m in materials:
            price_str = f"{m[4]:.2f}"
            self.tree.insert("", "end", values=(m[0], m[1], m[2], m[3], price_str, m[5], m[6], m[7], m[8]))

    def on_add_material(self):
        self.controller.show_frame("MaterialFormPage", material_id=None)

    def on_item_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected)
        material_id = item['values'][0]
        self.controller.show_frame("MaterialFormPage", material_id=material_id)

class MaterialFormPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.material_id = None

        self.title_label = ttk.Label(self, text="", font=("Arial", 16))
        self.title_label.pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill="x")

        # Поля формы
        self.fields = {}

        # Тип материала
        ttk.Label(form_frame, text="Тип материала:").grid(row=0, column=0, sticky="e", pady=5)
        self.type_var = tk.StringVar()
        self.type_cb = ttk.Combobox(form_frame, textvariable=self.type_var, state="readonly")
        self.type_cb['values'] = ("Древесина", "Металл", "Пластик", "Ткань", "Стекло", "Другой")
        self.type_cb.grid(row=0, column=1, sticky="w", pady=5)
        self.fields['type'] = self.type_var

        # Наименование
        ttk.Label(form_frame, text="Наименование:").grid(row=1, column=0, sticky="e", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var).grid(row=1, column=1, sticky="w", pady=5)
        self.fields['name'] = self.name_var

        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=2, column=0, sticky="e", pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.desc_var).grid(row=2, column=1, sticky="w", pady=5)
        self.fields['description'] = self.desc_var

        # Цена единицы
        ttk.Label(form_frame, text="Цена за единицу:").grid(row=3, column=0, sticky="e", pady=5)
        self.price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.price_var).grid(row=3, column=1, sticky="w", pady=5)
        self.fields['unit_price'] = self.price_var

        # Единица измерения
        ttk.Label(form_frame, text="Единица измерения:").grid(row=4, column=0, sticky="e", pady=5)
        self.unit_var = tk.StringVar()
        self.unit_cb = ttk.Combobox(form_frame, textvariable=self.unit_var, state="readonly")
        self.unit_cb['values'] = ("шт", "м", "кг", "л", "упак", "другое")
        self.unit_cb.grid(row=4, column=1, sticky="w", pady=5)
        self.fields['unit'] = self.unit_var

        # Количество в упаковке
        ttk.Label(form_frame, text="Количество в упаковке:").grid(row=5, column=0, sticky="e", pady=5)
        self.pack_qty_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.pack_qty_var).grid(row=5, column=1, sticky="w", pady=5)
        self.fields['package_quantity'] = self.pack_qty_var

        # Количество на складе
        ttk.Label(form_frame, text="Количество на складе:").grid(row=6, column=0, sticky="e", pady=5)
        self.qty_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.qty_var).grid(row=6, column=1, sticky="w", pady=5)
        self.fields['quantity'] = self.qty_var

        # Минимальное количество
        ttk.Label(form_frame, text="Минимальное количество:").grid(row=7, column=0, sticky="e", pady=5)
        self.min_qty_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.min_qty_var).grid(row=7, column=1, sticky="w", pady=5)
        self.fields['min_quantity'] = self.min_qty_var

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)

        self.save_btn = ttk.Button(btn_frame, text="Сохранить", command=self.on_save)
        self.save_btn.pack(side="left", padx=10)

        self.back_btn = ttk.Button(btn_frame, text="Назад", command=self.on_back)
        self.back_btn.pack(side="left", padx=10)

    def refresh(self, material_id=None):
        self.material_id = material_id
        if material_id is None:
            self.title_label.config(text="Добавить новый материал")
            self.type_var.set("")
            self.name_var.set("")
            self.desc_var.set("")
            self.price_var.set("")
            self.unit_var.set("")
            self.pack_qty_var.set("")
            self.qty_var.set("")
            self.min_qty_var.set("")
        else:
            self.title_label.config(text="Редактировать материал")
            material = get_material_by_id(material_id)
            if material:
                self.type_var.set(material[1])
                self.name_var.set(material[2])
                self.desc_var.set(material[3] if material[3] else "")
                self.price_var.set(f"{material[4]:.2f}")
                self.unit_var.set(material[5])
                self.pack_qty_var.set(str(material[6]))
                self.qty_var.set(str(material[7]))
                self.min_qty_var.set(str(material[8]))
            else:
                messagebox.showerror("Ошибка", "Материал не найден в базе данных.")
                self.controller.show_frame("MaterialsListPage")

    def on_save(self):
        try:
            if not self.type_var.get():
                raise ValueError("Тип материала обязателен для заполнения.")
            if not self.name_var.get():
                raise ValueError("Наименование обязательно для заполнения.")
            if not self.unit_var.get():
                raise ValueError("Единица измерения обязательна для заполнения.")

            price = float(self.price_var.get())
            if price < 0:
                raise ValueError("Цена материала не может быть отрицательной.")

            package_qty = int(self.pack_qty_var.get())
            if package_qty <= 0:
                raise ValueError("Количество в упаковке должно быть положительным целым числом.")

            quantity = int(self.qty_var.get())
            if quantity < 0:
                raise ValueError("Количество на складе не может быть отрицательным.")

            min_quantity = int(self.min_qty_var.get())
            if min_quantity < 0:
                raise ValueError("Минимальное количество не может быть отрицательным.")

            material_data = (
                self.type_var.get(),
                self.name_var.get(),
                self.desc_var.get(),
                price,
                self.unit_var.get(),
                package_qty,
                quantity,
                min_quantity
            )

            if self.material_id is None:
                success, msg = add_material_db(material_data)
            else:
                success, msg = update_material_db(self.material_id, material_data)

            if success:
                messagebox.showinfo("Успех", msg)
                self.controller.show_frame("MaterialsListPage")
            else:
                messagebox.showerror("Ошибка", msg)

        except ValueError as ve:
            messagebox.showerror("Ошибка ввода", str(ve))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def on_back(self):
        if messagebox.askyesno("Подтверждение", "Вернуться без сохранения изменений?"):
            self.controller.show_frame("MaterialsListPage")

# --- Пример добавления продукции и связей (один раз при запуске) ---

def initialize_example_data():
    # Добавление продукцию, если еще нет
    cursor.execute('SELECT COUNT(*) FROM Products')
    if cursor.fetchone()[0] == 0:
        add_product("Офисный стол", "Стол для офиса")
        add_product("Офисный стул", "Стул для офиса")

    # Добавление материалов, если еще нет (с минимальными полями для примера)
    cursor.execute('SELECT COUNT(*) FROM Materials')
    if cursor.fetchone()[0] == 0:
        # Пример с заполнением всех полей
        materials_to_add = [
            ("Древесина", "ДСП", "Древесно-стружечная плита", 150.00, "м2", 10, 100, 5),
            ("Металл", "Металл", "Стальной профиль", 300.00, "кг", 5, 50, 10)
        ]
        for mat in materials_to_add:
            add_material_db(mat)

    # Связь материалы с продукцией
    cursor.execute('SELECT ProductID FROM Products WHERE Name = ?', ("Офисный стол",))
    product_id = cursor.fetchone()[0]
    cursor.execute('SELECT MaterialID FROM Materials WHERE Name = ?', ("ДСП",))
    material_id_dsp = cursor.fetchone()[0]
    cursor.execute('SELECT MaterialID FROM Materials WHERE Name = ?', ("Металл",))
    material_id_metal = cursor.fetchone()[0]

    # Добавляются связи, если их нет
    cursor.execute('SELECT COUNT(*) FROM ProductMaterials')
    if cursor.fetchone()[0] == 0:
        add_product_material(product_id, material_id_dsp, 5)
        add_product_material(product_id, material_id_metal, 2)

# --- Запуск приложения ---

if __name__ == '__main__':
    initialize_example_data()
    app = WarehouseApp()
    app.mainloop()

    # Закрытие соединения с БД при выходе
    conn.close()
