// DishForge.java - Генератор случайных блюд на Java (CLI + Swing GUI)
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.List;
import java.util.stream.Collectors;

public class DishForge {
    private static final String DATA_FILE = "dishes.json";
    private static final String FAV_FILE = "favorites.json";

    static class Dish {
        String name; String type; String cuisine; int time; String difficulty;
        String description; List<String> ingredients; List<String> instructions;
        Dish(String name, String type, String cuisine, int time, String difficulty,
             String description, List<String> ingredients, List<String> instructions) {
            this.name = name; this.type = type; this.cuisine = cuisine; this.time = time;
            this.difficulty = difficulty; this.description = description;
            this.ingredients = ingredients; this.instructions = instructions;
        }
    }

    static class Forge {
        List<Dish> dishes = new ArrayList<>();
        List<String> favorites = new ArrayList<>();

        void load() {
            try {
                String json = new String(Files.readAllBytes(Paths.get(DATA_FILE)));
                // Упрощённо: для реального проекта использовать Jackson
                // В этой версии оставляем заглушку и загружаем дефолтные
            } catch (Exception e) {}
            if (dishes.isEmpty()) {
                dishes = defaultDishes();
                save();
            }
            try {
                String json = new String(Files.readAllBytes(Paths.get(FAV_FILE)));
                // парсинг вручную
            } catch (Exception e) {}
        }

        void save() {
            try (PrintWriter pw = new PrintWriter(DATA_FILE)) {
                pw.println("[");
                for (int i = 0; i < dishes.size(); i++) {
                    Dish d = dishes.get(i);
                    pw.printf("  {\"name\":\"%s\",\"type\":\"%s\",\"cuisine\":\"%s\",\"time\":%d,\"difficulty\":\"%s\",\"description\":\"%s\",\"ingredients\":[",
                            d.name, d.type, d.cuisine, d.time, d.difficulty, d.description);
                    for (int j = 0; j < d.ingredients.size(); j++) {
                        pw.printf("\"%s\"%s", d.ingredients.get(j), (j < d.ingredients.size()-1 ? "," : ""));
                    }
                    pw.print("],\"instructions\":[");
                    for (int j = 0; j < d.instructions.size(); j++) {
                        pw.printf("\"%s\"%s", d.instructions.get(j), (j < d.instructions.size()-1 ? "," : ""));
                    }
                    pw.printf("]}%s\n", (i < dishes.size()-1 ? "," : ""));
                }
                pw.println("]");
            } catch (IOException e) {}
            try (PrintWriter pw = new PrintWriter(FAV_FILE)) {
                pw.println("[");
                for (int i = 0; i < favorites.size(); i++) {
                    pw.printf("  \"%s\"%s\n", favorites.get(i), (i < favorites.size()-1 ? "," : ""));
                }
                pw.println("]");
            } catch (IOException e) {}
        }

        List<Dish> defaultDishes() {
            List<Dish> list = new ArrayList<>();
            list.add(new Dish("Овсянка с ягодами", "breakfast", "russian", 10, "easy",
                    "Полезный завтрак из овсяных хлопьев с ягодами и мёдом.",
                    Arrays.asList("Овсяные хлопья 100г", "Молоко 200мл", "Ягоды 50г", "Мёд 1 ст.л."),
                    Arrays.asList("Вскипятить молоко", "Добавить хлопья, варить 5 мин", "Добавить ягоды и мёд")));
            list.add(new Dish("Паста Карбонара", "lunch", "italian", 25, "medium",
                    "Классическая итальянская паста с беконом и пармезаном.",
                    Arrays.asList("Паста 200г", "Бекон 100г", "Яйца 2 шт", "Пармезан 50г", "Сливки 100мл"),
                    Arrays.asList("Отварить пасту", "Обжарить бекон", "Смешать яйца, сыр и сливки", "Соединить с пастой")));
            return list;
        }

        Dish generate(String type, String cuisine, Integer maxTime, String difficulty) {
            List<Dish> filtered = new ArrayList<>(dishes);
            if (type != null) filtered = filtered.stream().filter(d -> d.type.equals(type)).collect(Collectors.toList());
            if (cuisine != null) filtered = filtered.stream().filter(d -> d.cuisine.equals(cuisine)).collect(Collectors.toList());
            if (maxTime != null) filtered = filtered.stream().filter(d -> d.time <= maxTime).collect(Collectors.toList());
            if (difficulty != null) filtered = filtered.stream().filter(d -> d.difficulty.equals(difficulty)).collect(Collectors.toList());
            if (filtered.isEmpty()) return null;
            return filtered.get(new Random().nextInt(filtered.size()));
        }

