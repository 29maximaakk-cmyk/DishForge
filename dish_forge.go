// dish_forge.go - Генератор случайных блюд на Go (CLI)
package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"strings"
	"time"
)

type Dish struct {
	Name         string   `json:"name"`
	Type         string   `json:"type"`
	Cuisine      string   `json:"cuisine"`
	Time         int      `json:"time"`
	Difficulty   string   `json:"difficulty"`
	Description  string   `json:"description"`
	Ingredients  []string `json:"ingredients"`
	Instructions []string `json:"instructions"`
}

type Forge struct {
	Dishes    []Dish   `json:"dishes"`
	Favorites []string `json:"favorites"`
}

const dataFile = "dishes.json"
const favFile = "favorites.json"

func loadForge() *Forge {
	var f Forge
	file, err := os.ReadFile(dataFile)
	if err != nil {
		f.Dishes = defaultDishes()
		f.Favorites = []string{}
		saveForge(&f)
		return &f
	}
	err = json.Unmarshal(file, &f)
	if err != nil {
		f.Dishes = defaultDishes()
		f.Favorites = []string{}
	}
	// load favorites separately
	favData, err := os.ReadFile(favFile)
	if err == nil {
		var favs []string
		json.Unmarshal(favData, &favs)
		f.Favorites = favs
	}
	return &f
}

func saveForge(f *Forge) {
	data, _ := json.MarshalIndent(f.Dishes, "", "  ")
	os.WriteFile(dataFile, data, 0644)
	favData, _ := json.MarshalIndent(f.Favorites, "", "  ")
	os.WriteFile(favFile, favData, 0644)
}

func defaultDishes() []Dish {
	return []Dish{
		{"Овсянка с ягодами", "breakfast", "russian", 10, "easy",
			"Полезный завтрак из овсяных хлопьев с ягодами и мёдом.",
			[]string{"Овсяные хлопья 100г", "Молоко 200мл", "Ягоды 50г", "Мёд 1 ст.л."},
			[]string{"Вскипятить молоко", "Добавить хлопья, варить 5 мин", "Добавить ягоды и мёд"}},
		{"Паста Карбонара", "lunch", "italian", 25, "medium",
			"Классическая итальянская паста с беконом и пармезаном.",
			[]string{"Паста 200г", "Бекон 100г", "Яйца 2 шт", "Пармезан 50г", "Сливки 100мл"},
			[]string{"Отварить пасту", "Обжарить бекон", "Смешать яйца, сыр и сливки", "Соединить с пастой"}},
		{"Суши Филадельфия", "dinner", "japanese", 40, "hard",
			"Роллы с лососем, сливочным сыром и авокадо.",
			[]string{"Рис для суши 200г", "Нори 4 шт", "Лосось 150г", "Сливочный сыр 100г", "Авокадо 1 шт"},
			[]string{"Сварить рис", "Нарезать лосось и авокадо", "Собрать роллы", "Нарезать и подавать"}},
	}
}

func (f *Forge) generate(dishType, cuisine, difficulty string, maxTime int) *Dish {
	filtered := f.Dishes
	if dishType != "" {
		filtered = filterByType(filtered, dishType)
	}
	if cuisine != "" {
		filtered = filterByCuisine(filtered, cuisine)
	}
	if maxTime > 0 {
		filtered = filterByTime(filtered, maxTime)
	}
	if difficulty != "" {
		filtered = filterByDifficulty(filtered, difficulty)
	}
	if len(filtered) == 0 {
		return nil
	}
	rand.Seed(time.Now().UnixNano())
	return &filtered[rand.Intn(len(filtered))]
}

func filterByType(dishes []Dish, t string) []Dish {
	var res []Dish
	for _, d := range dishes {
		if d.Type == t {
			res = append(res, d)
		}
	}
	return res
}
func filterByCuisine(dishes []Dish, c string) []Dish {
	var res []Dish
	for _, d := range dishes {
		if d.Cuisine == c {
			res = append(res, d)
		}
	}
	return res
}
func filterByTime(dishes []Dish, maxTime int) []Dish {
	var res []Dish
	for _, d := range dishes {
		if d.Time <= maxTime {
			res = append(res, d)
		}
	}
	return res
}
func filterByDifficulty(dishes []Dish, diff string) []Dish {
	var res []Dish
	for _, d := range dishes {
		if d.Difficulty == diff {
			res = append(res, d)
		}
	}
	return res
}

