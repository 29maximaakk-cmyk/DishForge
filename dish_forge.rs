// dish_forge.rs - Генератор случайных блюд на Rust (CLI)
use serde::{Serialize, Deserialize};
use std::collections::HashSet;
use std::fs;
use std::io::{self, Write, BufRead};
use std::path::Path;
use std::str::FromStr;
use rand::seq::SliceRandom;
use rand::thread_rng;

#[derive(Serialize, Deserialize, Clone)]
struct Dish {
    name: String,
    dish_type: String,
    cuisine: String,
    time: u32,
    difficulty: String,
    description: String,
    ingredients: Vec<String>,
    instructions: Vec<String>,
}

#[derive(Serialize, Deserialize)]
struct Forge {
    dishes: Vec<Dish>,
    favorites: Vec<String>,
}

const DATA_FILE: &str = "dishes.json";
const FAV_FILE: &str = "favorites.json";

impl Forge {
    fn load() -> Self {
        let mut f = Forge {
            dishes: vec![],
            favorites: vec![],
        };
        if Path::new(DATA_FILE).exists() {
            if let Ok(data) = fs::read_to_string(DATA_FILE) {
                if let Ok(dishes) = serde_json::from_str(&data) {
                    f.dishes = dishes;
                }
            }
        }
        if f.dishes.is_empty() {
            f.dishes = default_dishes();
            f.save();
        }
        if Path::new(FAV_FILE).exists() {
            if let Ok(data) = fs::read_to_string(FAV_FILE) {
                if let Ok(favs) = serde_json::from_str(&data) {
                    f.favorites = favs;
                }
            }
        }
        f
    }

    fn save(&self) {
        let data = serde_json::to_string_pretty(&self.dishes).unwrap();
        fs::write(DATA_FILE, data).unwrap();
        let fav_data = serde_json::to_string_pretty(&self.favorites).unwrap();
        fs::write(FAV_FILE, fav_data).unwrap();
    }

    fn generate(&self, dish_type: Option<&str>, cuisine: Option<&str>, max_time: Option<u32>, difficulty: Option<&str>) -> Option<Dish> {
        let mut filtered = self.dishes.clone();
        if let Some(t) = dish_type {
            filtered.retain(|d| d.dish_type == t);
        }
        if let Some(c) = cuisine {
            filtered.retain(|d| d.cuisine == c);
        }
        if let Some(t) = max_time {
            filtered.retain(|d| d.time <= t);
        }
        if let Some(d) = difficulty {
            filtered.retain(|dsh| dsh.difficulty == d);
        }
        if filtered.is_empty() {
            return None;
        }
        let mut rng = thread_rng();
        filtered.choose(&mut rng).cloned()
    }

    fn generate_menu(&self, count: usize, dish_type: Option<&str>, cuisine: Option<&str>, max_time: Option<u32>, difficulty: Option<&str>) -> Vec<Dish> {
        let mut available = self.dishes.clone();
        if let Some(t) = dish_type {
            available.retain(|d| d.dish_type == t);
        }
        if let Some(c) = cuisine {
            available.retain(|d| d.cuisine == c);
        }
        if let Some(t) = max_time {
            available.retain(|d| d.time <= t);
        }
        if let Some(d) = difficulty {
            available.retain(|dsh| dsh.difficulty == d);
        }
        let count = count.min(available.len());
        let mut rng = thread_rng();
        available.shuffle(&mut rng);
        available[..count].to_vec()
    }

    fn add_favorite(&mut self, name: &str) -> bool {
        if self.favorites.contains(&name.to_string()) {
            return false;
        }
        self.favorites.push(name.to_string());
        self.save();
        true
    }

    fn remove_favorite(&mut self, name: &str) -> bool {
        let idx = self.favorites.iter().position(|n| n == name);
        if let Some(idx) = idx {
            self.favorites.remove(idx);
            self.save();
            return true;
        }
        false
    }

    fn get_favorites(&self) -> Vec<Dish> {
        let mut result = vec![];
        for d in &self.dishes {
            if self.favorites.contains(&d.name) {
                result.push(d.clone());
            }
        }
        result
    }
}

fn default_dishes() -> Vec<Dish> {
    vec![
        Dish {
            name: "Овсянка с ягодами".to_string(),
            dish_type: "breakfast".to_string(),
            cuisine: "russian".to_string(),
            time: 10,
            difficulty: "easy".to_string(),
            description: "Полезный завтрак из овсяных хлопьев с ягодами и мёдом.".to_string(),
            ingredients: vec!["Овсяные хлопья 100г".to_string(), "Молоко 200мл".to_string(), "Ягоды 50г".to_string(), "Мёд 1 ст.л.".to_string()],
            instructions: vec!["Вскипятить молоко".to_string(), "Добавить хлопья, варить 5 мин".to_string(), "Добавить ягоды и мёд".to_string()],
        },
        Dish {
            name: "Паста Карбонара".to_string(),
            dish_type: "lunch".to_string(),
            cuisine: "italian".to_string(),
            time: 25,
            difficulty: "medium".to_string(),
            description: "Классическая итальянская паста с беконом и пармезаном.".to_string(),
            ingredients: vec!["Паста 200г".to_string(), "Бекон 100г".to_string(), "Яйца 2 шт".to_string(), "Пармезан 50г".to_string(), "Сливки 100мл".to_string()],
            instructions: vec!["Отварить пасту".to_string(), "Обжарить бекон".to_string(), "Смешать яйца, сыр и сливки".to_string(), "Соединить с пастой".to_string()],
        },
    ]
}