        List<Dish> generateMenu(int count, String type, String cuisine, Integer maxTime, String difficulty) {
            List<Dish> available = new ArrayList<>(dishes);
            if (type != null) available = available.stream().filter(d -> d.type.equals(type)).collect(Collectors.toList());
            if (cuisine != null) available = available.stream().filter(d -> d.cuisine.equals(cuisine)).collect(Collectors.toList());
            if (maxTime != null) available = available.stream().filter(d -> d.time <= maxTime).collect(Collectors.toList());
            if (difficulty != null) available = available.stream().filter(d -> d.difficulty.equals(difficulty)).collect(Collectors.toList());
            if (available.size() < count) count = available.size();
            Collections.shuffle(available);
            return available.subList(0, count);
        }

        boolean addFavorite(String name) {
            if (favorites.contains(name)) return false;
            favorites.add(name);
            save();
            return true;
        }

        boolean removeFavorite(String name) {
            if (favorites.remove(name)) { save(); return true; }
            return false;
        }

        List<Dish> getFavorites() {
            return dishes.stream().filter(d -> favorites.contains(d.name)).collect(Collectors.toList());
        }

        String formatDish(Dish d) {
            StringBuilder sb = new StringBuilder();
            sb.append("🍽️ ").append(d.name).append("\n");
            sb.append("  Тип: ").append(d.type).append("\n");
            sb.append("  Кухня: ").append(d.cuisine).append("\n");
            sb.append("  Время: ").append(d.time).append(" мин\n");
            sb.append("  Сложность: ").append(d.difficulty).append("\n");
            sb.append("  Описание: ").append(d.description).append("\n");
            sb.append("  Ингредиенты:\n");
            for (String ing : d.ingredients) sb.append("    - ").append(ing).append("\n");
            sb.append("  Приготовление:\n");
            for (int i = 0; i < d.instructions.size(); i++) sb.append("    ").append(i+1).append(". ").append(d.instructions.get(i)).append("\n");
            return sb.toString();
        }
    }

