"""
A general database key-value PDO
"""

import os
import sqlite3


class DBManager:
    """
    PDO for split3 database, stimulate key-value database schema
    """

    def __init__(self, db_dir):
        """
        constructor for DBManager

        @param db_dir: database directory
        """
        self.__cursor = None
        self.__db = None
        self.connect(db_dir)

    def create_table_if_not_exist(self, table_name: str):
        """
        create table via given table name, do nothing if table already exist

        @param table_name: table name
        @return:
        """
        self.__cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {table_name}
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL  ,
                            Key TEXT            NOT NULL UNIQUE ,
                            Value Text          NOT NULL)"""
        )

    def push(self, key: str, value: str, table_name: str):
        """
        push key-value into specified table

        @param key: key to push
        @param value: corresponding value
        @param table_name: table name
        @return:
        """
        try:
            self.__cursor.execute(
                f'INSERT INTO {table_name} (Key,Value) Values ("{key}", "{value}")'
            )
        except sqlite3.Error as e_msg:
            raise Exception(
                f"key f'{key}' already exist in table '{table_name}'"
            ) from e_msg

    def push_dict(self, data: dict, table_name: str):
        """
        push a dictionary into table
        @param data: data in dict format
        @param table_name: table name
        @return:
        """
        for key in data.keys():
            self.push(key, data[key], table_name)

    def update(self, key: str, value: str, table_name: str):
        """
        update value corresponding to given key in given table
        @param key: key name
        @param value: value name
        @param table_name: table name
        @return:
        """
        try:
            self.__cursor.execute(
                f'UPDATE {table_name} SET Value="{value}" WHERE Key="{key}"'
            )
        except sqlite3.Error as e_msg:
            raise Exception(str(e_msg)) from e_msg

    def remove(self, key: str, table_name: str):
        """
        remove item with given key from table given

        @param key: key name
        @param table_name: table name
        @return:
        """
        try:
            self.__cursor.execute(f'DELETE from {table_name} where key="{key}"')
        except sqlite3.Error as e_msg:
            raise Exception(str(e_msg)) from e_msg

    def drop_table(self, table_name: str):
        """
        drop the table with given table name

        @param table_name: table name
        @return:
        """
        self.__cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    def select(self, table_name: str, is_desc: bool = False, amount: int = -1) -> dict:
        """
        select items from table given

        @param table_name: table name
        @param is_desc: is ordered descend
        @param amount: amount item to be selected, if overflow or -1, select all items
        @return: selected items
        """
        arg_limit = "LIMIT " + str(amount) if amount != -1 else ""
        arg_desc = "ORDERED BY Value DESC" if is_desc else ""
        try:
            data = self.__cursor.execute(
                f"SELECT id, key, value  from {table_name} {arg_limit} {arg_desc}"
            )
        except Exception as e_msg:
            raise Exception(
                f"error occur when select from table: {table_name}"
            ) from e_msg
        out = {}
        for row in data:
            out[row[1]] = row[2]
        return out

    def select_where(self, table_name: str, key: str) -> list:
        try:
            data = self.__cursor.execute(
                f"SELECT id, key, value  from {table_name} WHERE key = '{key}'"
            )
        except Exception as e_msg:
            raise Exception(
                f"error occur when select from table: {table_name}"
            ) from e_msg
        return list(data.fetchall())

    def commit(self):
        """
        commit database change

        @return:
        """
        try:
            self.__db.commit()
        except Exception as e_msg:
            raise Exception("error occur when commit database") from e_msg

    def close(self):
        """
        close the database

        @return:
        """
        try:
            self.__db.close()
        except Exception as e_msg:
            raise Exception("error occur when close database") from e_msg

    def connect(self, db_dir):
        """
        connect the database

        @param db_dir: database directory
        @return:
        """
        if not os.path.exists(db_dir):
            print(f"create new db: {db_dir} in: ")
        else:
            print(f"connect to db: {db_dir}")
        self.__db = sqlite3.connect(db_dir, check_same_thread=False)
        self.__cursor = self.__db.cursor()
