"""Лабораторная работа № 6. Вариант 19. Ситникова Ольга, группа БИ2-1."""
import platform  # сведения о компьютере
import statistics  # медиана времени
import sys  # sys.getsizeof для оценки памяти
import time  # замер времени
import matplotlib.pyplot as plt  # графики

SIZES = [1000, 5000, 10_000]  # размеры n по варианту 19


class Node:  # узел односвязного списка
    __slots__ = ("value", "next")  # фиксированный набор полей: узел занимает меньше памяти

    def __init__(self, value, nxt=None):  # значение и ссылка на следующий узел
        self.value, self.next = value, nxt  # сохраняем значение и ссылку


class LinkedList:  # односвязный список со ссылкой на хвост
    def __init__(self):  # создание пустого списка
        self.head, self.tail, self.size = None, None, 0  # начало, конец и число элементов

    def nodes(self):  # генератор узлов; ограничен size, поэтому работает и для кольцевого списка
        node = self.head  # начинаем с первого узла
        for _ in range(self.size):  # ровно size шагов
            yield node  # отдаём текущий узел
            node = node.next  # переходим к следующему

    def push_front(self, value):  # вставка в начало, Θ(1)
        self.head = Node(value, self.head)  # новый узел становится головой
        if self.tail is None:  # список был пуст
            self.tail = self.head  # единственный узел одновременно и хвост
        self.size += 1  # увеличиваем число элементов

    def push_back(self, value):  # вставка в конец, Θ(1) благодаря ссылке tail
        node = Node(value)  # создаём новый узел
        if self.tail is None:  # список пуст
            self.head = self.tail = node  # узел и голова, и хвост
        else:  # список не пуст
            self.tail.next = node  # старый хвост ссылается на новый узел
            self.tail = node  # новый узел становится хвостом
        self.size += 1  # увеличиваем число элементов

    def _node(self, index):  # узел по индексу, Θ(index)
        if not 0 <= index < self.size:  # проверка границ
            raise IndexError("Индекс вне диапазона")  # сообщаем об ошибке
        node = self.head  # идём от головы
        for _ in range(index):  # index переходов по ссылкам
            node = node.next  # к следующему узлу
        return node  # найденный узел

    def insert(self, index, value):  # вставка по индексу, Θ(n)
        if not 0 <= index <= self.size:  # допустим и индекс size (вставка в конец)
            raise IndexError("Индекс вне диапазона")  # сообщаем об ошибке
        if index == 0:  # вставка в начало
            return self.push_front(value)  # используем готовый метод
        if index == self.size:  # вставка в конец
            return self.push_back(value)  # используем готовый метод
        prev = self._node(index - 1)  # узел перед позицией вставки
        prev.next = Node(value, prev.next)  # переставляем ссылки
        self.size += 1  # увеличиваем число элементов

    def pop_front(self):  # удаление из начала, Θ(1)
        if self.head is None:  # список пуст
            raise IndexError("Список пуст")  # сообщаем об ошибке
        value = self.head.value  # запоминаем значение головы
        self.head = self.head.next  # сдвигаем голову
        if self.head is None:  # список опустел
            self.tail = None  # хвоста больше нет
        self.size -= 1  # уменьшаем число элементов
        return value  # возвращаем удалённое значение

    def get(self, index):  # доступ по индексу, Θ(n)
        return self._node(index).value  # значение найденного узла

    def find(self, value):  # поиск значения, Θ(n)
        for i, node in enumerate(self.nodes()):  # перебираем узлы с номерами
            if node.value == value:  # нашли значение
                return i  # возвращаем индекс
        return -1  # значения нет

    def to_list(self):  # содержимое в виде обычного списка
        return [node.value for node in self.nodes()]  # значения всех узлов по порядку

    def __len__(self):  # число элементов
        return self.size  # хранится в поле size


