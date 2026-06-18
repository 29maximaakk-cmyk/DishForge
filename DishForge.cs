// DishForge.cs - Генератор случайных блюд на C# (CLI + WinForms)
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Windows.Forms;

namespace DishForge
{
    public class Dish
    {
        public string Name { get; set; }
        public string Type { get; set; }
        public string Cuisine { get; set; }
        public int Time { get; set; }
        public string Difficulty { get; set; }
        public string Description { get; set; }
        public List<string> Ingredients { get; set; }
        public List<string> Instructions { get; set; }
    }

    public class Forge
    {
        public List<Dish> Dishes { get; set; } = new List<Dish>();
        public List<string> Favorites { get; set; } = new List<string>();
        private const string DataFile = "dishes.json";
        private const string FavFile = "favorites.json";

        public void Load()
        {
            if (File.Exists(DataFile))
            {
                try
                {
                    string json = File.ReadAllText(DataFile);
                    var dishes = JsonSerializer.Deserialize<List<Dish>>(json);
                    if (dishes != null) Dishes = dishes;
                }
                catch { }
            }
            if (!Dishes.Any()) { Dishes = DefaultDishes(); Save(); }
            if (File.Exists(FavFile))
            {
                try
                {
                    string json = File.ReadAllText(FavFile);
                    var favs = JsonSerializer.Deserialize<List<string>>(json);
                    if (favs != null) Favorites = favs;
                }
                catch { }
            }
        }

        public void Save()
        {
            File.WriteAllText(DataFile, JsonSerializer.Serialize(Dishes, new JsonSerializerOptions { WriteIndented = true }));
            File.WriteAllText(FavFile, JsonSerializer.Serialize(Favorites, new JsonSerializerOptions { WriteIndented = true }));
        }

        private List<Dish> DefaultDishes()
        {
            return new List<Dish>
            {
                new Dish { Name = "Овсянка с ягодами", Type = "breakfast", Cuisine = "russian", Time = 10, Difficulty = "easy",
                    Description = "Полезный завтрак из овсяных хлопьев с ягодами и мёдом.",
                    Ingredients = new List<string>{"Овсяные хлопья 100г", "Молоко 200мл", "Ягоды 50г", "Мёд 1 ст.л."},
                    Instructions = new List<string>{"Вскипятить молоко", "Добавить хлопья, варить 5 мин", "Добавить ягоды и мёд"} },
                new Dish { Name = "Паста Карбонара", Type = "lunch", Cuisine = "italian", Time = 25, Difficulty = "medium",
                    Description = "Классическая итальянская паста с беконом и пармезаном.",
                    Ingredients = new List<string>{"Паста 200г", "Бекон 100г", "Яйца 2 шт", "Пармезан 50г", "Сливки 100мл"},
                    Instructions = new List<string>{"Отварить пасту", "Обжарить бекон", "Смешать яйца, сыр и сливки", "Соединить с пастой"} }
            };
        }

        public Dish Generate(string type, string cuisine, int? maxTime, string difficulty)
        {
            var filtered = Dishes.AsEnumerable();
            if (!string.IsNullOrEmpty(type)) filtered = filtered.Where(d => d.Type == type);
            if (!string.IsNullOrEmpty(cuisine)) filtered = filtered.Where(d => d.Cuisine == cuisine);
            if (maxTime.HasValue) filtered = filtered.Where(d => d.Time <= maxTime.Value);
            if (!string.IsNullOrEmpty(difficulty)) filtered = filtered.Where(d => d.Difficulty == difficulty);
            var list = filtered.ToList();
            if (!list.Any()) return null;
            return list[new Random().Next(list.Count)];
        }

        public List<Dish> GenerateMenu(int count, string type, string cuisine, int? maxTime, string difficulty)
        {
            var available = Dishes.AsEnumerable();
            if (!string.IsNullOrEmpty(type)) available = available.Where(d => d.Type == type);
            if (!string.IsNullOrEmpty(cuisine)) available = available.Where(d => d.Cuisine == cuisine);
            if (maxTime.HasValue) available = available.Where(d => d.Time <= maxTime.Value);
            if (!string.IsNullOrEmpty(difficulty)) available = available.Where(d => d.Difficulty == difficulty);
            var list = available.ToList();
            if (list.Count < count) count = list.Count;
            var rnd = new Random();
            return list.OrderBy(x => rnd.Next()).Take(count).ToList();
        }

