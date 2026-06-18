#!/usr/bin/env python3
"""
dish_forge.py - Генератор случайных блюд на Python (CLI + Tkinter GUI)
Поддерживает: фильтры по типу, кухне, времени, сложности, избранное.
"""
import argparse
import sys
import json
import os
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict, field

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

DATA_FILE = "dishes.json"
FAVORITES_FILE = "favorites.json"

@dataclass
class Dish:
    name: str
    type: str          # breakfast, lunch, dinner, dessert, snack, drink
    cuisine: str       # italian, japanese, russian, mexican, french, chinese, indian
    time: int          # время приготовления в минутах
    difficulty: str    # easy, medium, hard
    description: str
    ingredients: List[str]
    instructions: List[str]

class DishForge:
    def __init__(self, data_file=DATA_FILE, fav_file=FAVORITES_FILE):
        self.data_file = data_file
        self.fav_file = fav_file
        self.dishes: List[Dish] = []
        self.favorites: List[str] = []
        self.load()
        self.load_favorites()

    def load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.dishes = [Dish(**d) for d in data]
            except:
                self.dishes = self._default_dishes()
        else:
            self.dishes = self._default_dishes()
            self.save()

    def load_favorites(self):
        if os.path.exists(self.fav_file):
            try:
                with open(self.fav_file, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
            except:
                self.favorites = []
        else:
            self.favorites = []

    def save(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(d) for d in self.dishes], f, indent=2, ensure_ascii=False)

    def save_favorites(self):
        with open(self.fav_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, indent=2, ensure_ascii=False)

    def _default_dishes(self) -> List[Dish]:
        """База рецептов (сокращённая версия для примера)"""
        return [
            Dish("Овсянка с ягодами", "breakfast", "russian", 10, "easy",
                 "Полезный завтрак из овсяных хлопьев с ягодами и мёдом.",
                 ["Овсяные хлопья 100г", "Молоко 200мл", "Ягоды 50г", "Мёд 1 ст.л."],
                 ["Вскипятить молоко", "Добавить хлопья, варить 5 мин", "Добавить ягоды и мёд"]),
            Dish("Паста Карбонара", "lunch", "italian", 25, "medium",
                 "Классическая итальянская паста с беконом и пармезаном.",
                 ["Паста 200г", "Бекон 100г", "Яйца 2 шт", "Пармезан 50г", "Сливки 100мл"],
                 ["Отварить пасту", "Обжарить бекон", "Смешать яйца, сыр и сливки", "Соединить с пастой"]),
            Dish("Суши Филадельфия", "dinner", "japanese", 40, "hard",
                 "Роллы с лососем, сливочным сыром и авокадо.",
                 ["Рис для суши 200г", "Нори 4 шт", "Лосось 150г", "Сливочный сыр 100г", "Авокадо 1 шт"],
                 ["Сварить рис", "Нарезать лосось и авокадо", "Собрать роллы", "Нарезать и подавать"]),
            Dish("Борщ", "dinner", "russian", 60, "medium",
                 "Традиционный украинский суп со свеклой и капустой.",
                 ["Свекла 2 шт", "Капуста 200г", "Картофель 3 шт", "Мясо 300г", "Лук 1 шт", "Морковь 1 шт"],
                 ["Сварить бульон", "Обжарить лук и морковь", "Добавить свеклу", "Соединить с бульоном и варить"]),
            Dish("Чизкейк", "dessert", "french", 50, "medium",
                 "Нежный творожный десерт с печеньем и ягодами.",
                 ["Печенье 200г", "Масло 100г", "Творог 500г", "Сахар 150г", "Яйца 3 шт", "Сливки 200мл"],
                 ["Измельчить печенье", "Смешать с маслом", "Взбить творог с сахаром и яйцами", "Запекать 40 мин"]),
            Dish("Гуакамоле", "snack", "mexican", 15, "easy",
                 "Мексиканская закуска из авокадо с лимоном и специями.",
                 ["Авокадо 2 шт", "Лимон 1 шт", "Помидор 1 шт", "Лук 1/2 шт", "Кинза", "Соль, перец"],
                 ["Размять авокадо", "Добавить сок лимона", "Нарезать помидор и лук", "Смешать и посолить"]),
            Dish("Лимонад", "drink", "french", 10, "easy",
                 "Освежающий напиток из лимонов и мяты.",
                 ["Лимоны 3 шт", "Сахар 100г", "Вода 1л", "Мята 10г"],
                 ["Выжать сок лимонов", "Смешать с водой и сахаром", "Добавить мяту, охладить"]),
            Dish("Пицца Маргарита", "lunch", "italian", 35, "medium",
                 "Классическая пицца с томатным соусом и моцареллой.",
                 ["Тесто для пиццы 1 шт", "Томатный соус 200г", "Моцарелла 150г", "Базилик"],
                 ["Раскатать тесто", "Намазать соус", "Добавить моцареллу", "Запекать 15 мин"]),
            Dish("Салат Цезарь", "lunch", "french", 20, "easy",
                 "Популярный салат с курицей, пармезаном и сухариками.",
                 ["Куриное филе 200г", "Салат Романо 1 пучок", "Пармезан 50г", "Сухарики 50г", "Соус Цезарь"],
                 ["Обжарить курицу", "Нарезать салат", "Смешать с сухариками и сыром", "Добавить соус"]),
            Dish("Тирамису", "dessert", "italian", 30, "medium",
                 "Знаменитый итальянский десерт с маскарпоне и кофе.",
                 ["Печенье Савоярди 200г", "Кофе 200мл", "Маскарпоне 250г", "Яйца 4 шт", "Сахар 100г"],
                 ["Взбить желтки с сахаром", "Добавить маскарпоне", "Обмакнуть печенье в кофе", "Слоями собрать десерт"]),
        ]

    def generate(self, dish_type: str = None, cuisine: str = None, max_time: int = None,
                 difficulty: str = None) -> Optional[Dish]:
        filtered = self.dishes
        if dish_type:
            filtered = [d for d in filtered if d.type == dish_type]
        if cuisine:
            filtered = [d for d in filtered if d.cuisine == cuisine]
        if max_time:
            filtered = [d for d in filtered if d.time <= max_time]
        if difficulty:
            filtered = [d for d in filtered if d.difficulty == difficulty]
        if not filtered:
            return None
        return random.choice(filtered)

    def generate_menu(self, count: int = 3, **filters) -> List[Dish]:
        """Генерирует меню из нескольких блюд (без повторений)"""
        available = self.dishes
        if filters:
            if 'dish_type' in filters and filters['dish_type']:
                available = [d for d in available if d.type == filters['dish_type']]
            if 'cuisine' in filters and filters['cuisine']:
                available = [d for d in available if d.cuisine == filters['cuisine']]
            if 'max_time' in filters and filters['max_time']:
                available = [d for d in available if d.time <= filters['max_time']]
            if 'difficulty' in filters and filters['difficulty']:
                available = [d for d in available if d.difficulty == filters['difficulty']]
        if len(available) < count:
            count = len(available)
        return random.sample(available, count)

    def get_types(self) -> List[str]:
        return sorted(set(d.type for d in self.dishes))

    def get_cuisines(self) -> List[str]:
        return sorted(set(d.cuisine for d in self.dishes))

    def get_difficulties(self) -> List[str]:
        return sorted(set(d.difficulty for d in self.dishes))

    def add_favorite(self, dish_name: str) -> bool:
        if dish_name not in self.favorites:
            self.favorites.append(dish_name)
            self.save_favorites()
            return True
        return False

    def remove_favorite(self, dish_name: str) -> bool:
        if dish_name in self.favorites:
            self.favorites.remove(dish_name)
            self.save_favorites()
            return True
        return False

    def get_favorites(self) -> List[Dish]:
        return [d for d in self.dishes if d.name in self.favorites]

    def format_dish(self, dish: Dish) -> str:
        lines = []
        lines.append(f"🍽️ {dish.name}")
        lines.append(f"  Тип: {dish.type}")
        lines.append(f"  Кухня: {dish.cuisine}")
        lines.append(f"  Время: {dish.time} мин")
        lines.append(f"  Сложность: {dish.difficulty}")
        lines.append(f"  Описание: {dish.description}")
        lines.append("  Ингредиенты:")
        for ing in dish.ingredients:
            lines.append(f"    - {ing}")
        lines.append("  Приготовление:")
        for step in dish.instructions:
            lines.append(f"    {step}")
        return "\n".join(lines)

