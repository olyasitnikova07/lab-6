"""Лабораторная работа № 6. Вариант 19. Ситникова Ольга, БИ 2-1.
Односвязный и кольцевой список, поиск цикла, диагностика ссылочной структуры."""
import sys  # sys.getsizeof нужен для оценки памяти (Т4)
import time  # time.perf_counter нужен для измерения времени (Т2)


class Node:  # узел односвязного списка
    __slots__ = ("value", "next")  # фиксируем поля узла: он занимает меньше памяти

    def __init__(self, value, nxt=None):  # конструктор узла
        self.value = value  # сохраняем значение
        self.next = nxt  # сохраняем ссылку на следующий узел (или None)


class LinkedList:  # односвязный список со ссылкой на хвост
    def __init__(self):  # создаём пустой список
        self.head = None  # голова: первого узла пока нет
        self.tail = None  # хвост: последнего узла пока нет
        self.size = 0  # число элементов

    def push_front(self, value):  # вставка в начало, Θ(1)
        self.head = Node(value, self.head)  # новый узел ссылается на старую голову и сам становится головой
        if self.tail is None:  # если список был пустой
            self.tail = self.head  # то новый узел ещё и хвост
        self.size += 1  # увеличиваем счётчик

    def push_back(self, value):  # вставка в конец, Θ(1) благодаря tail
        node = Node(value)  # создаём новый узел
        if self.tail is None:  # если список пустой
            self.head = self.tail = node  # узел — и голова, и хвост
        else:  # иначе
            self.tail.next = node  # старый хвост ссылается на новый узел
            self.tail = node  # новый узел становится хвостом
        self.size += 1  # увеличиваем счётчик

    def _node(self, index):  # узел с номером index, Θ(n)
        node = self.head  # начинаем с головы
        for _ in range(index):  # index раз
            node = node.next  # переходим к следующему узлу
        return node  # возвращаем найденный узел

    def insert(self, index, value):  # вставка по индексу
        if index <= 0:  # позиция в начале
            self.push_front(value)  # вставляем в начало
        elif index >= self.size:  # позиция за концом
            self.push_back(value)  # вставляем в конец
        else:  # вставка в середину
            prev = self._node(index - 1)  # находим узел перед нужной позицией, Θ(n)
            prev.next = Node(value, prev.next)  # перестановка ссылок, Θ(1)
            self.size += 1  # увеличиваем счётчик

    def pop_front(self):  # удаление из начала, Θ(1)
        if self.head is None:  # если список пуст
            raise IndexError("Список пуст")  # сообщаем об ошибке
        value = self.head.value  # запоминаем значение головы
        self.head = self.head.next  # голова сдвигается на следующий узел
        if self.head is None:  # если список стал пустым
            self.tail = None  # хвоста тоже нет
        self.size -= 1  # уменьшаем счётчик
        return value  # возвращаем удалённое значение

    def get(self, index):  # доступ по индексу, Θ(n)
        if not 0 <= index < self.size:  # проверяем границы
            raise IndexError("Индекс вне диапазона")  # сообщаем об ошибке
        return self._node(index).value  # идём от головы и берём значение

    def find(self, value):  # поиск значения, Θ(n); результат — индекс или -1
        node = self.head  # начинаем с головы
        for i in range(self.size):  # ровно size шагов: не зациклимся даже на кольце
            if node.value == value:  # нашли значение
                return i  # возвращаем индекс
            node = node.next  # идём дальше
        return -1  # значения в списке нет

    def to_list(self):  # содержимое в виде обычного list (для вывода)
        result, node = [], self.head  # пустой результат и текущий узел
        for _ in range(self.size):  # ровно size шагов (безопасно для кольца)
            result.append(node.value)  # добавляем значение узла
            node = node.next  # идём дальше
        return result  # возвращаем значения

    def __len__(self):  # len(список)
        return self.size  # длина — это счётчик


class CircularList(LinkedList):  # кольцевой список: хвост всегда ссылается на голову
    def push_front(self, value):  # вставка в начало
        super().push_front(value)  # обычная вставка
        self.tail.next = self.head  # замыкаем кольцо на новую голову

    def push_back(self, value):  # вставка в конец
        super().push_back(value)  # обычная вставка
        self.tail.next = self.head  # замыкаем кольцо

    def pop_front(self):  # удаление из начала
        if self.tail:  # если список не пуст
            self.tail.next = None  # временно размыкаем кольцо
        value = super().pop_front()  # обычное удаление
        if self.tail:  # если что-то осталось
            self.tail.next = self.head  # замыкаем кольцо снова
        return value  # возвращаем удалённое значение


