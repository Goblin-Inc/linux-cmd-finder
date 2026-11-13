import re
from difflib import SequenceMatcher
import sys

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    tk = None
    ttk = None


COMMANDS = [
    {
        "name": "touch",
        "description": "Создаёт пустой файл или обновляет время последнего изменения у существующего файла.",
        "keywords": ["создать файл", "новый файл", "пустой файл", "папка", "изменить время", "обновить timestamp", "touch"]
    },
    {
        "name": "mkdir",
        "description": "Создаёт новую директорию.",
        "keywords": ["создать папку", "новая папка", "directory", "folder", "mkdir"]
    },
    {
        "name": "cp",
        "description": "Копирует файл или директорию в другое место.",
        "keywords": ["копировать файл", "скопировать папку", "copy", "backup", "duplicate"]
    },
    {
        "name": "mv",
        "description": "Перемещает файл или папку или переименовывает объект.",
        "keywords": ["переместить файл", "переименовать", "move", "rename", "переместить папку"]
    },
    {
        "name": "rm",
        "description": "Удаляет файл или каталог.",
        "keywords": ["удалить файл", "delete file", "remove file", "clean", "стереть", "rm"]
    },
    {
        "name": "cat",
        "description": "Показывает содержимое файла или объединяет несколько файлов.",
        "keywords": ["посмотреть файл", "содержимое", "read text", "вывод текста", "concat"]
    },
    {
        "name": "ls",
        "description": "Показывает список файлов и папок в текущей директории.",
        "keywords": ["список файлов", "посмотреть папку", "list directory", "ls"]
    },
    {
        "name": "pwd",
        "description": "Показывает текущую рабочую директорию.",
        "keywords": ["текущая папка", "где я", "working directory", "path"]
    },
    {
        "name": "cd",
        "description": "Переходит в другую директорию.",
        "keywords": ["перейти в папку", "сменить каталог", "go to directory", "open folder"]
    },
    {
        "name": "echo",
        "description": "Выводит текст в консоль или в файл.",
        "keywords": ["напечатать текст", "вывести строку", "print message", "echo"]
    },
    {
        "name": "grep",
        "description": "Ищет текст в файлах или выводе команд.",
        "keywords": ["поиск строки", "поиск текста", "find text", "filter output", "grep"]
    },
    {
        "name": "find",
        "description": "Ищет файлы и папки по имени или условиям в каталоге.",
        "keywords": ["найти файл", "поиск файла", "search file", "find"]
    },
    {
        "name": "chmod",
        "description": "Изменяет права доступа к файлу или папке.",
        "keywords": ["права доступа", "permission", "изменить права", "chmod"]
    },
    {
        "name": "chown",
        "description": "Меняет владельца файла или группы.",
        "keywords": ["владелец файла", "owner", "group", "сменить владельца"]
    },
    {
        "name": "nano",
        "description": "Простой текстовый редактор в терминале.",
        "keywords": ["редактировать файл", "открыть редактор", "text editor", "nano"]
    },
    {
        "name": "vim",
        "description": "Мощный текстовый редактор в терминале.",
        "keywords": ["редактор кода", "text editor", "изменить файл", "vim"]
    },
    {
        "name": "tar",
        "description": "Создаёт и распаковывает tar-архивы.",
        "keywords": ["архив", "zip", "упаковать", "сжать", "untar", "tar"]
    },
    {
        "name": "gzip",
        "description": "Сжимает или распаковывает файлы в формате gzip.",
        "keywords": ["сжать файл", "gzip", "compress", "decompress"]
    },
    {
        "name": "unzip",
        "description": "Распаковывает zip-архивы.",
        "keywords": ["распаковать zip", "unpack archive", "zip file", "extract"]
    },
    {
        "name": "curl",
        "description": "Отправляет HTTP-запросы и получает данные из сети.",
        "keywords": ["загрузить страницу", "http запрос", "download url", "curl"]
    },
    {
        "name": "wget",
        "description": "Скачивает файлы по URL из сети.",
        "keywords": ["скачать файл", "download file", "по url", "wget"]
    },
    {
        "name": "ssh",
        "description": "Подключается к удалённому серверу по безопасному каналу.",
        "keywords": ["подключиться к серверу", "remote server", "login to host", "ssh"]
    },
    {
        "name": "scp",
        "description": "Копирует файлы между машинами по сети.",
        "keywords": ["скопировать файл на сервер", "copy remote file", "scp"]
    },
    {
        "name": "ps",
        "description": "Показывает работающие процессы в системе.",
        "keywords": ["процессы", "running processes", "top", "ps"]
    },
    {
        "name": "kill",
        "description": "Завершает процесс по PID или имени.",
        "keywords": ["остановить процесс", "kill process", "terminate app", "stop program"]
    },
    {
        "name": "top",
        "description": "Показывает активность процессов в реальном времени.",
        "keywords": ["мониторинг процессов", "load", "cpu", "memory", "top"]
    },
    {
        "name": "df",
        "description": "Показывает использование дискового пространства.",
        "keywords": ["место на диске", "disk usage", "free space", "df"]
    },
    {
        "name": "du",
        "description": "Показывает размер директорий и файлов.",
        "keywords": ["размер папки", "folder size", "disk usage", "du"]
    },
    {
        "name": "whoami",
        "description": "Показывает имя текущего пользователя.",
        "keywords": ["кто я", "current user", "username", "whoami"]
    },
    {
        "name": "uname",
        "description": "Показывает информацию об операционной системе и ядре.",
        "keywords": ["версия linux", "kernel", "os", "uname"]
    },
    {
        "name": "man",
        "description": "Открывает встроенную справку по команде.",
        "keywords": ["справка", "help", "manual", "man"]
    },
    {
        "name": "sudo",
        "description": "Запускает команду с правами суперпользователя.",
        "keywords": ["администратор", "root", "superuser", "rights", "sudo"]
    },
    {
        "name": "apt",
        "description": "Устанавливает, удаляет и обновляет пакеты в Debian/Ubuntu.",
        "keywords": ["установить пакет", "update package", "install program", "apt"]
    },
    {
        "name": "apt-get",
        "description": "Старый менеджер пакетов для установки и обновления программ.",
        "keywords": ["установить пакет", "install package", "update packages", "apt-get"]
    },
    {
        "name": "ping",
        "description": "Проверяет доступность узла по сети.",
        "keywords": ["проверить сеть", "host available", "ping server", "ping"]
    },
    {
        "name": "ifconfig",
        "description": "Показывает настройки сетевых интерфейсов.",
        "keywords": ["ip адрес", "network card", "address", "ifconfig"]
    },
    {
        "name": "ip",
        "description": "Показывает и управляет настройками сети.",
        "keywords": ["ip адрес", "network config", "interface", "ip"]
    },
    {
        "name": "history",
        "description": "Показывает список ранее введённых команд в терминале.",
        "keywords": ["история команд", "previous commands", "shell log", "history"]
    },
    {
        "name": "clear",
        "description": "Очищает экран терминала.",
        "keywords": ["очистить консоль", "clear screen", "reset terminal", "clear"]
    },
]


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-zа-я0-9\s]+", " ", text.lower()).strip()