# ========== CLI ==========
def cli():
    parser = argparse.ArgumentParser(description="Генератор случайных блюд")
    subparsers = parser.add_subparsers(dest="command", help="Команды")

    # generate
    gen_parser = subparsers.add_parser("generate", help="Сгенерировать случайное блюдо")
    gen_parser.add_argument("--type", choices=['breakfast','lunch','dinner','dessert','snack','drink'], help="Тип блюда")
    gen_parser.add_argument("--cuisine", help="Кухня")
    gen_parser.add_argument("--time", type=int, help="Максимальное время приготовления (мин)")
    gen_parser.add_argument("--difficulty", choices=['easy','medium','hard'], help="Сложность")

    # random-menu
    menu_parser = subparsers.add_parser("random-menu", help="Сгенерировать меню")
    menu_parser.add_argument("--count", type=int, default=3, help="Количество блюд")
    menu_parser.add_argument("--type", choices=['breakfast','lunch','dinner','dessert','snack','drink'], help="Тип блюда")
    menu_parser.add_argument("--cuisine", help="Кухня")
    menu_parser.add_argument("--time", type=int, help="Максимальное время")
    menu_parser.add_argument("--difficulty", choices=['easy','medium','hard'], help="Сложность")

    # list
    list_parser = subparsers.add_parser("list", help="Список всех блюд")
    list_parser.add_argument("--type", help="Фильтр по типу")
    list_parser.add_argument("--cuisine", help="Фильтр по кухне")

    # favorites
    fav_parser = subparsers.add_parser("favorites", help="Управление избранным")
    fav_subparsers = fav_parser.add_subparsers(dest="fav_cmd", help="Команды избранного")
    fav_add = fav_subparsers.add_parser("add", help="Добавить в избранное")
    fav_add.add_argument("name", help="Название блюда")
    fav_remove = fav_subparsers.add_parser("remove", help="Удалить из избранного")
    fav_remove.add_argument("name", help="Название блюда")
    fav_list = fav_subparsers.add_parser("list", help="Показать избранное")

    # gui
    parser.add_argument("--gui", action="store_true", help="Запустить GUI")
    args = parser.parse_args()

    if args.gui and GUI_AVAILABLE:
        root = tk.Tk()
        app = DishForgeGUI(root)
        root.mainloop()
        return

    forge = DishForge()
    if args.command == "generate":
        dish = forge.generate(args.type, args.cuisine, args.time, args.difficulty)
        if dish:
            print(forge.format_dish(dish))
        else:
            print("❌ Блюда не найдены по заданным критериям")
    elif args.command == "random-menu":
        filters = {}
        if args.type: filters['dish_type'] = args.type
        if args.cuisine: filters['cuisine'] = args.cuisine
        if args.time: filters['max_time'] = args.time
        if args.difficulty: filters['difficulty'] = args.difficulty
        dishes = forge.generate_menu(args.count, **filters)
        if dishes:
            print(f"🍽️ Меню из {len(dishes)} блюд:")
            for i, d in enumerate(dishes, 1):
                print(f"\n{i}. {d.name}")
                print(f"   Тип: {d.type}, Кухня: {d.cuisine}, Время: {d.time} мин, Сложность: {d.difficulty}")
                print(f"   {d.description}")
        else:
            print("❌ Недостаточно блюд для меню")
    elif args.command == "list":
        dishes = forge.dishes
        if args.type:
            dishes = [d for d in dishes if d.type == args.type]
        if args.cuisine:
            dishes = [d for d in dishes if d.cuisine == args.cuisine]
        for d in dishes:
            print(f"{d.name} ({d.type}, {d.cuisine}, {d.time} мин)")
    elif args.command == "favorites":
        if args.fav_cmd == "add":
            if forge.add_favorite(args.name):
                print(f"✅ '{args.name}' добавлен в избранное")
            else:
                print(f"⚠️ '{args.name}' уже в избранном")
        elif args.fav_cmd == "remove":
            if forge.remove_favorite(args.name):
                print(f"✅ '{args.name}' удалён из избранного")
            else:
                print(f"❌ '{args.name}' не найден в избранном")
        elif args.fav_cmd == "list":
            favs = forge.get_favorites()
            if favs:
                print("⭐ Избранное:")
                for d in favs:
                    print(f"  {d.name} ({d.type}, {d.cuisine})")
            else:
                print("Избранное пусто")
    else:
        # interactive mode
        interactive_mode(forge)

