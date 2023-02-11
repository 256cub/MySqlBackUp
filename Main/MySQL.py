import logging
import config

import mysql.connector

logging.basicConfig(filename=config.APP_LOG_PATH, encoding='utf-8', level=logging.INFO, format="%(asctime)s: [%(levelname)s] [LINE:%(lineno)s] [FILE:%(filename)s] %(message)s")


class MySQL:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            passwd=config.DB_PASSWORD,
            database=config.DB_DATABASE,
            auth_plugin="mysql_native_password"
        )

    def select(self, query):
        sql_cursor = self.connection.cursor(dictionary=True)
        sql_cursor.execute(query)
        sql_result = sql_cursor.fetchall()
        sql_cursor.close()
        return sql_result

    def select_single(self, query):
        sql_cursor = self.connection.cursor(dictionary=True)
        sql_cursor.execute(query)
        sql_result = sql_cursor.fetchone()
        sql_cursor.close()
        return sql_result

    def update(self, query):
        sql_cursor = self.connection.cursor()
        sql_cursor.execute(query)
        self.connection.commit()
        last_row = sql_cursor.fetchone()
        sql_cursor.close()
        return last_row

    def insert(self, query):
        sql_cursor = self.connection.cursor()
        sql_cursor.execute(query)
        self.connection.commit()
        last_row_id = sql_cursor.lastrowid
        sql_cursor.close()
        return last_row_id

    def close(self):
        self.connection.close()

    def get_table_columns(self, table):
        return self.select('SHOW columns FROM {}'.format(table))

    def get_from_db(self, table, column_name='status', column_value='ACTIVE', limit=100):
        try:
            query = "SELECT * FROM `{}` ".format(table)

            if column_name:
                if column_value == 'null':
                    query += "WHERE `{}` IS NULL ".format(column_name)
                else:
                    query += "WHERE `{}` = '{}' ".format(column_name, column_value)

            query += "ORDER BY RAND() LIMIT {}; ".format(limit)

            if limit == 1:
                return self.select_single(query)
            else:
                return self.select(query)
        except Exception as exception:
            logging.error(exception)
            logging.error(query)

    def get_from_db_by_multiple(self, table, columns_name=None, columns_value=None, limit=1):
        try:
            query = "SELECT * FROM `{}` WHERE ".format(table)
            for column_id, column_name in enumerate(columns_name):
                query += " `{}` = {} AND ".format(column_name, columns_value[column_id])

            query += "ORDER BY RAND() LIMIT {}; ".format(limit)
            query = query.replace('AND ORDER', ' ORDER')

            if limit == 1:
                return self.select_single(query)
            else:
                return self.select(query)
        except Exception as exception:
            logging.error(exception)
            logging.error(query)

    def delete_from_db(self, table, column_name, column_value):
        try:
            query = "DELETE FROM `{}` WHERE `{}` = '{}'; ".format(table, column_name, column_value)
            return self.select(query)
        except Exception as exception:
            logging.error(exception)
            logging.error(query)

    def update_row_into_table(self, table, columns, match_column='id'):
        try:
            query = "UPDATE `{}` SET ".format(table)
            for column_id, column_name in enumerate(columns):
                if column_name == match_column:
                    continue
                query += "`{}` = \"{}\", ".format(column_name, columns[column_name])

            size = len(query)
            query = query[:size - 2]
            query += " WHERE `{}` = {} ".format(match_column, columns[match_column])

            return self.update(query)
        except Exception as exception:
            logging.error(exception)
            logging.error(query)

    def save_json_into_table(self, table, params, match_columns=['id']):
        try:

            columns = self.get_table_columns(table)

            columns_name = []
            columns_value = []

            for column in columns:
                if column['Field'] in params:

                    if column['Type'] == b'tinyint(1)' or column['Type'] == 'tinyint(1)':
                        column_value = str(int(params[column['Field']]))
                    elif column['Type'] == b'varchar(255)' or column['Type'] == 'varchar(255)':
                        column_value = str(params[column['Field']])
                        column_value = column_value.replace('"', "")
                        column_value = column_value[:254]
                    else:
                        column_value = str(params[column['Field']])
                        column_value = column_value.replace('"', '')

                    columns_name.append(column['Field'])
                    columns_value.append('"' + column_value + '"')

            if len(match_columns) == 1:
                found_id = self.get_from_db(table, column_name=match_columns[0], column_value=params[match_columns[0]], limit=1)

                if found_id:
                    query = "UPDATE `{}` SET ".format(table)
                    for column_id, column_name in enumerate(columns_name):
                        query += "`{}` = {}, ".format(column_name, columns_value[column_id])

                    query += "WHERE `{}` = \"{}\"; ".format(match_columns[0], params[match_columns[0]])
                    query = query.replace(', WHERE', ' WHERE')

                    self.update(query)
                    return found_id['id']

                else:
                    query = "INSERT INTO `{}` ({}) VALUES ({}) ".format(table, ', '.join(columns_name), ', '.join(columns_value))
                    return self.insert(query)
            else:
                found_id = self.get_from_db_by_multiple(table, columns_name=match_columns, columns_value=[params[match_columns[0]], params[match_columns[1]]], limit=1)
                if found_id:
                    return found_id['id']
                else:
                    query = "INSERT INTO `{}` ({}, {}) VALUES ({}, {}) ".format(table, match_columns[0], match_columns[1], params[match_columns[0]], params[match_columns[1]])
                    return self.insert(query)

        except Exception as exception:
            print('ERROR')
            logging.error(exception)
            logging.error(query)

    def get_tables(self, table):
        try:

            query = 'SHOW TABLES;'
            tables = self.select(query)
            print(table)
            return tables

        except Exception as exception:
            logging.error(exception)
            logging.error(query)

    def get_databases(self):
        try:
            
            query = 'SHOW DATABASES;'
            found_databases = self.select(query)

            databases = []
            for found_database in found_databases:
                if found_database['Database'] not in config.DATABASE_TO_EXCLUDE:
                    databases.append(found_database)

            return databases

        except Exception as exception:
            logging.error(exception)
            logging.error(query)