def make_cycle(lst, k):  # замыкает хвост на узел k: получается цикл (в форме «ρ»)
    lst.tail.next = lst._node(k)  # хвост теперь ссылается на k-й узел


def find_cycle(head):  # алгоритм Флойда: (индекс начала цикла, длина цикла) или None
    slow = fast = head  # оба указателя стартуют с головы
    while fast and fast.next:  # пока «быстрый» не дошёл до конца
        slow, fast = slow.next, fast.next.next  # медленный на 1 шаг, быстрый на 2
        if slow is fast:  # указатели встретились, значит цикл есть
            length, node = 1, slow.next  # считаем длину цикла: один круг от точки встречи
            while node is not slow:  # пока не вернулись в точку встречи
                node, length = node.next, length + 1  # шаг вперёд и +1 к длине
            slow, start = head, 0  # медленный возвращается в голову
            while slow is not fast:  # двигаем оба по 1 шагу до встречи
                slow, fast, start = slow.next, fast.next, start + 1  # они встретятся в начале цикла
            return start, length  # индекс входа в цикл и длина цикла
    return None  # быстрый дошёл до None: цикла нет


def has_cycle_set(head):  # второй способ: запоминаем посещённые узлы, Θ(n) времени и памяти
    seen, node = set(), head  # множество посещённых и текущий узел
    while node:  # пока не конец списка
        if node in seen:  # узел уже встречался
            return True  # значит цикл
        seen.add(node)  # запоминаем узел
        node = node.next  # идём дальше
    return False  # дошли до None: цикла нет


def has_cycle_array(nxt):  # то же на встроенном list: nxt[i] — номер следующего узла (-1 — конец)
    slow = fast = 0  # оба указателя в начале
    while fast != -1 and nxt[fast] != -1:  # пока быстрый не дошёл до конца
        slow, fast = nxt[slow], nxt[nxt[fast]]  # медленный на 1 шаг, быстрый на 2
        if slow == fast:  # встретились
            return True  # цикл есть
    return False  # цикла нет


def build(n, k=None):  # список из n узлов; если задано k — хвост замкнут на узел k
    lst = LinkedList()  # пустой список
    for i in range(n):  # n раз
        lst.push_back(i)  # добавляем значение в конец
    if k is not None:  # нужен цикл
        make_cycle(lst, k)  # замыкаем хвост на k-й узел
    return lst  # возвращаем список


def build_array(n, k=None):  # то же на встроенном list
    nxt = list(range(1, n + 1))  # у i-го узла следующий — (i+1)-й
    nxt[-1] = -1 if k is None else k  # последний: конец (-1) или возврат на узел k
    return nxt  # возвращаем массив ссылок


