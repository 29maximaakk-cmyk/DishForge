#!/usr/bin/env node
/**
 * dish_forge.js - Генератор случайных блюд на JavaScript (Node.js CLI + веб)
 */
const fs = require('fs');
const path = require('path');
const { program } = require('commander');

const DATA_FILE = path.join(__dirname, 'dishes.json');
const FAVORITES_FILE = path.join(__dirname, 'favorites.json');

class Dish {
    constructor(name, type, cuisine, time, difficulty, description, ingredients, instructions) {
        this.name = name;
        this.type = type;
        this.cuisine = cuisine;
        this.time = time;
        this.difficulty = difficulty;
        this.description = description;
        this.ingredients = ingredients;
        this.instructions = instructions;
    }
}

class DishForge {
    constructor() {
        this.dishes = [];
        this.favorites = [];
        this.load();
        this.loadFavorites();
    }

    load() {
        if (fs.existsSync(DATA_FILE)) {
            try {
                const data = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
                this.dishes = data.map(d => new Dish(d.name, d.type, d.cuisine, d.time, d.difficulty, d.description, d.ingredients, d.instructions));
                return;
            } catch {}
        }
        this.dishes = this.defaultDishes();
        this.save();
    }

    save() {
        fs.writeFileSync(DATA_FILE, JSON.stringify(this.dishes, null, 2));
    }

    loadFavorites() {
        if (fs.existsSync(FAVORITES_FILE)) {
            try {
                this.favorites = JSON.parse(fs.readFileSync(FAVORITES_FILE, 'utf8'));
            } catch {}
        }
    }

    saveFavorites() {
        fs.writeFileSync(FAVORITES_FILE, JSON.stringify(this.favorites, null, 2));
    }

    defaultDishes() {
        return [
            new Dish("Овсянка с ягодами", "breakfast", "russian", 10, "easy",
                "Полезный завтрак из овсяных хлопьев с ягодами и мёдом.",
                ["Овсяные хлопья 100г", "Молоко 200мл", "Ягоды 50г", "Мёд 1 ст.л."],
                ["Вскипятить молоко", "Добавить хлопья, варить 5 мин", "Добавить ягоды и мёд"]),
            new Dish("Паста Карбонара", "lunch", "italian", 25, "medium",
                "Классическая итальянская паста с беконом и пармезаном.",
                ["Паста 200г", "Бекон 100г", "Яйца 2 шт", "Пармезан 50г", "Сливки 100мл"],
                ["Отварить пасту", "Обжарить бекон", "Смешать яйца, сыр и сливки", "Соединить с пастой"]),
            new Dish("Суши Филадельфия", "dinner", "japanese", 40, "hard",
                "Роллы с лососем, сливочным сыром и авокадо.",
                ["Рис для суши 200г", "Нори 4 шт", "Лосось 150г", "Сливочный сыр 100г", "Авокадо 1 шт"],
                ["Сварить рис", "Нарезать лосось и авокадо", "Собрать роллы", "Нарезать и подавать"]),
            new Dish("Борщ", "dinner", "russian", 60, "medium",
                "Традиционный украинский суп со свеклой и капустой.",
                ["Свекла 2 шт", "Капуста 200г", "Картофель 3 шт", "Мясо 300г", "Лук 1 шт", "Морковь 1 шт"],
                ["Сварить бульон", "Обжарить лук и морковь", "Добавить свеклу", "Соединить с бульоном и варить"]),
            new Dish("Чизкейк", "dessert", "french", 50, "medium",
                "Нежный творожный десерт с печеньем и ягодами.",
                ["Печенье 200г", "Масло 100г", "Творог 500г", "Сахар 150г", "Яйца 3 шт", "Сливки 200мл"],
                ["Измельчить печенье", "Смешать с маслом", "Взбить творог с сахаром и яйцами", "Запекать 40 мин"]),
        ];
    }

    generate(type, cuisine, maxTime, difficulty) {
        let filtered = this.dishes;
        if (type) filtered = filtered.filter(d => d.type === type);
        if (cuisine) filtered = filtered.filter(d => d.cuisine === cuisine);
        if (maxTime) filtered = filtered.filter(d => d.time <= maxTime);
        if (difficulty) filtered = filtered.filter(d => d.difficulty === difficulty);
        if (!filtered.length) return null;
        return filtered[Math.floor(Math.random() * filtered.length)];
    }

