#!/bin/bash
echo "-------------------------"
echo Snapshot Water Quality App Linux configuration files
echo "existing files will be saved as [name].old"
echo "Timestamp: $(date +'%Y-%m-%d %T')"
echo "-------------------------"
echo " Copying custom not found  html page ..."
cat custom_50x.txt >custom_50x.txt.old
cat /usr/share/nginx/html/custom_50x.html >custom_50x.txt
echo " Copy complete."
echo " Copying NGINX configuration ..."
cat nginx_config.txt >nginx_config.txt.old
cat /etc/nginx/sites-available/reverse-proxy >nginx_config.txt
echo " Copy complete."
echo " Copying map.service file ..."
cat map.service >map.service.old
cat /etc/systemd/system/map.service >map.service
echo " Copy complete."
echo " ============ Snapshot complete ==========="
