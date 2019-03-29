#!/bin/bash

echo "#### NÃO DEFINA SENHA PARA ROOT NO MYSQL"
echo "#### QUANDO APARECER AS JANELAS, BASTA APERTAR 'ENTER'"
sudo apt-get install mysql-server
sudo apt-get install python-mysqldb
mysql -u root -e "create database signsdb"