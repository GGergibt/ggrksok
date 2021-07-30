from pathlib import Path


def checking_path():
    path = Path("phonebook")
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        pass
    else:
        pass


def get_phonebook(name):
    """Функция проверяет наличие файла и если он есть отдает номер телефона"""
    checking_path()
    path = Path(f"phonebook/{name}.txt")
    if path.exists():
        with path.open() as f:
            phone = "".join(f.readlines())
        return phone


def write_phonebook(name, phone):
    """Функция  создает файла по имени и записывает номер телефона"""
    checking_path()
    try:
        path = Path(f"phonebook/{name}.txt")
        with open(f"phonebook/{name}.txt", "w") as file:
            file.writelines(phone)
        return True
    except:
        print("Ошибка записи")


def delete_phonebook(name):
    """Функция удаляет файл по имени"""
    checking_path()
    path = Path(f"phonebook/{name}.txt")
    if path.exists():
        path.unlink()
        return True