SYNONYM_MAP = {
    "создание": {"создание", "создать", "создаёт", "create", "new"},
    "файл": {"файл", "файла", "file", "files"},
    "папка": {"папка", "папки", "каталог", "directory", "folder", "folders"},
    "удаление": {"удаление", "удалить", "delete", "remove", "del", "стереть"},
    "поиск": {"поиск", "найти", "search", "find"},
    "текст": {"текст", "строка", "line", "text"},
    "создать": {"создать", "создание", "create", "new"},
    "содержимое": {"содержимое", "read", "show", "view", "output"},
    "скачать": {"скачать", "download", "fetch"},
    "копия": {"копия", "копировать", "copy", "duplicate"},
    "перемещение": {"перемещение", "переместить", "move", "rename"},
    "права": {"права", "permission", "permissions", "chmod"},
    "архив": {"архив", "archive", "zip", "tar", "compress"},
    "сетевой": {"сеть", "сетевой", "network", "remote", "host", "ping"},
    "процесс": {"процесс", "процессы", "process", "task"},
}


def expand_tokens(text: str):
    tokens = set()
    for token in tokenize(text):
        tokens.add(token)
        for canonical, variants in SYNONYM_MAP.items():
            if token in variants:
                tokens.update(variants)
                tokens.add(canonical)
    return tokens


def tokenize(text: str):
    return [token for token in normalize_text(text).split() if token]


