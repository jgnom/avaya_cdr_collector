# -*- coding: utf-8 -*-
# python3

from loguru import logger
import time
import socket
import re
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time


logger.add("/var/log/cdr_collector/cdr_collector_{time:DD-MM-YYYY}.log",
    format="{time:DD-MM-YYYY at HH:mm:ss} {level} {message}", rotation="20 MB", compression="zip")

serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv_sock.bind(('', 9000))
serv_sock.listen(10)


def recieve_msg(client_sock):
    while True:
        len_msg = 102
        len_msg_socket = len_msg * 9000
        valid_msg = []
        msg = client_sock.recv(len_msg_socket) #.decode("utf-8") # I got the error when I put server.recv
        
        if len(msg) == len_msg:
            logger.debug(f"Received {len(msg)} byte")
            global start_time
            start_time = time.time()
            msg = msg.decode("utf-8")
            valid_msg.append(msg)
            msg = valid_msg
            return msg
            
        elif len(msg) > len_msg:
            logger.debug(f"Received {len(msg)} byte")
            i = r"b'\d{9}"
            ls = [msg[i:i+len_msg] for i in range(0,len(msg),len_msg)] 
            for i in ls:
                if len(i) == len_msg:
                    i = i.decode("utf-8")
                    valid_msg.append(i)
            msg = valid_msg            
            return msg
            break
            
        elif len(msg) == 0:
            logger.info(f"Received {len(msg)} byte client DISCONNECTED!!!")
            timing = start_time - time.time()
            logger.info(f"Время обработки = {timing}")
            return False
            break
            
        else:
            logger.info(f"ACM is CONNECTED, time {msg.decode('utf-8')}")


def start(serv_sock):
    serv_sock.listen(1)
    while True:
        logger.info(f"waiting connection, socket is OPEN!!!")
        client_sock, client_addr = serv_sock.accept()
        logger.info(f"Connected to socket by, {client_addr}")
        while True:
            msg = recieve_msg(client_sock)
            
            if msg == False:
                client_sock.close()
                break
            else:    
                put_to_db(msg)
                
        logger.info(f"Socket connection by {client_addr} is CLOSED!!!")
        client_sock.close()
        
                
def put_to_db(msg):
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user="user",
        # пароль, который указали при установке PostgreSQL
        password="password",
        host="127.0.0.1",
        port="5432")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        #sql_insert_query = f"SELECT cdr_unformatted_func_py({tst})"
        sql_insert_query = f"SELECT cdr_unformatted_func_py(VARIADIC ARRAY{msg!r})" # !r для того чтобы строка передавалась  с ковычками.
        cursor.execute(sql_insert_query)
        connection.commit()
    except (Exception, Error) as error:
        logger.error(f"Error at work PostgreSQL, {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.debug(f"Data length={len(msg)} has been successfully written to the database")
            

start(serv_sock)