    // ========== CLI ==========
    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("--gui")) {
            SwingUtilities.invokeLater(() -> new DishForgeGUI().setVisible(true));
            return;
        }
        Forge forge = new Forge();
        forge.load();
        if (args.length == 0) {
            interactiveMode(forge);
            return;
        }
        try {
            String cmd = args[0];
            switch (cmd) {
                case "generate": {
                    String type = null, cuisine = null, difficulty = null;
                    Integer maxTime = null;
                    for (int i = 1; i < args.length; i++) {
                        if (args[i].equals("--type")) type = args[++i];
                        else if (args[i].equals("--cuisine")) cuisine = args[++i];
                        else if (args[i].equals("--time")) maxTime = Integer.parseInt(args[++i]);
                        else if (args[i].equals("--difficulty")) difficulty = args[++i];
                    }
                    Dish d = forge.generate(type, cuisine, maxTime, difficulty);
                    if (d != null) System.out.println(forge.formatDish(d));
                    else System.out.println("❌ Блюда не найдены");
                    break;
                }
                case "menu": {
                    int count = 3; String type = null, cuisine = null, difficulty = null; Integer maxTime = null;
                    for (int i = 1; i < args.length; i++) {
                        if (args[i].equals("--count")) count = Integer.parseInt(args[++i]);
                        else if (args[i].equals("--type")) type = args[++i];
                        else if (args[i].equals("--cuisine")) cuisine = args[++i];
                        else if (args[i].equals("--time")) maxTime = Integer.parseInt(args[++i]);
                        else if (args[i].equals("--difficulty")) difficulty = args[++i];
                    }
                    List<Dish> menu = forge.generateMenu(count, type, cuisine, maxTime, difficulty);
                    if (!menu.isEmpty()) {
                        System.out.printf("🍽️ Меню из %d блюд:\n", menu.size());
                        for (int i = 0; i < menu.size(); i++) {
                            Dish d = menu.get(i);
                            System.out.printf("\n%d. %s (%s, %s, %d мин, %s)\n", i+1, d.name, d.type, d.cuisine, d.time, d.difficulty);
                            System.out.println("   " + d.description);
                        }
                    } else System.out.println("❌ Недостаточно блюд");
                    break;
                }
                case "list": {
                    String type = null, cuisine = null;
                    for (int i = 1; i < args.length; i++) {
                        if (args[i].equals("--type")) type = args[++i];
                        else if (args[i].equals("--cuisine")) cuisine = args[++i];
                    }
                    List<Dish> dishes = forge.dishes;
                    if (type != null) dishes = dishes.stream().filter(d -> d.type.equals(type)).collect(Collectors.toList());
                    if (cuisine != null) dishes = dishes.stream().filter(d -> d.cuisine.equals(cuisine)).collect(Collectors.toList());
                    for (Dish d : dishes) System.out.printf("%s (%s, %s, %d мин)\n", d.name, d.type, d.cuisine, d.time);
                    break;
                }
                case "favorites": {
                    if (args.length > 2 && args[2].equals("add") && args.length > 3) {
                        String name = args[3];
                        if (forge.addFavorite(name)) System.out.printf("✅ '%s' добавлен в избранное\n", name);
                        else System.out.printf("⚠️ '%s' уже в избранном или не существует\n", name);
                    } else if (args.length > 2 && args[2].equals("remove") && args.length > 3) {
                        String name = args[3];
                        if (forge.removeFavorite(name)) System.out.printf("✅ '%s' удалён из избранного\n", name);
                        else System.out.printf("❌ '%s' не найден в избранном\n", name);
                    } else {
                        List<Dish> favs = forge.getFavorites();
                        if (!favs.isEmpty()) {
                            System.out.println("⭐ Избранное:");
                            for (Dish d : favs) System.out.printf("  %s (%s, %s)\n", d.name, d.type, d.cuisine);
                        } else System.out.println("Избранное пусто");
                    }
                    break;
                }
                default: interactiveMode(forge);
            }
        } catch (Exception e) { System.err.println("Ошибка: " + e.getMessage()); }
    }

    static void interactiveMode(Forge forge) {
        Scanner sc = new Scanner(System.in);
        while (true) {
            System.out.println("\n🍳 DishForge - Генератор блюд (интерактивный)");
            System.out.println("1. Сгенерировать случайное блюдо");
            System.out.println("2. Сгенерировать меню");
            System.out.println("3. Список всех блюд");
            System.out.println("4. Избранное");
            System.out.println("0. Выход");
            System.out.print("Выберите действие: ");
            String choice = sc.nextLine();
            switch (choice) {
                case "0": return;
                case "1": {
                    System.out.print("Тип (Enter пропустить): ");
                    String t = sc.nextLine(); if (t.isEmpty()) t = null;
                    System.out.print("Кухня (Enter пропустить): ");
                    String c = sc.nextLine(); if (c.isEmpty()) c = null;
                    System.out.print("Макс. время (мин, Enter пропустить): ");
                    String timeStr = sc.nextLine();
                    Integer mt = timeStr.isEmpty() ? null : Integer.parseInt(timeStr);
                    System.out.print("Сложность (easy/medium/hard, Enter пропустить): ");
                    String diff = sc.nextLine(); if (diff.isEmpty()) diff = null;
                    Dish d = forge.generate(t, c, mt, diff);
                    if (d != null) System.out.println(forge.formatDish(d));
                    else System.out.println("❌ Блюда не найдены");
                    break;
                }
                case "2": {
                    System.out.print("Количество блюд (по умолчанию 3): ");
                    String cntStr = sc.nextLine();
                    int count = cntStr.isEmpty() ? 3 : Integer.parseInt(cntStr);
                    System.out.print("Тип (Enter пропустить): ");
                    String t = sc.nextLine(); if (t.isEmpty()) t = null;
                    System.out.print("Кухня (Enter пропустить): ");
                    String c = sc.nextLine(); if (c.isEmpty()) c = null;
                    System.out.print("Макс. время (мин, Enter пропустить): ");
                    String timeStr = sc.nextLine();
                    Integer mt = timeStr.isEmpty() ? null : Integer.parseInt(timeStr);
                    System.out.print("Сложность (Enter пропустить): ");
                    String diff = sc.nextLine(); if (diff.isEmpty()) diff = null;
                    List<Dish> menu = forge.generateMenu(count, t, c, mt, diff);
                    if (!menu.isEmpty()) {
                        System.out.printf("🍽️ Меню из %d блюд:\n", menu.size());
                        for (int i = 0; i < menu.size(); i++) {
                            Dish d = menu.get(i);
                            System.out.printf("\n%d. %s (%s, %s, %d мин, %s)\n", i+1, d.name, d.type, d.cuisine, d.time, d.difficulty);
                            System.out.println("   " + d.description);
                        }
                    } else System.out.println("❌ Недостаточно блюд");
                    break;
                }
                case "3": {
                    System.out.print("Тип (Enter пропустить): ");
                    String t = sc.nextLine(); if (t.isEmpty()) t = null;
                    System.out.print("Кухня (Enter пропустить): ");
                    String c = sc.nextLine(); if (c.isEmpty()) c = null;
                    List<Dish> dishes = forge.dishes;
                    if (t != null) dishes = dishes.stream().filter(d -> d.type.equals(t)).collect(Collectors.toList());
                    if (c != null) dishes = dishes.stream().filter(d -> d.cuisine.equals(c)).collect(Collectors.toList());
                    for (Dish d : dishes) System.out.printf("  %s (%s, %s, %d мин)\n", d.name, d.type, d.cuisine, d.time);
                    break;
                }
                case "4": {
                    List<Dish> favs = forge.getFavorites();
                    System.out.println("⭐ Избранное:");
                    if (!favs.isEmpty()) for (Dish d : favs) System.out.printf("  %s (%s, %s)\n", d.name, d.type, d.cuisine);
                    else System.out.println("  Пусто");
                    System.out.println("\n1. Добавить в избранное");
                    System.out.println("2. Удалить из избранного");
                    System.out.println("3. Назад");
                    System.out.print("Выберите: ");
                    String sub = sc.nextLine();
                    if (sub.equals("1")) {
                        System.out.print("Название блюда: ");
                        String name = sc.nextLine();
                        if (forge.addFavorite(name)) System.out.printf("✅ '%s' добавлен\n", name);
                        else System.out.printf("⚠️ '%s' уже в избранном или не существует\n", name);
                    } else if (sub.equals("2")) {
                        System.out.print("Название блюда: ");
                        String name = sc.nextLine();
                        if (forge.removeFavorite(name)) System.out.printf("✅ '%s' удалён\n", name);
                        else System.out.printf("❌ '%s' не найден\n", name);
                    }
                    break;
                }
                default: System.out.println("Неверный выбор");
            }
        }
    }

    // ========== GUI ==========
    static class DishForgeGUI extends JFrame {
        private Forge forge = new Forge();
        private JComboBox<String> typeBox, cuisineBox, diffBox;
        private JTextField timeField;
        private JTextArea resultArea;
        private Dish currentDish;

        public DishForgeGUI() {
            forge.load();
            setTitle("🍳 DishForge - Генератор блюд");
            setSize(700, 550);
            setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            setLayout(new BorderLayout(5,5));
            JPanel top = new JPanel(new GridBagLayout());
            GridBagConstraints gbc = new GridBagConstraints();
            gbc.insets = new Insets(5,5,5,5);
            gbc.gridx = 0; gbc.gridy = 0; top.add(new JLabel("Тип:"), gbc);
            gbc.gridx = 1; typeBox = new JComboBox<>(new String[]{"", "breakfast", "lunch", "dinner", "dessert", "snack", "drink"}); top.add(typeBox, gbc);
            gbc.gridx = 2; top.add(new JLabel("Кухня:"), gbc);
            gbc.gridx = 3; cuisineBox = new JComboBox<>(new String[]{"", "italian", "japanese", "russian", "mexican", "french", "chinese", "indian"}); top.add(cuisineBox, gbc);
            gbc.gridx = 4; top.add(new JLabel("Макс. время (мин):"), gbc);
            gbc.gridx = 5; timeField = new JTextField(6); top.add(timeField, gbc);
            gbc.gridx = 6; top.add(new JLabel("Сложность:"), gbc);
            gbc.gridx = 7; diffBox = new JComboBox<>(new String[]{"", "easy", "medium", "hard"}); top.add(diffBox, gbc);
            gbc.gridx = 8; JButton genBtn = new JButton("🎲 Сгенерировать"); genBtn.addActionListener(e -> generate()); top.add(genBtn, gbc);
            gbc.gridx = 9; JButton menuBtn = new JButton("🍽️ Меню (3)"); menuBtn.addActionListener(e -> generateMenu(3)); top.add(menuBtn, gbc);
            add(top, BorderLayout.NORTH);

            resultArea = new JTextArea();
            resultArea.setEditable(false);
            add(new JScrollPane(resultArea), BorderLayout.CENTER);

            JPanel bottom = new JPanel(new FlowLayout());
            JButton favBtn = new JButton("⭐ Добавить в избранное");
            favBtn.addActionListener(e -> addFavorite());
            bottom.add(favBtn);
            JButton listFavBtn = new JButton("📋 Избранное");
            listFavBtn.addActionListener(e -> showFavorites());
            bottom.add(listFavBtn);
            add(bottom, BorderLayout.SOUTH);
        }

        void generate() {
            String type = typeBox.getSelectedItem().toString();
            if (type.isEmpty()) type = null;
            String cuisine = cuisineBox.getSelectedItem().toString();
            if (cuisine.isEmpty()) cuisine = null;
            String timeStr = timeField.getText().trim();
            Integer maxTime = timeStr.isEmpty() ? null : Integer.parseInt(timeStr);
            String diff = diffBox.getSelectedItem().toString();
            if (diff.isEmpty()) diff = null;
            Dish d = forge.generate(type, cuisine, maxTime, diff);
            if (d != null) {
                currentDish = d;
                resultArea.setText(forge.formatDish(d));
            } else {
                resultArea.setText("❌ Блюда не найдены по заданным критериям");
                currentDish = null;
            }
        }

        void generateMenu(int count) {
            String type = typeBox.getSelectedItem().toString();
            if (type.isEmpty()) type = null;
            String cuisine = cuisineBox.getSelectedItem().toString();
            if (cuisine.isEmpty()) cuisine = null;
            String timeStr = timeField.getText().trim();
            Integer maxTime = timeStr.isEmpty() ? null : Integer.parseInt(timeStr);
            String diff = diffBox.getSelectedItem().toString();
            if (diff.isEmpty()) diff = null;
            List<Dish> menu = forge.generateMenu(count, type, cuisine, maxTime, diff);
            resultArea.setText("");
            if (!menu.isEmpty()) {
                resultArea.append(String.format("🍽️ Меню из %d блюд:\n\n", menu.size()));
                for (int i = 0; i < menu.size(); i++) {
                    Dish d = menu.get(i);
                    resultArea.append(String.format("%d. %s (%s, %s, %d мин, %s)\n", i+1, d.name, d.type, d.cuisine, d.time, d.difficulty));
                    resultArea.append("   " + d.description + "\n\n");
                }
            } else {
                resultArea.append("❌ Недостаточно блюд");
            }
            currentDish = null;
        }

        void addFavorite() {
            if (currentDish == null) {
                JOptionPane.showMessageDialog(this, "Сначала сгенерируйте блюдо");
                return;
            }
            if (forge.addFavorite(currentDish.name)) {
                JOptionPane.showMessageDialog(this, "Добавлено в избранное");
            } else {
                JOptionPane.showMessageDialog(this, "Уже в избранном");
            }
        }

        void showFavorites() {
            List<Dish> favs = forge.getFavorites();
            if (favs.isEmpty()) {
                JOptionPane.showMessageDialog(this, "Избранное пусто");
                return;
            }
            JDialog dialog = new JDialog(this, "⭐ Избранное", true);
            dialog.setSize(500, 400);
            JTextArea area = new JTextArea();
            area.setEditable(false);
            for (Dish d : favs) {
                area.append("🍽️ " + d.name + "\n");
                area.append("  Тип: " + d.type + ", Кухня: " + d.cuisine + ", Время: " + d.time + " мин, Сложность: " + d.difficulty + "\n\n");
            }
            dialog.add(new JScrollPane(area));
            dialog.setLocationRelativeTo(this);
            dialog.setVisible(true);
        }
    }
}