func (f *Forge) generateMenu(count int, dishType, cuisine, difficulty string, maxTime int) []Dish {
	available := f.Dishes
	if dishType != "" {
		available = filterByType(available, dishType)
	}
	if cuisine != "" {
		available = filterByCuisine(available, cuisine)
	}
	if maxTime > 0 {
		available = filterByTime(available, maxTime)
	}
	if difficulty != "" {
		available = filterByDifficulty(available, difficulty)
	}
	if len(available) < count {
		count = len(available)
	}
	rand.Seed(time.Now().UnixNano())
	shuffled := make([]Dish, len(available))
	copy(shuffled, available)
	rand.Shuffle(len(shuffled), func(i, j int) { shuffled[i], shuffled[j] = shuffled[j], shuffled[i] })
	return shuffled[:count]
}

func (f *Forge) addFavorite(name string) bool {
	for _, n := range f.Favorites {
		if n == name {
			return false
		}
	}
	f.Favorites = append(f.Favorites, name)
	saveForge(f)
	return true
}

func (f *Forge) removeFavorite(name string) bool {
	for i, n := range f.Favorites {
		if n == name {
			f.Favorites = append(f.Favorites[:i], f.Favorites[i+1:]...)
			saveForge(f)
			return true
		}
	}
	return false
}

func (f *Forge) getFavorites() []Dish {
	var result []Dish
	for _, d := range f.Dishes {
		for _, n := range f.Favorites {
			if d.Name == n {
				result = append(result, d)
				break
			}
		}
	}
	return result
}

func formatDish(d Dish) string {
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("🍽️ %s\n", d.Name))
	sb.WriteString(fmt.Sprintf("  Тип: %s\n", d.Type))
	sb.WriteString(fmt.Sprintf("  Кухня: %s\n", d.Cuisine))
	sb.WriteString(fmt.Sprintf("  Время: %d мин\n", d.Time))
	sb.WriteString(fmt.Sprintf("  Сложность: %s\n", d.Difficulty))
	sb.WriteString(fmt.Sprintf("  Описание: %s\n", d.Description))
	sb.WriteString("  Ингредиенты:\n")
	for _, ing := range d.Ingredients {
		sb.WriteString(fmt.Sprintf("    - %s\n", ing))
	}
	sb.WriteString("  Приготовление:\n")
	for i, step := range d.Instructions {
		sb.WriteString(fmt.Sprintf("    %d. %s\n", i+1, step))
	}
	return sb.String()
}

func main() {
	var (
		cmd        string
		dishType   string
		cuisine    string
		maxTime    int
		difficulty string
		count      int
		name       string
	)
	flag.StringVar(&cmd, "cmd", "", "Команда: generate, menu, list, favorites")
	flag.StringVar(&dishType, "type", "", "Тип блюда")
	flag.StringVar(&cuisine, "cuisine", "", "Кухня")
	flag.IntVar(&maxTime, "time", 0, "Макс. время")
	flag.StringVar(&difficulty, "difficulty", "", "Сложность")
	flag.IntVar(&count, "count", 3, "Количество блюд в меню")
	flag.StringVar(&name, "name", "", "Название блюда для избранного")
	flag.Parse()

	forge := loadForge()

	switch cmd {
	case "generate":
		dish := forge.generate(dishType, cuisine, difficulty, maxTime)
		if dish != nil {
			fmt.Println(formatDish(*dish))
		} else {
			fmt.Println("❌ Блюда не найдены")
		}
	case "menu":
		dishes := forge.generateMenu(count, dishType, cuisine, difficulty, maxTime)
		if len(dishes) > 0 {
			fmt.Printf("🍽️ Меню из %d блюд:\n", len(dishes))
			for i, d := range dishes {
				fmt.Printf("\n%d. %s (%s, %s, %d мин, %s)\n", i+1, d.Name, d.Type, d.Cuisine, d.Time, d.Difficulty)
				fmt.Printf("   %s\n", d.Description)
			}
		} else {
			fmt.Println("❌ Недостаточно блюд")
		}
	case "list":
		dishes := forge.Dishes
		if dishType != "" {
			dishes = filterByType(dishes, dishType)
		}
		if cuisine != "" {
			dishes = filterByCuisine(dishes, cuisine)
		}
		for _, d := range dishes {
			fmt.Printf("%s (%s, %s, %d мин)\n", d.Name, d.Type, d.Cuisine, d.Time)
		}
	case "favorites":
		if name != "" {
			if forge.addFavorite(name) {
				fmt.Printf("✅ '%s' добавлен в избранное\n", name)
			} else {
				fmt.Printf("⚠️ '%s' уже в избранном или не существует\n", name)
			}
		} else {
			favs := forge.getFavorites()
			if len(favs) > 0 {
				fmt.Println("⭐ Избранное:")
				for _, d := range favs {
					fmt.Printf("  %s (%s, %s)\n", d.Name, d.Type, d.Cuisine)
				}
			} else {
				fmt.Println("Избранное пусто")
			}
		}
	default:
		interactiveMode(forge)
	}
}