    generateMenu(count, filters = {}) {
        let available = this.dishes;
        if (filters.type) available = available.filter(d => d.type === filters.type);
        if (filters.cuisine) available = available.filter(d => d.cuisine === filters.cuisine);
        if (filters.maxTime) available = available.filter(d => d.time <= filters.maxTime);
        if (filters.difficulty) available = available.filter(d => d.difficulty === filters.difficulty);
        if (available.length < count) count = available.length;
        const shuffled = [...available].sort(() => Math.random() - 0.5);
        return shuffled.slice(0, count);
    }

    getTypes() { return [...new Set(this.dishes.map(d => d.type))].sort(); }
    getCuisines() { return [...new Set(this.dishes.map(d => d.cuisine))].sort(); }
    getDifficulties() { return [...new Set(this.dishes.map(d => d.difficulty))].sort(); }

    addFavorite(name) {
        if (!this.favorites.includes(name)) {
            this.favorites.push(name);
            this.saveFavorites();
            return true;
        }
        return false;
    }

    removeFavorite(name) {
        const idx = this.favorites.indexOf(name);
        if (idx !== -1) {
            this.favorites.splice(idx, 1);
            this.saveFavorites();
            return true;
        }
        return false;
    }

    getFavorites() {
        return this.dishes.filter(d => this.favorites.includes(d.name));
    }

    formatDish(dish) {
        let lines = [];
        lines.push(`🍽️ ${dish.name}`);
        lines.push(`  Тип: ${dish.type}`);
        lines.push(`  Кухня: ${dish.cuisine}`);
        lines.push(`  Время: ${dish.time} мин`);
        lines.push(`  Сложность: ${dish.difficulty}`);
        lines.push(`  Описание: ${dish.description}`);
        lines.push("  Ингредиенты:");
        dish.ingredients.forEach(ing => lines.push(`    - ${ing}`));
        lines.push("  Приготовление:");
        dish.instructions.forEach((step, i) => lines.push(`    ${i+1}. ${step}`));
        return lines.join("\n");
    }
}

program
    .command('generate')
    .option('--type <type>', 'Тип блюда')
    .option('--cuisine <cuisine>', 'Кухня')
    .option('--time <time>', 'Макс. время (мин)', parseInt)
    .option('--difficulty <difficulty>', 'Сложность')
    .action((options) => {
        const forge = new DishForge();
        const dish = forge.generate(options.type, options.cuisine, options.time, options.difficulty);
        if (dish) console.log(forge.formatDish(dish));
        else console.log('❌ Блюда не найдены');
    });

program
    .command('random-menu')
    .option('--count <count>', 'Количество блюд', parseInt, 3)
    .option('--type <type>', 'Тип блюда')
    .option('--cuisine <cuisine>', 'Кухня')
    .option('--time <time>', 'Макс. время', parseInt)
    .option('--difficulty <difficulty>', 'Сложность')
    .action((options) => {
        const forge = new DishForge();
        const filters = {};
        if (options.type) filters.type = options.type;
        if (options.cuisine) filters.cuisine = options.cuisine;
        if (options.time) filters.maxTime = options.time;
        if (options.difficulty) filters.difficulty = options.difficulty;
        const dishes = forge.generateMenu(options.count, filters);
        if (dishes.length) {
            console.log(`🍽️ Меню из ${dishes.length} блюд:`);
            dishes.forEach((d, i) => {
                console.log(`\n${i+1}. ${d.name} (${d.type}, ${d.cuisine}, ${d.time} мин, ${d.difficulty})`);
                console.log(`   ${d.description}`);
            });
        } else {
            console.log('❌ Недостаточно блюд');
        }
    });

program
    .command('list')
    .option('--type <type>', 'Фильтр по типу')
    .option('--cuisine <cuisine>', 'Фильтр по кухне')
    .action((options) => {
        const forge = new DishForge();
        let dishes = forge.dishes;
        if (options.type) dishes = dishes.filter(d => d.type === options.type);
        if (options.cuisine) dishes = dishes.filter(d => d.cuisine === options.cuisine);
        dishes.forEach(d => console.log(`${d.name} (${d.type}, ${d.cuisine}, ${d.time} мин)`));
    });