def measure(action, repeats=15):  # медианное время выполнения action(), с
    times = []  # сюда складываем замеры
    for _ in range(repeats):  # повторяем несколько раз
        start = time.perf_counter()  # запоминаем время начала
        action()  # выполняем измеряемое действие
        times.append(time.perf_counter() - start)  # сохраняем затраченное время
    return sorted(times)[repeats // 2]  # медиана сглаживает случайные выбросы


def diagnose(title, lst):  # диагностика ссылочной структуры (прикладная задача)
    res = find_cycle(lst.head)  # запускаем алгоритм Флойда
    if res is None:  # цикла нет
        text = "цикла нет, структура линейная"  # итог для линейного списка
    else:  # цикл найден
        start, length = res  # распаковываем результат
        text = f"ЦИКЛ: вход в узле {start}, длина цикла {length}, узлов достижимо {start + length}"  # итог
    print(f"  {title:<28} size={lst.size:<3} -> {text}")  # печатаем строку диагностики


if __name__ == "__main__":  # блок запускается только при прямом старте файла
    # ---- Т1. Корректность на малом примере: вывод после каждой операции ----
    lst = LinkedList()  # односвязный список
    print("Односвязный список:")  # заголовок
    for v in (10, 25, 7):  # три значения
        lst.push_back(v)  # вставка в конец
        print(f"  push_back({v:>2})   ->", lst.to_list())  # содержимое после операции
    lst.push_front(99)  # вставка в начало
    print("  push_front(99) ->", lst.to_list())  # содержимое
    lst.insert(2, 55)  # вставка в середину (на позицию 2)
    print("  insert(2, 55)  ->", lst.to_list())  # содержимое
    print("  pop_front()    ->", lst.pop_front(), lst.to_list())  # удалённое значение и остаток
    print("  get(2) =", lst.get(2), "| find(7) =", lst.find(7), "| find(1) =", lst.find(1))  # доступ и поиск
    ring = CircularList()  # кольцевой список
    print("Кольцевой список:")  # заголовок
    for v in (1, 2, 3, 4):  # четыре значения
        ring.push_back(v)  # вставка в конец
    ring.push_front(0)  # вставка в начало
    print("  содержимое:", ring.to_list(), "| tail.next.value =", ring.tail.next.value)  # хвост указывает на голову
    ring.pop_front()  # удаление из начала
    print("  pop_front() ->", ring.to_list(), "| tail.next.value =", ring.tail.next.value)  # кольцо сохранилось

    # ---- Прикладная задача: диагностика ссылочной структуры ----
    print("\nДиагностика ссылочной структуры:")  # заголовок
    diagnose("пустой список", LinkedList())  # случай без узлов
    diagnose("линейный список", build(10))  # цикла нет
    diagnose("цикл: хвост -> узел 4", build(10, 4))  # цикл в середине
    diagnose("самопетля: хвост -> хвост", build(10, 9))  # цикл из одного узла
    diagnose("кольцевой список", ring)  # кольцо, цикл с самой головы
    big = CircularList()  # кольцо побольше
    for v in range(10):  # десять значений
        big.push_back(v)  # вставка в конец
    diagnose("кольцевой список (10)", big)  # цикл длиной 10

    # ---- Т2. Измерение времени ----
    SIZES = [1000, 5000, 10000]  # размеры n по варианту
    NAMES = ["Флойд, без цикла", "Флойд, с циклом", "set, с циклом", "list: Флойд, с циклом"]  # столбцы
    rows = []  # сюда складываем строки результатов
    for n in SIZES:  # для каждого размера
        plain, cyc = build(n), build(n, n // 2)  # список без цикла и с циклом
        arr = build_array(n, n // 2)  # то же с циклом на встроенном list
        rows.append([  # строка таблицы: время четырёх способов
            measure(lambda: find_cycle(plain.head)),  # Флойд на списке без цикла
            measure(lambda: find_cycle(cyc.head)),  # Флойд на списке с циклом
            measure(lambda: has_cycle_set(cyc.head)),  # способ с множеством
            measure(lambda: has_cycle_array(arr)),  # Флойд на встроенном list
        ])  # конец строки
    print("\nВремя поиска цикла, мс:")  # заголовок таблицы
    print(f"{'n':>6}" + "".join(f"{s:>24}" for s in NAMES))  # шапка таблицы
    for n, row in zip(SIZES, rows):  # печатаем строки
        print(f"{n:>6}" + "".join(f"{t * 1000:>24.4f}" for t in row))  # время в миллисекундах

    # ---- Т3. Какая оценка соответствует кривой ----
    print(f"\nРост времени при росте n в {SIZES[-1] // SIZES[0]} раз:")  # заголовок
    for j, name in enumerate(NAMES):  # по каждому столбцу
        growth = rows[-1][j] / rows[0][j]  # во сколько раз выросло время
        print(f"  {name:<24} x{growth:5.1f} -> {'Θ(n)' if growth > 3 else 'Θ(1)'}")  # ~10 раз → Θ(n), ~1 → Θ(1)
    try:  # matplotlib может быть не установлен
        import matplotlib.pyplot as plt  # библиотека графиков
        for j, name in enumerate(NAMES):  # по каждому столбцу
            plt.plot(SIZES, [r[j] * 1000 for r in rows], marker="o", label=name)  # кривая T(n)
        plt.xlabel("n, число узлов")  # подпись оси X
        plt.ylabel("T, мс")  # подпись оси Y
        plt.title("Поиск цикла: зависимость T(n)")  # заголовок графика
        plt.legend()  # легенда
        plt.grid(True)  # сетка
        plt.savefig("lab6_graph.png", dpi=150)  # сохраняем график в файл
        plt.show()  # показываем окно с графиком
    except ImportError:  # если библиотеки нет
        print("Для графика выполните: pip install matplotlib")  # подсказка

    # ---- Т4. Расход памяти на 10 000 элементов ----
    m = build(10000)  # список из 10 000 узлов
    node, nodes_bytes = m.head, 0  # текущий узел и счётчик байт узлов
    for _ in range(m.size):  # обходим все узлы
        nodes_bytes += sys.getsizeof(node)  # прибавляем размер узла
        node = node.next  # идём дальше
    ll_bytes = sys.getsizeof(m) + nodes_bytes  # объект списка плюс все узлы
    py_bytes = sys.getsizeof(list(range(10000)))  # встроенный list (массив ссылок)
    print(f"\nПамять на 10 000 элементов (без самих чисел): список {ll_bytes} Б, list {py_bytes} Б,"
          f" разница в {ll_bytes / py_bytes:.1f} раза")  # итог сравнения