def interactive_mode(forge):
    while True:
        print("\n🍳 DishForge - Генератор блюд (интерактивный)")
        print("1. Сгенерировать случайное блюдо")
        print("2. Сгенерировать меню")
        print("3. Список всех блюд")
        print("4. Избранное")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            print("Оставьте пустым для любого значения")
            t = input("Тип (breakfast/lunch/dinner/dessert/snack/drink): ").strip() or None
            c = input("Кухня (italian/japanese/russian/mexican/french/chinese/indian): ").strip() or None
            time_str = input("Макс. время (мин): ").strip()
            max_time = int(time_str) if time_str else None
            diff = input("Сложность (easy/medium/hard): ").strip() or None
            dish = forge.generate(t, c, max_time, diff)
            if dish:
                print(forge.format_dish(dish))
            else:
                print("❌ Блюда не найдены")
        elif choice == "2":
            try:
                count = int(input("Количество блюд (по умолчанию 3): ").strip() or "3")
            except:
                count = 3
            t = input("Тип (Enter пропустить): ").strip() or None
            c = input("Кухня (Enter пропустить): ").strip() or None
            time_str = input("Макс. время (мин, Enter пропустить): ").strip()
            max_time = int(time_str) if time_str else None
            diff = input("Сложность (easy/medium/hard, Enter пропустить): ").strip() or None
            filters = {}
            if t: filters['dish_type'] = t
            if c: filters['cuisine'] = c
            if max_time: filters['max_time'] = max_time
            if diff: filters['difficulty'] = diff
            dishes = forge.generate_menu(count, **filters)
            if dishes:
                print(f"🍽️ Меню из {len(dishes)} блюд:")
                for i, d in enumerate(dishes, 1):
                    print(f"\n{i}. {d.name} ({d.type}, {d.cuisine}, {d.time} мин, {d.difficulty})")
                    print(f"   {d.description}")
            else:
                print("❌ Недостаточно блюд")
        elif choice == "3":
            t = input("Тип (Enter пропустить): ").strip() or None
            c = input("Кухня (Enter пропустить): ").strip() or None
            dishes = forge.dishes
            if t: dishes = [d for d in dishes if d.type == t]
            if c: dishes = [d for d in dishes if d.cuisine == c]
            for d in dishes:
                print(f"  {d.name} ({d.type}, {d.cuisine}, {d.time} мин)")
        elif choice == "4":
            print("⭐ Избранное:")
            favs = forge.get_favorites()
            if favs:
                for d in favs:
                    print(f"  {d.name} ({d.type}, {d.cuisine})")
            else:
                print("  Пусто")
            print("\n1. Добавить в избранное")
            print("2. Удалить из избранного")
            print("3. Назад")
            sub = input("Выберите: ").strip()
            if sub == "1":
                name = input("Название блюда: ").strip()
                if forge.add_favorite(name):
                    print(f"✅ '{name}' добавлен")
                else:
                    print(f"⚠️ '{name}' уже в избранном или не существует")
            elif sub == "2":
                name = input("Название блюда: ").strip()
                if forge.remove_favorite(name):
                    print(f"✅ '{name}' удалён")
                else:
                    print(f"❌ '{name}' не найден")
        else:
            print("Неверный выбор")