func interactiveMode(f *Forge) {
	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Println("\n🍳 DishForge - Генератор блюд (интерактивный)")
		fmt.Println("1. Сгенерировать случайное блюдо")
		fmt.Println("2. Сгенерировать меню")
		fmt.Println("3. Список всех блюд")
		fmt.Println("4. Избранное")
		fmt.Println("0. Выход")
		fmt.Print("Выберите действие: ")
		scanner.Scan()
		choice := scanner.Text()
		switch choice {
		case "0":
			return
		case "1":
			fmt.Print("Тип (Enter пропустить): ")
			scanner.Scan()
			t := scanner.Text()
			fmt.Print("Кухня (Enter пропустить): ")
			scanner.Scan()
			c := scanner.Text()
			fmt.Print("Макс. время (мин, Enter пропустить): ")
			scanner.Scan()
			timeStr := scanner.Text()
			mt := 0
			if timeStr != "" {
				mt, _ = strconv.Atoi(timeStr)
			}
			fmt.Print("Сложность (easy/medium/hard, Enter пропустить): ")
			scanner.Scan()
			diff := scanner.Text()
			dish := f.generate(t, c, diff, mt)
			if dish != nil {
				fmt.Println(formatDish(*dish))
			} else {
				fmt.Println("❌ Блюда не найдены")
			}
		case "2":
			fmt.Print("Количество блюд (по умолчанию 3): ")
			scanner.Scan()
			cntStr := scanner.Text()
			cnt := 3
			if cntStr != "" {
				cnt, _ = strconv.Atoi(cntStr)
			}
			fmt.Print("Тип (Enter пропустить): ")
			scanner.Scan()
			t := scanner.Text()
			fmt.Print("Кухня (Enter пропустить): ")
			scanner.Scan()
			c := scanner.Text()
			fmt.Print("Макс. время (мин, Enter пропустить): ")
			scanner.Scan()
			timeStr := scanner.Text()
			mt := 0
			if timeStr != "" {
				mt, _ = strconv.Atoi(timeStr)
			}
			fmt.Print("Сложность (Enter пропустить): ")
			scanner.Scan()
			diff := scanner.Text()
			dishes := f.generateMenu(cnt, t, c, diff, mt)
			if len(dishes) > 0 {
				fmt.Printf("🍽️ Меню из %d блюд:\n", len(dishes))
				for i, d := range dishes {
					fmt.Printf("\n%d. %s (%s, %s, %d мин, %s)\n", i+1, d.Name, d.Type, d.Cuisine, d.Time, d.Difficulty)
					fmt.Printf("   %s\n", d.Description)
				}
			} else {
				fmt.Println("❌ Недостаточно блюд")
			}
		case "3":
			fmt.Print("Тип (Enter пропустить): ")
			scanner.Scan()
			t := scanner.Text()
			fmt.Print("Кухня (Enter пропустить): ")
			scanner.Scan()
			c := scanner.Text()
			dishes := f.Dishes
			if t != "" {
				dishes = filterByType(dishes, t)
			}
			if c != "" {
				dishes = filterByCuisine(dishes, c)
			}
			for _, d := range dishes {
				fmt.Printf("  %s (%s, %s, %d мин)\n", d.Name, d.Type, d.Cuisine, d.Time)
			}
		case "4":
			favs := f.getFavorites()
			fmt.Println("⭐ Избранное:")
			if len(favs) > 0 {
				for _, d := range favs {
					fmt.Printf("  %s (%s, %s)\n", d.Name, d.Type, d.Cuisine)
				}
			} else {
				fmt.Println("  Пусто")
			}
			fmt.Println("\n1. Добавить в избранное")
			fmt.Println("2. Удалить из избранного")
			fmt.Println("3. Назад")
			fmt.Print("Выберите: ")
			scanner.Scan()
			sub := scanner.Text()
			if sub == "1" {
				fmt.Print("Название блюда: ")
				scanner.Scan()
				name := scanner.Text()
				if f.addFavorite(name) {
					fmt.Printf("✅ '%s' добавлен\n", name)
				} else {
					fmt.Printf("⚠️ '%s' уже в избранном или не существует\n", name)
				}
			} else if sub == "2" {
				fmt.Print("Название блюда: ")
				scanner.Scan()
				name := scanner.Text()
				if f.removeFavorite(name) {
					fmt.Printf("✅ '%s' удалён\n", name)
				} else {
					fmt.Printf("❌ '%s' не найден\n", name)
				}
			}
		default:
			fmt.Println("Неверный выбор")
		}
	}
}