fn format_dish(d: &Dish) -> String {
    let mut lines = vec![];
    lines.push(format!("🍽️ {}", d.name));
    lines.push(format!("  Тип: {}", d.dish_type));
    lines.push(format!("  Кухня: {}", d.cuisine));
    lines.push(format!("  Время: {} мин", d.time));
    lines.push(format!("  Сложность: {}", d.difficulty));
    lines.push(format!("  Описание: {}", d.description));
    lines.push("  Ингредиенты:".to_string());
    for ing in &d.ingredients {
        lines.push(format!("    - {}", ing));
    }
    lines.push("  Приготовление:".to_string());
    for (i, step) in d.instructions.iter().enumerate() {
        lines.push(format!("    {}. {}", i+1, step));
    }
    lines.join("\n")
}

fn read_line(prompt: &str) -> String {
    print!("{}", prompt);
    io::stdout().flush().unwrap();
    let mut input = String::new();
    io::stdin().read_line(&mut input).unwrap();
    input.trim().to_string()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        interactive_mode();
        return;
    }
    let mut forge = Forge::load();
    match args[1].as_str() {
        "generate" => {
            let mut dish_type = None;
            let mut cuisine = None;
            let mut max_time = None;
            let mut difficulty = None;
            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--type" => { dish_type = Some(args[i+1].clone()); i += 2; }
                    "--cuisine" => { cuisine = Some(args[i+1].clone()); i += 2; }
                    "--time" => { max_time = Some(args[i+1].parse().unwrap_or(0)); i += 2; }
                    "--difficulty" => { difficulty = Some(args[i+1].clone()); i += 2; }
                    _ => { i += 1; }
                }
            }
            if let Some(dish) = forge.generate(dish_type.as_deref(), cuisine.as_deref(), max_time, difficulty.as_deref()) {
                println!("{}", format_dish(&dish));
            } else {
                println!("❌ Блюда не найдены");
            }
        }
        "menu" => {
            let mut count = 3;
            let mut dish_type = None;
            let mut cuisine = None;
            let mut max_time = None;
            let mut difficulty = None;
            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--count" => { count = args[i+1].parse().unwrap_or(3); i += 2; }
                    "--type" => { dish_type = Some(args[i+1].clone()); i += 2; }
                    "--cuisine" => { cuisine = Some(args[i+1].clone()); i += 2; }
                    "--time" => { max_time = Some(args[i+1].parse().unwrap_or(0)); i += 2; }
                    "--difficulty" => { difficulty = Some(args[i+1].clone()); i += 2; }
                    _ => { i += 1; }
                }
            }
            let dishes = forge.generate_menu(count, dish_type.as_deref(), cuisine.as_deref(), max_time, difficulty.as_deref());
            if !dishes.is_empty() {
                println!("🍽️ Меню из {} блюд:", dishes.len());
                for (i, d) in dishes.iter().enumerate() {
                    println!("\n{}. {} ({}, {}, {} мин, {})", i+1, d.name, d.dish_type, d.cuisine, d.time, d.difficulty);
                    println!("   {}", d.description);
                }
            } else {
                println!("❌ Недостаточно блюд");
            }
        }
        "list" => {
            let mut dish_type = None;
            let mut cuisine = None;
            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--type" => { dish_type = Some(args[i+1].clone()); i += 2; }
                    "--cuisine" => { cuisine = Some(args[i+1].clone()); i += 2; }
                    _ => { i += 1; }
                }
            }
            let mut dishes = forge.dishes.clone();
            if let Some(t) = dish_type {
                dishes.retain(|d| d.dish_type == t);
            }
            if let Some(c) = cuisine {
                dishes.retain(|d| d.cuisine == c);
            }
            for d in dishes {
                println!("{} ({}, {}, {} мин)", d.name, d.dish_type, d.cuisine, d.time);
            }
        }
        "favorites" => {
            if args.len() > 3 && args[2] == "add" {
                let name = args[3].clone();
                if forge.add_favorite(&name) {
                    println!("✅ '{}' добавлен в избранное", name);
                } else {
                    println!("⚠️ '{}' уже в избранном или не существует", name);
                }
            } else if args.len() > 3 && args[2] == "remove" {
                let name = args[3].clone();
                if forge.remove_favorite(&name) {
                    println!("✅ '{}' удалён из избранного", name);
                } else {
                    println!("❌ '{}' не найден в избранном", name);
                }
            } else {
                let favs = forge.get_favorites();
                if !favs.is_empty() {
                    println!("⭐ Избранное:");
                    for d in favs {
                        println!("  {} ({}, {})", d.name, d.dish_type, d.cuisine);
                    }
                } else {
                    println!("Избранное пусто");
                }
            }
        }
        _ => interactive_mode(),
    }
}