class CircularList(LinkedList):  # кольцевой односвязный список: хвост ссылается на голову
    def push_front(self, value):  # вставка в начало
        super().push_front(value)  # обычная вставка
        self.tail.next = self.head  # замыкаем кольцо на новую голову

    def push_back(self, value):  # вставка в конец
        super().push_back(value)  # обычная вставка
        self.tail.next = self.head  # замыкаем кольцо

    def pop_front(self):  # удаление из начала
        if self.tail:  # список не пуст
            self.tail.next = None  # временно разрываем кольцо
        value = super().pop_front()  # обычное удаление
        if self.tail:  # остались элементы
            self.tail.next = self.head  # снова замыкаем кольцо
        return value  # возвращаем удалённое значение


def build(n, cycle_to=None):  # односвязный список из n узлов; хвост можно замкнуть на узел cycle_to
    lst = LinkedList()  # пустой список
    for i in range(n):  # добавляем значения 0..n-1
        lst.push_back(i)  # вставка в конец
    if cycle_to is not None:  # нужен цикл
        lst.tail.next = lst._node(cycle_to)  # хвост ссылается на узел cycle_to
    return lst  # готовый список


def build_array(n, cycle_to=None):  # то же на встроенном list: nxt[i] — индекс следующего узла
    return list(range(1, n)) + [-1 if cycle_to is None else cycle_to]  # последний элемент: конец (-1) или цикл


def has_cycle_floyd(head):  # алгоритм Флойда («черепаха и заяц»): время Θ(n), память O(1)
    slow = fast = head  # оба указателя в начале
    while fast is not None and fast.next is not None:  # пока заяц не дошёл до конца
        slow, fast = slow.next, fast.next.next  # черепаха на 1 шаг, заяц на 2
        if slow is fast:  # указатели встретились
            return True  # цикл есть
    return False  # дошли до конца, цикла нет


def has_cycle_array(nxt):  # алгоритм Флойда для массива ссылок на встроенном list
    slow = fast = 0  # индексы указателей
    while fast != -1 and nxt[fast] != -1:  # пока заяц не дошёл до конца
        slow, fast = nxt[slow], nxt[nxt[fast]]  # черепаха на 1 шаг, заяц на 2
        if slow == fast:  # указатели встретились
            return True  # цикл есть
    return False  # цикла нет


def has_cycle_set(head):  # метод множества посещённых узлов: время Θ(n), память Θ(n)
    seen, node = set(), head  # посещённые узлы и текущий узел
    while node is not None:  # пока не конец списка
        if node in seen:  # узел встречается повторно
            return True  # цикл есть
        seen.add(node)  # запоминаем узел
        node = node.next  # переходим дальше
    return False  # цикла нет


def diagnose(head):  # диагностика структуры: (есть ли цикл, индекс входа в цикл, длина цикла)
    slow = fast = head  # оба указателя в начале
    while fast is not None and fast.next is not None:  # фаза 1: поиск встречи
        slow, fast = slow.next, fast.next.next  # черепаха на 1 шаг, заяц на 2
        if slow is fast:  # встретились внутри цикла
            slow, start = head, 0  # фаза 2: черепаха возвращается в начало
            while slow is not fast:  # оба идут по одному шагу до встречи
                slow, fast, start = slow.next, fast.next, start + 1  # встреча происходит во входе в цикл
            length, node = 1, fast.next  # считаем длину цикла
            while node is not fast:  # обходим цикл до возвращения
                node, length = node.next, length + 1  # следующий узел цикла
            return True, start, length  # цикл есть: вход и длина
    return False, -1, 0  # цикла нет


def measure(action, repeats=21):  # медианное время выполнения action(), мс
    times = []  # результаты повторов
    for _ in range(repeats):  # несколько повторов
        t0 = time.perf_counter()  # начало замера
        action()  # исследуемая операция
        times.append(time.perf_counter() - t0)  # длительность повтора
    return statistics.median(times) * 1000  # медиана в миллисекундах


def demo(lst, steps):  # Т1: выполнить операции и вывести содержимое после каждой
    for name, *args in steps:  # имя метода и его аргументы
        res = getattr(lst, name)(*args)  # вызываем метод по имени
        print(f"  {name}({', '.join(map(str, args))}) -> {lst.to_list()}, длина {len(lst)}" + ("" if res is None else f", вернул {res}"))  # вывод