# ========== GUI ==========
if GUI_AVAILABLE:
    class DishForgeGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("🍳 DishForge - Генератор блюд")
            self.root.geometry("700x600")
            self.root.resizable(True, True)
            self.forge = DishForge()
            self.create_widgets()

        def create_widgets(self):
            main = ttk.Frame(self.root, padding="10")
            main.pack(fill=tk.BOTH, expand=True)

            # Фильтры
            filter_frame = ttk.LabelFrame(main, text="Фильтры")
            filter_frame.pack(fill=tk.X, pady=5)
            fgrid = ttk.Frame(filter_frame)
            fgrid.pack(pady=5, padx=5)
            ttk.Label(fgrid, text="Тип:").grid(row=0, column=0, sticky="w")
            self.type_var = tk.StringVar()
            ttk.Combobox(fgrid, textvariable=self.type_var, values=[''] + self.forge.get_types(), state="readonly", width=12).grid(row=0, column=1, padx=5)
            ttk.Label(fgrid, text="Кухня:").grid(row=0, column=2, sticky="w")
            self.cuisine_var = tk.StringVar()
            ttk.Combobox(fgrid, textvariable=self.cuisine_var, values=[''] + self.forge.get_cuisines(), state="readonly", width=12).grid(row=0, column=3, padx=5)
            ttk.Label(fgrid, text="Макс. время (мин):").grid(row=0, column=4, sticky="w")
            self.time_var = tk.StringVar()
            ttk.Entry(fgrid, textvariable=self.time_var, width=8).grid(row=0, column=5, padx=5)
            ttk.Label(fgrid, text="Сложность:").grid(row=0, column=6, sticky="w")
            self.diff_var = tk.StringVar()
            ttk.Combobox(fgrid, textvariable=self.diff_var, values=[''] + self.forge.get_difficulties(), state="readonly", width=10).grid(row=0, column=7, padx=5)
            ttk.Button(fgrid, text="🎲 Сгенерировать", command=self.generate).grid(row=0, column=8, padx=5)
            ttk.Button(fgrid, text="🍽️ Меню (3)", command=lambda: self.generate_menu(3)).grid(row=0, column=9, padx=5)

            # Результат
            self.result_text = scrolledtext.ScrolledText(main, wrap=tk.WORD, height=15)
            self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

            # Кнопки
            bottom = ttk.Frame(main)
            bottom.pack(fill=tk.X, pady=5)
            ttk.Button(bottom, text="⭐ Добавить в избранное", command=self.add_favorite).pack(side=tk.LEFT, padx=5)
            ttk.Button(bottom, text="📋 Избранное", command=self.show_favorites).pack(side=tk.LEFT, padx=5)
            ttk.Button(bottom, text="📤 Экспорт HTML", command=self.export_html).pack(side=tk.LEFT, padx=5)

            # Текущее отображаемое блюдо
            self.current_dish = None

        def generate(self):
            t = self.type_var.get() or None
            c = self.cuisine_var.get() or None
            time_str = self.time_var.get().strip()
            max_time = int(time_str) if time_str else None
            diff = self.diff_var.get() or None
            dish = self.forge.generate(t, c, max_time, diff)
            if dish:
                self.current_dish = dish
                self.display_dish(dish)
            else:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "❌ Блюда не найдены по заданным критериям")

        def generate_menu(self, count):
            t = self.type_var.get() or None
            c = self.cuisine_var.get() or None
            time_str = self.time_var.get().strip()
            max_time = int(time_str) if time_str else None
            diff = self.diff_var.get() or None
            filters = {}
            if t: filters['dish_type'] = t
            if c: filters['cuisine'] = c
            if max_time: filters['max_time'] = max_time
            if diff: filters['difficulty'] = diff
            dishes = self.forge.generate_menu(count, **filters)
            self.result_text.delete(1.0, tk.END)
            if dishes:
                self.result_text.insert(tk.END, f"🍽️ Меню из {len(dishes)} блюд:\n\n")
                for i, d in enumerate(dishes, 1):
                    self.result_text.insert(tk.END, f"{i}. {d.name} ({d.type}, {d.cuisine}, {d.time} мин, {d.difficulty})\n")
                    self.result_text.insert(tk.END, f"   {d.description}\n\n")
            else:
                self.result_text.insert(tk.END, "❌ Недостаточно блюд")

        def display_dish(self, dish):
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, self.forge.format_dish(dish))

        def add_favorite(self):
            if self.current_dish:
                if self.forge.add_favorite(self.current_dish.name):
                    messagebox.showinfo("Избранное", f"'{self.current_dish.name}' добавлен в избранное")
                else:
                    messagebox.showinfo("Избранное", f"'{self.current_dish.name}' уже в избранном")
            else:
                messagebox.showwarning("Нет блюда", "Сначала сгенерируйте блюдо")

        def show_favorites(self):
            favs = self.forge.get_favorites()
            if not favs:
                messagebox.showinfo("Избранное", "Избранное пусто")
                return
            win = tk.Toplevel(self.root)
            win.title("⭐ Избранное")
            win.geometry("500x400")
            text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            for d in favs:
                text.insert(tk.END, f"🍽️ {d.name}\n")
                text.insert(tk.END, f"  Тип: {d.type}, Кухня: {d.cuisine}, Время: {d.time} мин, Сложность: {d.difficulty}\n\n")
            text.config(state='disabled')

        def export_html(self):
            if not self.current_dish:
                messagebox.showwarning("Нет блюда", "Сначала сгенерируйте блюдо")
                return
            filepath = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
            if filepath:
                dish = self.current_dish
                html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{dish.name}</title>
<style>body{{font-family:system-ui;max-width:800px;margin:40px auto;padding:20px;background:#f8f9fa;}}
h1{{color:#2c3e50;}} .meta{{color:#7f8c8d;}} .section{{margin:20px 0;padding:15px;background:white;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);}}
ul{{list-style-type:disc;padding-left:20px;}}</style>
</head>
<body>
<h1>🍽️ {dish.name}</h1>
<div class="meta"><strong>Тип:</strong> {dish.type} | <strong>Кухня:</strong> {dish.cuisine} | <strong>Время:</strong> {dish.time} мин | <strong>Сложность:</strong> {dish.difficulty}</div>
<div class="section"><p>{dish.description}</p></div>
<div class="section"><h3>Ингредиенты</h3><ul>{"".join(f"<li>{ing}</li>" for ing in dish.ingredients)}</ul></div>
<div class="section"><h3>Приготовление</h3><ol>{"".join(f"<li>{step}</li>" for step in dish.instructions)}</ol></div>
</body></html>"""
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)
                messagebox.showinfo("Экспорт", f"Рецепт сохранён в {filepath}")

if __name__ == "__main__":
    cli()