fn interactive_mode() {
    let mut forge = Forge::load();
    let stdin = io::stdin();
    let mut stdout = io::stdout();
    loop {
        println!("\n🍳 DishForge - Генератор блюд (интерактивный)");
        println!("1. Сгенерировать случайное блюдо");
        println!("2. Сгенерировать меню");
        println!("3. Список всех блюд");
        println!("4. Избранное");
        println!("0. Выход");
        print!("Выберите действие: ");
        stdout.flush().unwrap();
        let mut choice = String::new();
        stdin.read_line(&mut choice).unwrap();
        match choice.trim() {
            "0" => break,
            "1" => {
                let t = read_line("Тип (Enter пропустить): ");
                let t = if t.is_empty() { None } else { Some(t.as_str()) };
                let c = read_line("Кухня (Enter пропустить): ");
                let c = if c.is_empty() { None } else { Some(c.as_str()) };
                let time_str = read_line("Макс. время (мин, Enter пропустить): ");
                let max_time = if time_str.is_empty() { None } else { Some(time_str.parse::<u32>().unwrap_or(0)) };
                let diff = read_line("Сложность (easy/medium/hard, Enter пропустить): ");
                let diff = if diff.is_empty() { None } else { Some(diff.as_str()) };
                if let Some(dish) = forge.generate(t, c, max_time, diff) {
                    println!("{}", format_dish(&dish));
                } else {
                    println!("❌ Блюда не найдены");
                }
            }
            "2" => {
                let count_str = read_line("Количество блюд (по умолчанию 3): ");
                let count = if count_str.is_empty() { 3 } else { count_str.parse::<usize>().unwrap_or(3) };
                let t = read_line("Тип (Enter пропустить): ");
                let t = if t.is_empty() { None } else { Some(t.as_str()) };
                let c = read_line("Кухня (Enter пропустить): ");
                let c = if c.is_empty() { None } else { Some(c.as_str()) };
                let time_str = read_line("Макс. время (мин, Enter пропустить): ");
                let max_time = if time_str.is_empty() { None } else { Some(time_str.parse::<u32>().unwrap_or(0)) };
                let diff = read_line("Сложность (Enter пропустить): ");
                let diff = if diff.is_empty() { None } else { Some(diff.as_str()) };
                let dishes = forge.generate_menu(count, t, c, max_time, diff);
                if !dishes.is_empty() {
                    println!("🍽️ Меню из {} блюд:", dishes.len());
                    for (i, d) in dishes.iter().enumerate() {
                        println!("\n{}. {} ({}, {}, {} мин, {})", i+1, d.name, d.dish_type, d.cuisine, d.time, d.difficulty);
                        println!("   {}", d.description);
                    }
                } else {
                    println!("❌ Недостаточно блюд");
                }
            }
            "3" => {
                let t = read_line("Тип (Enter пропустить): ");
                let c = read_line("Кухня (Enter пропустить): ");
                let mut dishes = forge.dishes.clone();
                if !t.is_empty() {
                    dishes.retain(|d| d.dish_type == t);
                }
                if !c.is_empty() {
                    dishes.retain(|d| d.cuisine == c);
                }
                for d in dishes {
                    println!("  {} ({}, {}, {} мин)", d.name, d.dish_type, d.cuisine, d.time);
                }
            }
            "4" => {
                let favs = forge.get_favorites();
                println!("⭐ Избранное:");
                if !favs.is_empty() {
                    for d in favs {
                        println!("  {} ({}, {})", d.name, d.dish_type, d.cuisine);
                    }
                } else {
                    println!("  Пусто");
                }
                println!("\n1. Добавить в избранное");
                println!("2. Удалить из избранного");
                println!("3. Назад");
                let sub = read_line("Выберите: ");
                if sub == "1" {
                    let name = read_line("Название блюда: ");
                    if forge.add_favorite(&name) {
                        println!("✅ '{}' добавлен", name);
                    } else {
                        println!("⚠️ '{}' уже в избранном или не существует", name);
                    }
                } else if sub == "2" {
                    let name = read_line("Название блюда: ");
                    if forge.remove_favorite(&name) {
                        println!("✅ '{}' удалён", name);
                    } else {
                        println!("❌ '{}' не найден", name);
                    }
                }
            }
            _ => println!("Неверный выбор"),
        }
    }
}