program
    .command('favorites')
    .command('add <name>').action((name) => {
        const forge = new DishForge();
        if (forge.addFavorite(name)) console.log(`✅ '${name}' добавлен в избранное`);
        else console.log(`⚠️ '${name}' уже в избранном или не существует`);
    })
    .command('remove <name>').action((name) => {
        const forge = new DishForge();
        if (forge.removeFavorite(name)) console.log(`✅ '${name}' удалён из избранного`);
        else console.log(`❌ '${name}' не найден в избранном`);
    })
    .command('list').action(() => {
        const forge = new DishForge();
        const favs = forge.getFavorites();
        if (favs.length) {
            console.log('⭐ Избранное:');
            favs.forEach(d => console.log(`  ${d.name} (${d.type}, ${d.cuisine})`));
        } else {
            console.log('Избранное пусто');
        }
    });

if (process.argv.length <= 2) {
    // interactive mode
    const forge = new DishForge();
    const readline = require('readline');
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    const prompt = (q) => new Promise(resolve => rl.question(q, resolve));

    (async () => {
        while (true) {
            console.log('\n🍳 DishForge - Генератор блюд (интерактивный)');
            console.log('1. Сгенерировать случайное блюдо');
            console.log('2. Сгенерировать меню');
            console.log('3. Список всех блюд');
            console.log('4. Избранное');
            console.log('0. Выход');
            const choice = await prompt('Выберите действие: ');
            switch (choice.trim()) {
                case '0': rl.close(); return;
                case '1': {
                    const t = await prompt('Тип (Enter пропустить): ') || undefined;
                    const c = await prompt('Кухня (Enter пропустить): ') || undefined;
                    const timeStr = await prompt('Макс. время (мин, Enter пропустить): ');
                    const maxTime = timeStr ? parseInt(timeStr) : undefined;
                    const diff = await prompt('Сложность (easy/medium/hard, Enter пропустить): ') || undefined;
                    const dish = forge.generate(t, c, maxTime, diff);
                    if (dish) console.log(forge.formatDish(dish));
                    else console.log('❌ Блюда не найдены');
                    break;
                }
                case '2': {
                    const count = parseInt(await prompt('Количество блюд (по умолчанию 3): ') || '3');
                    const t = await prompt('Тип (Enter пропустить): ') || undefined;
                    const c = await prompt('Кухня (Enter пропустить): ') || undefined;
                    const timeStr = await prompt('Макс. время (мин, Enter пропустить): ');
                    const maxTime = timeStr ? parseInt(timeStr) : undefined;
                    const diff = await prompt('Сложность (Enter пропустить): ') || undefined;
                    const filters = {};
                    if (t) filters.type = t;
                    if (c) filters.cuisine = c;
                    if (maxTime) filters.maxTime = maxTime;
                    if (diff) filters.difficulty = diff;
                    const dishes = forge.generateMenu(count, filters);
                    if (dishes.length) {
                        console.log(`🍽️ Меню из ${dishes.length} блюд:`);
                        dishes.forEach((d, i) => {
                            console.log(`\n${i+1}. ${d.name} (${d.type}, ${d.cuisine}, ${d.time} мин, ${d.difficulty})`);
                            console.log(`   ${d.description}`);
                        });
                    } else {
                        console.log('❌ Недостаточно блюд');
                    }
                    break;
                }
                case '3': {
                    const t = await prompt('Тип (Enter пропустить): ') || undefined;
                    const c = await prompt('Кухня (Enter пропустить): ') || undefined;
                    let dishes = forge.dishes;
                    if (t) dishes = dishes.filter(d => d.type === t);
                    if (c) dishes = dishes.filter(d => d.cuisine === c);
                    dishes.forEach(d => console.log(`  ${d.name} (${d.type}, ${d.cuisine}, ${d.time} мин)`));
                    break;
                }
                case '4': {
                    const favs = forge.getFavorites();
                    console.log('⭐ Избранное:');
                    if (favs.length) favs.forEach(d => console.log(`  ${d.name} (${d.type}, ${d.cuisine})`));
                    else console.log('  Пусто');
                    console.log('\n1. Добавить в избранное');
                    console.log('2. Удалить из избранного');
                    console.log('3. Назад');
                    const sub = await prompt('Выберите: ');
                    if (sub === '1') {
                        const name = await prompt('Название блюда: ');
                        if (forge.addFavorite(name)) console.log(`✅ '${name}' добавлен`);
                        else console.log(`⚠️ '${name}' уже в избранном или не существует`);
                    } else if (sub === '2') {
                        const name = await prompt('Название блюда: ');
                        if (forge.removeFavorite(name)) console.log(`✅ '${name}' удалён`);
                        else console.log(`❌ '${name}' не найден`);
                    }
                    break;
                }
                default: console.log('Неверный выбор');
            }
        }
    })();
} else {
    program.parse(process.argv);
}
