<?php
// dish_forge.php - Генератор случайных блюд на PHP (CLI + веб)
// CLI: php dish_forge.php generate --type=breakfast

$dataFile = 'dishes.json';
$favFile = 'favorites.json';

function loadDishes() {
    global $dataFile;
    if (file_exists($dataFile)) {
        $json = file_get_contents($dataFile);
        $data = json_decode($json, true);
        if ($data) return $data;
    }
    return defaultDishes();
}

function defaultDishes() {
    return [
        ['name' => 'Овсянка с ягодами', 'type' => 'breakfast', 'cuisine' => 'russian', 'time' => 10, 'difficulty' => 'easy',
         'description' => 'Полезный завтрак из овсяных хлопьев с ягодами и мёдом.',
         'ingredients' => ['Овсяные хлопья 100г', 'Молоко 200мл', 'Ягоды 50г', 'Мёд 1 ст.л.'],
         'instructions' => ['Вскипятить молоко', 'Добавить хлопья, варить 5 мин', 'Добавить ягоды и мёд']],
        ['name' => 'Паста Карбонара', 'type' => 'lunch', 'cuisine' => 'italian', 'time' => 25, 'difficulty' => 'medium',
         'description' => 'Классическая итальянская паста с беконом и пармезаном.',
         'ingredients' => ['Паста 200г', 'Бекон 100г', 'Яйца 2 шт', 'Пармезан 50г', 'Сливки 100мл'],
         'instructions' => ['Отварить пасту', 'Обжарить бекон', 'Смешать яйца, сыр и сливки', 'Соединить с пастой']],
    ];
}

function saveDishes($dishes) {
    global $dataFile;
    file_put_contents($dataFile, json_encode($dishes, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

function loadFavorites() {
    global $favFile;
    if (file_exists($favFile)) {
        $json = file_get_contents($favFile);
        $data = json_decode($json, true);
        return $data ?: [];
    }
    return [];
}

function saveFavorites($favorites) {
    global $favFile;
    file_put_contents($favFile, json_encode($favorites, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

function generateDish($dishes, $type = null, $cuisine = null, $maxTime = null, $difficulty = null) {
    $filtered = $dishes;
    if ($type) $filtered = array_filter($filtered, fn($d) => $d['type'] == $type);
    if ($cuisine) $filtered = array_filter($filtered, fn($d) => $d['cuisine'] == $cuisine);
    if ($maxTime !== null) $filtered = array_filter($filtered, fn($d) => $d['time'] <= $maxTime);
    if ($difficulty) $filtered = array_filter($filtered, fn($d) => $d['difficulty'] == $difficulty);
    $filtered = array_values($filtered);
    if (empty($filtered)) return null;
    return $filtered[array_rand($filtered)];
}

function generateMenu($dishes, $count = 3, $type = null, $cuisine = null, $maxTime = null, $difficulty = null) {
    $available = $dishes;
    if ($type) $available = array_filter($available, fn($d) => $d['type'] == $type);
    if ($cuisine) $available = array_filter($available, fn($d) => $d['cuisine'] == $cuisine);
    if ($maxTime !== null) $available = array_filter($available, fn($d) => $d['time'] <= $maxTime);
    if ($difficulty) $available = array_filter($available, fn($d) => $d['difficulty'] == $difficulty);
    $available = array_values($available);
    if (count($available) < $count) $count = count($available);
    shuffle($available);
    return array_slice($available, 0, $count);
}

function formatDish($d) {
    $lines = [];
    $lines[] = "🍽️ {$d['name']}";
    $lines[] = "  Тип: {$d['type']}";
    $lines[] = "  Кухня: {$d['cuisine']}";
    $lines[] = "  Время: {$d['time']} мин";
    $lines[] = "  Сложность: {$d['difficulty']}";
    $lines[] = "  Описание: {$d['description']}";
    $lines[] = "  Ингредиенты:";
    foreach ($d['ingredients'] as $ing) $lines[] = "    - $ing";
    $lines[] = "  Приготовление:";
    foreach ($d['instructions'] as $i => $step) $lines[] = "    " . ($i+1) . ". $step";
    return implode("\n", $lines);
}

// ========== CLI ==========
if (php_sapi_name() === 'cli') {
    $options = getopt("", ["cmd:", "type:", "cuisine:", "time:", "difficulty:", "count:", "name:"]);
    $cmd = $options['cmd'] ?? null;
    $dishes = loadDishes();
    $favorites = loadFavorites();

    switch ($cmd) {
        case 'generate':
            $type = $options['type'] ?? null;
            $cuisine = $options['cuisine'] ?? null;
            $maxTime = isset($options['time']) ? (int)$options['time'] : null;
            $difficulty = $options['difficulty'] ?? null;
            $dish = generateDish($dishes, $type, $cuisine, $maxTime, $difficulty);
            if ($dish) echo formatDish($dish) . "\n";
            else echo "❌ Блюда не найдены\n";
            break;
        case 'menu':
            $count = isset($options['count']) ? (int)$options['count'] : 3;
            $type = $options['type'] ?? null;
            $cuisine = $options['cuisine'] ?? null;
            $maxTime = isset($options['time']) ? (int)$options['time'] : null;
            $difficulty = $options['difficulty'] ?? null;
            $menu = generateMenu($dishes, $count, $type, $cuisine, $maxTime, $difficulty);
            if (!empty($menu)) {
                echo "🍽️ Меню из " . count($menu) . " блюд:\n";
                foreach ($menu as $i => $d) {
                    echo "\n" . ($i+1) . ". {$d['name']} ({$d['type']}, {$d['cuisine']}, {$d['time']} мин, {$d['difficulty']})\n";
                    echo "   {$d['description']}\n";
                }
            } else echo "❌ Недостаточно блюд\n";
            break;
        case 'list':
            $type = $options['type'] ?? null;
            $cuisine = $options['cuisine'] ?? null;
            $list = $dishes;
            if ($type) $list = array_filter($list, fn($d) => $d['type'] == $type);
            if ($cuisine) $list = array_filter($list, fn($d) => $d['cuisine'] == $cuisine);
            foreach ($list as $d) echo "{$d['name']} ({$d['type']}, {$d['cuisine']}, {$d['time']} мин)\n";
            break;
        case 'favorites':
            if (isset($options['name']) && isset($options['cmd2']) && $options['cmd2'] == 'add') {
                $name = $options['name'];
                if (!in_array($name, $favorites)) {
                    $favorites[] = $name;
                    saveFavorites($favorites);
                    echo "✅ '$name' добавлен в избранное\n";
                } else {
                    echo "⚠️ '$name' уже в избранном\n";
                }
            } elseif (isset($options['name']) && isset($options['cmd2']) && $options['cmd2'] == 'remove') {
                $name = $options['name'];
                $idx = array_search($name, $favorites);
                if ($idx !== false) {
                    unset($favorites[$idx]);
                    saveFavorites($favorites);
                    echo "✅ '$name' удалён из избранного\n";
                } else {
                    echo "❌ '$name' не найден в избранном\n";
                }
            } else {
                if (!empty($favorites)) {
                    echo "⭐ Избранное:\n";
                    foreach ($favorites as $fav) echo "  $fav\n";
                } else {
                    echo "Избранное пусто\n";
                }
            }
            break;
        default:
            interactiveMode($dishes, $favorites);
            break;
    }
    exit;
}

// ========== ИНТЕРАКТИВНЫЙ РЕЖИМ ==========
function interactiveMode($dishes, &$favorites) {
    while (true) {
        echo "\n🍳 DishForge - Генератор блюд (интерактивный)\n";
        echo "1