if __name__ == "__main__":  # запуск только при прямом старте файла
    print(platform.platform(), "|", platform.processor() or platform.machine(), "| Python", platform.python_version())  # система
    print("\nТ1. Односвязный список:")  # заголовок проверки
    lst = LinkedList()  # пустой список
    demo(lst, [("push_back", 10), ("push_back", 25), ("push_back", 7), ("push_front", 99), ("insert", 2, 50), ("pop_front",), ("get", 2), ("find", 25), ("find", 1000)])  # операции
    print("Т1. Кольцевой список:")  # заголовок проверки
    circ = CircularList()  # пустой кольцевой список
    demo(circ, [("push_back", 1), ("push_back", 2), ("push_back", 3), ("push_front", 0), ("pop_front",)])  # операции
    print("  хвост ссылается на голову:", circ.tail.next is circ.head)  # проверка замыкания
    print("\nДиагностика (есть цикл, вход, длина цикла):")  # заголовок диагностики
    for desc, head in (("без цикла", build(8).head), ("цикл с узла 3", build(8, 3).head), ("кольцевой список", circ.head)):  # примеры
        print(f"  {desc:<18}{diagnose(head)}")  # результат диагностики
    res = {}  # время по (n, есть цикл): [Флойд на узлах, Флойд на list, множество]
    print("\n   n  цикл | Флойд (узлы) | Флойд (list) | множество  (мс)")  # заголовок таблицы
    for n in SIZES:  # перебираем размеры
        for cyc in (False, True):  # без цикла и с циклом (хвост ссылается на середину)
            ll, arr = build(n, n // 2 if cyc else None), build_array(n, n // 2 if cyc else None)  # одна и та же структура двумя способами
            assert has_cycle_floyd(ll.head) == has_cycle_set(ll.head) == has_cycle_array(arr) == cyc  # проверка правильности
            res[n, cyc] = [measure(lambda: has_cycle_floyd(ll.head)), measure(lambda: has_cycle_array(arr)), measure(lambda: has_cycle_set(ll.head))]  # замеры
            print(f"{n:>6}  {'да ' if cyc else 'нет'}  | " + " | ".join(f"{t:>12.4f}" for t in res[n, cyc]))  # строка таблицы
    print("\nДиагностика на n = 10000, хвост -> узел 5000:", diagnose(build(10_000, 5000).head))  # прикладная задача
    n = 10_000  # размер для оценки памяти (Т4)
    py, ll = list(range(n)), build(n)  # встроенный list и связный список из 10 000 элементов
    size_py = sys.getsizeof(py) + sum(map(sys.getsizeof, py))  # контейнер плюс объекты-числа
    size_ll = sys.getsizeof(ll) + sum(sys.getsizeof(x) + sys.getsizeof(x.value) for x in ll.nodes())  # объект списка, узлы и числа
    size_set = sys.getsizeof(set(ll.nodes()))  # множество узлов (доп. память метода множества)
    print(f"\nПамять, байт: list {size_py}, связный список {size_ll}, узел {sys.getsizeof(ll.head)}, множество посещённых {size_set}")  # вывод
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))  # два графика: без цикла и с циклом
    for ax, cyc in zip(axes, (False, True)):  # по одному графику на случай
        for j, name in enumerate(("Флойд (узлы)", "Флойд (list)", "Множество (узлы)")):  # три метода
            ax.plot(SIZES, [res[s, cyc][j] for s in SIZES], "o-", label=name)  # время от n
        ax.plot(SIZES, [res[SIZES[0], cyc][0] * s / SIZES[0] for s in SIZES], "k--", label="Θ(n) по первой точке")  # теоретическая прямая
        ax.set(xlabel="n", ylabel="Время, мс", title="С циклом" if cyc else "Без цикла")  # оформление
        ax.grid(True, alpha=0.3)  # сетка
        ax.legend()  # легенда
    plt.tight_layout()  # убираем наложение подписей
    plt.savefig("lab6_graphs.png", dpi=150)  # сохраняем график для отчёта
    plt.show()  # показываем график на экране
