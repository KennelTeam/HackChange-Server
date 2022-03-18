#!/bin/bash
host_ip=185.46.11.220
server_port=5003

#IMPORTANT!! RUN ONLY ON CLEAN DATABASE!!

echo "Fillig instruments and topics"
mysql -h $host_ip -P 3306 -u hackchange_admin -p hack_change < create_instruments.sql

echo "Filling investors and posts"
python3 fill_through_server.py $host_ip:$server_port

echo "Done!"