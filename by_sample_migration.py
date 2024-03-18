import sqlite3


def wtmd(com, fn):  # writing_the_migration_down
    with open(f"{fn[:-3]}.sql", "a") as file:
        file.write(f"{com}\n")


# считывание названия таблиц 2х БД
def read_name_table(cursor_db_1, cursor_db_2):
    sql_table = 'SELECT name FROM sqlite_master WHERE type="table"'

    mas_table_db1 = []
    command_table_db1 = cursor_db_1.execute(sql_table)
    for string in command_table_db1:
        mas_table_db1.append(string)

    mas_table_db2 = []
    command_table_db2 = cursor_db_2.execute(sql_table)
    for string in command_table_db2:
        mas_table_db2.append(string)

    mas = (mas_table_db1, mas_table_db2)
    return mas


# добавление новых таблиц в бд №2
def add_tables(mas_table_db1, mas_table_db2, cursor_db_2, fn):
    for name_table_db1 in mas_table_db1:
        name_no = True
        for name_table_db2 in mas_table_db2:
            if name_table_db1[0] == name_table_db2[0]:
                name_no = False
                break
        if name_no:
            command = 'CREATE TABLE ' + name_table_db1[0] + '(test text)'  # + (test test) т.к.
            # нельзя создать пустую таблицу
            wtmd(command, fn)
            print(command)
            cursor_db_2.execute(command)
            mas_table_db2.append(name_table_db1)
    return mas_table_db2


# удаление лишних таблиц из бд №2
def drop_tables(mas_table_db1, mas_table_db2, cursor_db_2, fn):
    for name_table_db2 in mas_table_db2:
        name_no = True
        for name_table_db1 in mas_table_db1:
            if name_table_db2[0] == name_table_db1[0]:
                name_no = False
                break
        if name_no:
            command = 'DROP TABLE ' + name_table_db2[0]
            wtmd(command, fn)
            print(command)
            cursor_db_2.execute(command)


# добавление новых колонок в таблицы БД № 2
def add_columns(name_table, mas_column_db1, mas_column_db2, cursor_db_2, fn):
    for name_column_db1 in mas_column_db1:
        column_no = True
        for name_column_db2 in mas_column_db2:
            if name_column_db1[1] == name_column_db2[1]:
                column_no = False
                break
        if column_no:
            command = 'ALTER TABLE ' + name_table + ' ADD COLUMN ' + name_column_db1[1] + ' ' + name_column_db1[2]
            wtmd(command, fn)
            print(command)
            cursor_db_2.execute(command)
            mas_column_db2.append(name_column_db1)
    return mas_column_db2


# удаление лишних колонок из БД №2
def drop_columns(name_table, mas_column_db1, mas_column_db2, cursor_db_2, fn):
    for name_column_db2 in mas_column_db2:
        column_no = True
        for name_column_db1 in mas_column_db1:
            if name_column_db2[1] == name_column_db1[1]:  # and name_column_db2[2] == name_column_db1[2]:
                column_no = False
                break
        if column_no:
            command = 'ALTER TABLE ' + name_table + ' DROP COLUMN ' + name_column_db2[1]
            wtmd(command, fn)
            print(command)
            cursor_db_2.execute(command)


# обновление структуры колонок в таблицах БД
def update_columns(mas_table_db1, cursor_db_1, cursor_db_2, fn):
    for name_table in mas_table_db1:
        command_name_column = 'pragma table_info(' + name_table[0] + ')'
        command_column_db1 = cursor_db_1.execute(command_name_column)
        command_column_db2 = cursor_db_2.execute(command_name_column)
        mas_column_db1 = []
        mas_column_db2 = []
        for string in command_column_db1:
            mas_column_db1.append(string)
        for string in command_column_db2:
            mas_column_db2.append(string)

        mas_column_db2 = add_columns(name_table[0], mas_column_db1, mas_column_db2, cursor_db_2, fn)
        drop_columns(name_table[0], mas_column_db1, mas_column_db2, cursor_db_2, fn)


# основная программа
def migrate(name_db1, name_db2):
    open(f"{name_db1[:-3]}.sql", 'w').close()  # очистка перед записью

    con_db_1 = sqlite3.connect(name_db2)
    con_db_2 = sqlite3.connect(name_db1)
    cursor_db_1 = con_db_1.cursor()
    cursor_db_2 = con_db_2.cursor()

    mas = read_name_table(cursor_db_1, cursor_db_2)
    mas_table_db1 = mas[0]
    mas_table_db2 = mas[1]

    mas_table_db2 = add_tables(mas_table_db1, mas_table_db2, cursor_db_2, name_db1)
    drop_tables(mas_table_db1, mas_table_db2, cursor_db_2, name_db1)

    update_columns(mas_table_db1, cursor_db_1, cursor_db_2, name_db1)

    con_db_1.commit()
    con_db_2.commit()
    con_db_1.close()
    con_db_2.close()


# if __name__ == "__main__":
#     migrate('users11.db', 'users12.db')  # первая меняет свою структуру на структуру второй