        public bool AddFavorite(string name)
        {
            if (Favorites.Contains(name)) return false;
            Favorites.Add(name);
            Save();
            return true;
        }

        public bool RemoveFavorite(string name)
        {
            if (Favorites.Remove(name)) { Save(); return true; }
            return false;
        }

        public List<Dish> GetFavorites()
        {
            return Dishes.Where(d => Favorites.Contains(d.Name)).ToList();
        }

        public string FormatDish(Dish d)
        {
            var lines = new List<string>();
            lines.Add($"🍽️ {d.Name}");
            lines.Add($"  Тип: {d.Type}");
            lines.Add($"  Кухня: {d.Cuisine}");
            lines.Add($"  Время: {d.Time} мин");
            lines.Add($"  Сложность: {d.Difficulty}");
            lines.Add($"  Описание: {d.Description}");
            lines.Add("  Ингредиенты:");
            d.Ingredients.ForEach(ing => lines.Add($"    - {ing}"));
            lines.Add("  Приготовление:");
            for (int i = 0; i < d.Instructions.Count; i++) lines.Add($"    {i+1}. {d.Instructions[i]}");
            return string.Join("\n", lines);
        }
    }

    class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            if (args.Length > 0 && args[0] == "--gui")
            {
                Application.EnableVisualStyles();
                Application.Run(new DishForgeGUI());
                return;
            }
            var forge = new Forge();
            forge.Load();
            if (args.Length == 0) { InteractiveMode(forge); return; }
            try
            {
                string cmd = args[0];
                switch (cmd)
                {
                    case "generate":
                        string type = null, cuisine = null, difficulty = null;
                        int? maxTime = null;
                        for (int i = 1; i < args.Length; i++)
                        {
                            if (args[i] == "--type") type = args[++i];
                            else if (args[i] == "--cuisine") cuisine = args[++i];
                            else if (args[i] == "--time") maxTime = int.Parse(args[++i]);
                            else if (args[i] == "--difficulty") difficulty = args[++i];
                        }
                        var dish = forge.Generate(type, cuisine, maxTime, difficulty);
                        if (dish != null) Console.WriteLine(forge.FormatDish(dish));
                        else Console.WriteLine("❌ Блюда не найдены");
                        break;
                    case "menu":
                        int count = 3; type = null; cuisine = null; difficulty = null; maxTime = null;
                        for (int i = 1; i < args.Length; i++)
                        {
                            if (args[i] == "--count") count = int.Parse(args[++i]);
                            else if (args[i] == "--type") type = args[++i];
                            else if (args[i] == "--cuisine") cuisine = args[++i];
                            else if (args[i] == "--time") maxTime = int.Parse(args[++i]);
                            else if (args[i] == "--difficulty") difficulty = args[++i];
                        }
                        var menu = forge.GenerateMenu(count, type, cuisine, maxTime, difficulty);
                        if (menu.Any())
                        {
                            Console.WriteLine($"🍽️ Меню из {menu.Count} блюд:");
                            for (int i = 0; i < menu.Count; i++)
                            {
                                var d = menu[i];
                                Console.WriteLine($"\n{i+1}. {d.Name} ({d.Type}, {d.Cuisine}, {d.Time} мин, {d.Difficulty})");
                                Console.WriteLine($"   {d.Description}");
                            }
                        }
                        else Console.WriteLine("❌ Недостаточно блюд");
                        break;
                    case "list":
                        type = null; cuisine = null;
                        for (int i = 1; i < args.Length; i++)
                        {
                            if (args[i] == "--type") type = args[++i];
                            else if (args[i] == "--cuisine") cuisine = args[++i];
                        }
                        var dishes = forge.Dishes;
                        if (!string.IsNullOrEmpty(type)) dishes = dishes.Where(d => d.Type == type).ToList();
                        if (!string.IsNullOrEmpty(cuisine)) dishes = dishes.Where(d => d.Cuisine == cuisine).ToList();
                        dishes.ForEach(d => Console.WriteLine($"{d.Name} ({d.Type}, {d.Cuisine}, {d.Time} мин)"));
                        break;
                    case "favorites":
                        if (args.Length > 2 && args[2] == "add" && args.Length > 3)
                        {
                            string name = args[3];
                            if (forge.AddFavorite(name)) Console.WriteLine($"✅ '{name}' добавлен в избранное");
                            else Console.WriteLine($"⚠️ '{name}' уже в избранном или не существует");
                        }
                        else if (args.Length > 2 && args[2] == "remove" && args.Length > 3)
                        {
                            string name = args[3];
                            if (forge.RemoveFavorite(name)) Console.WriteLine($"✅ '{name}' удалён из избранного");
                            else Console.WriteLine($"❌ '{name}' не найден в избранном");
                        }
                        else
                        {
                            var favs = forge.GetFavorites();
                            if (favs.Any())
                            {
                                Console.WriteLine("⭐ Избранное:");
                                favs.ForEach(d => Console.WriteLine($"  {d.Name} ({d.Type}, {d.Cuisine})"));
                            }
                            else Console.WriteLine("Избранное пусто");
                        }
                        break;
                    default: InteractiveMode(forge); break;
                }
            }
            catch (Exception e) { Console.WriteLine($"Ошибка: {e.Message}"); }
        }

        static void InteractiveMode(Forge forge)
        {
            while (true)
            {
                Console.WriteLine("\n🍳 DishForge - Генератор блюд (интерактивный)");
                Console.WriteLine("1. Сгенерировать случайное блюдо");
                Console.WriteLine("2. Сгенерировать меню");
                Console.WriteLine("3. Список всех блюд");
                Console.WriteLine("4. Избранное");
                Console.WriteLine("0. Выход");
                Console.Write("Выберите действие: ");
                string choice = Console.ReadLine();
                switch (choice)
                {
                    case "0": return;
                    case "1":
                        Console.Write("Тип (Enter пропустить): ");
                        string t = Console.ReadLine(); if (string.IsNullOrEmpty(t)) t = null;
                        Console.Write("Кухня (Enter пропустить): ");
                        string c = Console.ReadLine(); if (string.IsNullOrEmpty(c)) c = null;
                        Console.Write("Макс. время (мин, Enter пропустить): ");
                        string timeStr = Console.ReadLine();
                        int? mt = string.IsNullOrEmpty(timeStr) ? (int?)null : int.Parse(timeStr);
                        Console.Write("Сложность (easy/medium/hard, Enter пропустить): ");
                        string diff = Console.ReadLine(); if (string.IsNullOrEmpty(diff)) diff = null;
                        var dish = forge.Generate(t, c, mt, diff);
                        if (dish != null) Console.WriteLine(forge.FormatDish(dish));
                        else Console.WriteLine("❌ Блюда не найдены");
                        break;
                    case "2":
                        Console.Write("Количество блюд (по умолчанию 3): ");
                        string cntStr = Console.ReadLine();
                        int count = string.IsNullOrEmpty(cntStr) ? 3 : int.Parse(cntStr);
                        Console.Write("Тип (Enter пропустить): ");
                        string type = Console.ReadLine(); if (string.IsNullOrEmpty(type)) type = null;
                        Console.Write("Кухня (Enter пропустить): ");
                        string cuisine = Console.ReadLine(); if (string.IsNullOrEmpty(cuisine)) cuisine = null;
                        Console.Write("Макс. время (мин, Enter пропустить): ");
                        string timeStr2 = Console.ReadLine();
                        int? maxTime = string.IsNullOrEmpty(timeStr2) ? (int?)null : int.Parse(timeStr2);
                        Console.Write("Сложность (Enter пропустить): ");
                        string difficulty = Console.ReadLine(); if (string.IsNullOrEmpty(difficulty)) difficulty = null;
                        var menu = forge.GenerateMenu(count, type, cuisine, maxTime, difficulty);
                        if (menu.Any())
                        {
                            Console.WriteLine($"🍽️ Меню из {menu.Count} блюд:");
                            for (int i = 0; i < menu.Count; i++)
                            {
                                var d = menu[i];
                                Console.WriteLine($"\n{i+1}. {d.Name} ({d.Type}, {d.Cuisine}, {d.Time} мин, {d.Difficulty})");
                                Console.WriteLine($"   {d.Description}");
                            }
                        }
                        else Console.WriteLine("❌ Недостаточно блюд");
                        break;
                    case "3":
                        Console.Write("Тип (Enter пропустить): ");
                        string filterType = Console.ReadLine();
                        Console.Write("Кухня (Enter пропустить): ");
                        string filterCuisine = Console.ReadLine();
                        var dishes = forge.Dishes;
                        if (!string.IsNullOrEmpty(filterType)) dishes = dishes.Where(d => d.Type == filterType).ToList();
                        if (!string.IsNullOrEmpty(filterCuisine)) dishes = dishes.Where(d => d.Cuisine == filterCuisine).ToList();
                        dishes.ForEach(d => Console.WriteLine($"  {d.Name} ({d.Type}, {d.Cuisine}, {d.Time} мин)"));
                        break;
                    case "4":
                        var favs = forge.GetFavorites();
                        Console.WriteLine("⭐ Избранное:");
                        if (favs.Any()) favs.ForEach(d => Console.WriteLine($"  {d.Name} ({d.Type}, {d.Cuisine})"));
                        else Console.WriteLine("  Пусто");
                        Console.WriteLine("\n1. Добавить в избранное");
                        Console.WriteLine("2. Удалить из избранного");
                        Console.WriteLine("3. Назад");
                        Console.Write("Выберите: ");
                        string sub = Console.ReadLine();
                        if (sub == "1")
                        {
                            Console.Write("Название блюда: ");
                            string name = Console.ReadLine();
                            if (forge.AddFavorite(name)) Console.WriteLine($"✅ '{name}' добавлен");
                            else Console.WriteLine($"⚠️ '{name}' уже в избранном или не существует");
                        }
                        else if (sub == "2")
                        {
                            Console.Write("Название блюда: ");
                            string name = Console.ReadLine();
                            if (forge.RemoveFavorite(name)) Console.WriteLine($"✅ '{name}' удалён");
                            else Console.WriteLine($"❌ '{name}' не найден");
                        }
                        break;
                    default: Console.WriteLine("Неверный выбор");
                }
            }
        }
    }

    // ========== GUI ==========
    public class DishForgeGUI : Form
    {
        private Forge forge = new Forge();
        private ComboBox typeBox, cuisineBox, diffBox;
        private TextBox timeBox;
        private TextBox resultBox;
        private Dish currentDish;

        public DishForgeGUI()
        {
            forge.Load();
            Text = "🍳 DishForge - Генератор блюд";
            Size = new System.Drawing.Size(700, 550);
            StartPosition = FormStartPosition.CenterScreen;

            var top = new FlowLayoutPanel { Dock = DockStyle.Top, Padding = new Padding(5) };
            top.Controls.Add(new Label { Text = "Тип:", AutoSize = true });
            typeBox = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList, Items = { "", "breakfast", "lunch", "dinner", "dessert", "snack", "drink" }, Width = 100 };
            top.Controls.Add(typeBox);
            top.Controls.Add(new Label { Text = "Кухня:", AutoSize = true });
            cuisineBox = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList, Items = { "", "italian", "japanese", "russian", "mexican", "french", "chinese", "indian" }, Width = 100 };
            top.Controls.Add(cuisineBox);
            top.Controls.Add(new Label { Text = "Время (мин):", AutoSize = true });
            timeBox = new TextBox { Width = 60 };
            top.Controls.Add(timeBox);
            top.Controls.Add(new Label { Text = "Сложность:", AutoSize = true });
            diffBox = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList, Items = { "", "easy", "medium", "hard" }, Width = 80 };
            top.Controls.Add(diffBox);
            var genBtn = new Button { Text = "🎲 Сгенерировать" };
            genBtn.Click += (s, e) => Generate();
            top.Controls.Add(genBtn);
            var menuBtn = new Button { Text = "🍽️ Меню (3)" };
            menuBtn.Click += (s, e) => GenerateMenu(3);
            top.Controls.Add(menuBtn);
            Controls.Add(top);

            resultBox = new TextBox { Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Vertical, Dock = DockStyle.Fill };
            Controls.Add(resultBox);

            var bottom = new FlowLayoutPanel { Dock = DockStyle.Bottom, Padding = new Padding(5) };
            var favBtn = new Button { Text = "⭐ Добавить в избранное" };
            favBtn.Click += (s, e) => AddFavorite();
            bottom.Controls.Add(favBtn);
            var listFavBtn = new Button { Text = "📋 Избранное" };
            listFavBtn.Click += (s, e) => ShowFavorites();
            bottom.Controls.Add(listFavBtn);
            Controls.Add(bottom);
        }

        void Generate()
        {
            string type = typeBox.SelectedItem.ToString();
            if (string.IsNullOrEmpty(type)) type = null;
            string cuisine = cuisineBox.SelectedItem.ToString();
            if (string.IsNullOrEmpty(cuisine)) cuisine = null;
            string timeStr = timeBox.Text.Trim();
            int? maxTime = string.IsNullOrEmpty(timeStr) ? (int?)null : int.Parse(timeStr);
            string diff = diffBox.SelectedItem.ToString();
            if (string.IsNullOrEmpty(diff)) diff = null;
            var dish = forge.Generate(type, cuisine, maxTime, diff);
            if (dish != null)
            {
                currentDish = dish;
                resultBox.Text = forge.FormatDish(dish);
            }
            else
            {
                resultBox.Text = "❌ Блюда не найдены";
                currentDish = null;
            }
        }

        void GenerateMenu(int count)
        {
            string type = typeBox.SelectedItem.ToString();
            if (string.IsNullOrEmpty(type)) type = null;
            string cuisine = cuisineBox.SelectedItem.ToString();
            if (string.IsNullOrEmpty(cuisine)) cuisine = null;
            string timeStr = timeBox.Text.Trim();
            int? maxTime = string.IsNullOrEmpty(timeStr) ? (int?)null : int.Parse(timeStr);
            string diff = diffBox.SelectedItem.ToString();
            if (string.IsNullOrEmpty(diff)) diff = null;
            var menu = forge.GenerateMenu(count, type, cuisine, maxTime, diff);
            resultBox.Text = "";
            if (menu.Any())
            {
                resultBox.AppendText($"🍽️ Меню из {menu.Count} блюд:\n\n");
                for (int i = 0; i < menu.Count; i++)
                {
                    var d = menu[i];
                    resultBox.AppendText($"{i+1}. {d.Name} ({d.Type}, {d.Cuisine}, {d.Time} мин, {d.Difficulty})\n");
                    resultBox.AppendText($"   {d.Description}\n\n");
                }
            }
            else
            {
                resultBox.AppendText("❌ Недостаточно блюд");
            }
            currentDish = null;
        }

        void AddFavorite()
        {
            if (currentDish == null) { MessageBox.Show("Сначала сгенерируйте блюдо"); return; }
            if (forge.AddFavorite(currentDish.Name)) MessageBox.Show("Добавлено в избранное");
            else MessageBox.Show("Уже в избранном");
        }

        void ShowFavorites()
        {
            var favs = forge.GetFavorites();
            if (!favs.Any()) { MessageBox.Show("Избранное пусто"); return; }
            var dialog = new Form { Text = "⭐ Избранное", Size = new System.Drawing.Size(500, 400), StartPosition = FormStartPosition.CenterParent };
            var area = new TextBox { Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Vertical, Dock = DockStyle.Fill };
            favs.ForEach(d => area.AppendText($"🍽️ {d.Name}\n  Тип: {d.Type}, Кухня: {d.Cuisine}, Время: {d.Time} мин, Сложность: {d.Difficulty}\n\n"));
            dialog.Controls.Add(area);
            dialog.ShowDialog();
        }
    }
}
