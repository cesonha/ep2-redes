import socket

def ping(connection):
    connection.send(bytes('PING', 'utf-8'))

def answerPing(connection):
    connection.send(bytes('PONG', 'utf-8'))

def hello(connection):
    connection.send(bytes('HELLO', 'utf-8'))

def answerHello(connection):
    connection.send(bytes('OK', 'utf-8'))