def score_command(query: str, command: dict) -> float:
    q = normalize_text(query)
    q_tokens = tokenize(q)
    if not q_tokens:
        return 0.0

    full_text = " ".join([
        command["name"],
        command["description"],
        *command["keywords"]
    ])
    full_text_norm = normalize_text(full_text)
    query_variants = expand_tokens(q)
    text_variants = expand_tokens(full_text_norm)

    score = 0.0
    overlap = query_variants & text_variants
    score += len(overlap) * 18

    for token in q_tokens:
        if token in full_text_norm.split():
            score += 12
        if token in normalize_text(command["name"]).split():
            score += 8

    if q in full_text_norm:
        score += 25

    # Точное совпадение по смысловым фразам
    exact_phrases = [
        "создать файл",
        "новый файл",
        "пустой файл",
        "создать папку",
        "новая папка",
        "удалить файл",
        "список файлов",
        "найти файл",
        "показать файл",
        "содержимое файла",
        "перейти в папку",
        "изменить права",
        "сделать архив",
        "скачать файл",
        "проверить сеть",
        "процесс",
        "остановить процесс",
    ]
    for phrase in exact_phrases:
        phrase_norm = normalize_text(phrase)
        if phrase_norm in q and phrase_norm in full_text_norm:
            score += 35

    score += SequenceMatcher(None, q, full_text_norm).ratio() * 45
    score += SequenceMatcher(None, q, normalize_text(command["description"])).ratio() * 20

    return score


def search_commands(query: str, limit: int = 10):
    if not query or not query.strip():
        return []

    results = []
    for command in COMMANDS:
        score = score_command(query, command)
        if score > 0:
            results.append((score, command))

    results.sort(key=lambda item: item[0], reverse=True)
    return [command for _, command in results[:limit]]


class CommandSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Поиск команд Linux")
        self.root.geometry("900x520")
        self.root.minsize(700, 400)

        self.frame = ttk.Frame(root, padding=12)
        self.frame.pack(fill="both", expand=True)

        ttk.Label(
            self.frame,
            text="Что нужно сделать? Например: создание файла, список папок, удалить файл, поиск текста",
            font=("Segoe UI", 11)
        ).pack(anchor="w", pady=(0, 8))

        self.search_var = tk.StringVar(value="Создание файла")
        self.entry = ttk.Entry(self.frame, textvariable=self.search_var, font=("Segoe UI", 12))
        self.entry.pack(fill="x", pady=(0, 10))
        self.entry.bind("<KeyRelease>", self.on_search)

        search_btn = ttk.Button(self.frame, text="Поиск", command=self.on_search)
        search_btn.pack(anchor="e", pady=(0, 10))

        columns = ("command", "description")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=18)
        self.tree.heading("command", text="Команда")
        self.tree.heading("description", text="Описание")
        self.tree.column("command", width=180, anchor="center")
        self.tree.column("description", width=600)
        self.tree.pack(fill="both", expand=True)

        self.on_search()

    def on_search(self, event=None):
        query = self.search_var.get()
        results = search_commands(query)
        self.tree.delete(*self.tree.get_children())

        if not results:
            self.tree.insert("", "end", values=("Нет результатов", "Попробуйте ввести: создание файла, поиск текста, пакет, удаление папки"))
            return

        for command in results:
            self.tree.insert("", "end", values=(command["name"], command["description"]))


def run_gui():
    if tk is None or ttk is None:
        print("Tkinter недоступен в этой среде. Используйте режим консоли.")
        return

    root = tk.Tk()
    app = CommandSearchApp(root)
    root.mainloop()


def run_console():
    print("Поиск команд Linux")
    print("Введите запрос, например: создание файла, поиск текста, копирование папки, удалить файл")
    print("Для выхода нажмите Ctrl+C\n")

    while True:
        try:
            query = input("Запрос: ").strip()
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break

        if not query:
            print("Пустой запрос. Попробуйте ещё раз.\n")
            continue

        results = search_commands(query, limit=8)
        if not results:
            print("Ничего не найдено. Попробуйте: создать файл, удалить файл, открыть папку, поиск текста.")
            print()
            continue

        print("\nВозможные команды:\n")
        for index, command in enumerate(results, start=1):
            print(f"{index}. {command['name']} — {command['description']}")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in {"--console", "-c"}:
        run_console()
    else:
        run_gui()
