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
    """Read user file"""
    checking_path()
    path = Path(f"phonebook/{name}.txt")
    if path.exists():
        with path.open() as f:
            phone = "".join(f.readlines())
        return phone


def write_phonebook(name, phone):
    """Write user file"""
    checking_path()
    try:
        path = Path(f"phonebook/{name}.txt")
        with open(f"phonebook/{name}.txt", "w") as file:
            file.writelines(phone)
        return True
    except:
        print("Ошибка записи")


def delete_phonebook(name):
    """Delete user file"""
    checking_path()
    path = Path(f"phonebook/{name}.txt")
    if path.exists():
        path.unlink()
        return True
