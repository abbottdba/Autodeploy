#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin
HUB='omhub.neweb.me'
image_name="veligood_front_web"
pro_name="veligood_front"
_type="web"

bak_webfiles()[[[
    date_now=`date +"%Y%m%d%H%M%S"`
    base_dir="/opt/compose-conf/web/$[[[pro_name]]]/data/$[[[_type]]]"
    webfiles="$[[[base_dir]]]/webfiles/"
    bak_webfiles="$[[[base_dir]]]/bak_webfiles/$[[[date_now]]]"
    rsync -avP --delete $[[[webfiles]]] $[[[bak_webfiles]]]
]]]

upload_data()[[[
    url_path=''
    old_url_path='href=/'
    base_dir="/opt/compose-conf/web/$[[[pro_name]]]/data/$[[[_type]]]"
    webfiles=$[[[base_dir]]]/webfiles/
    pro_webfiles=$[[[base_dir]]]/pro_webfiles/
    rsync_passwd_file=/etc/rsyncd.passwd
    ftp_dir=allftp/eu-lite/$[[[_type]]]/

    rsync -avzcP --exclude index.html --delete --password-file=$[[[rsync_passwd_file]]] $[[[webfiles]]] ben@m1ftp.neweb.me::$[[[ftp_dir]]]
    rsync -avP --delete $[[[webfiles]]] $[[[pro_webfiles]]]
    sed -i s#$[[[old_url_path]]]#$[[[url_path]]]# $[[[pro_webfiles]]]/index.html

    docker-enter $[[[image_name]]] rsync -avP --delete /opt/pro_cpms/ /usr/share/nginx/cpms/
    docker-enter $[[[image_name]]] mkdir /etc/nginx/mod.d
    docker-enter $[[[image_name]]] cp -rfv /opt/conf/mod.conf /etc/nginx/mod.d
    docker-enter $[[[image_name]]] cp -rfv /opt/conf/nginx.conf /etc/nginx/
    docker-enter $[[[image_name]]] cp -rfv /opt/conf/default.conf /etc/nginx/conf.d/
    docker-enter $[[[image_name]]] /etc/init.d/nginx restart
]]]

# bak webfiles
#bak_webfiles $[[[pro_name]]] $[[[_type]]]
# upload static files
#upload_data $[[[pro_name]]] $[[[_type]]] $[[[image_name]]]

CT=`docker inspect --format="[[[[[[.Id]]]]]]" $[[[image_name]]]`
DATE=`date +%F-%H-%M-%S`
docker login -u omadmin -p "Ad@sn1407" -e om@sinonet.ph omhub.neweb.me:5000
docker -H $[[[HUB]]] login -u omadmin -p "Ad@sn1407" -e om@sinonet.ph omhub.neweb.me:5000
####commit image and push registory######
echo -e "version: $[[[DATE]]] \n"
echo -e "commit images.....\n"
docker commit $[[[CT]]] $[[[HUB]]]:5000/$[[[image_name]]]
docker push $[[[HUB]]]:5000/$[[[image_name]]]
####back image to HUB#########
hubimage=$(docker -H $[[[HUB]]] images | grep $[[[HUB]]]:5000/$[[[image_name]]])
if [[ ! -z $[[[hubimage]]] ]]
  then
	docker -H $[[[HUB]]] tag $[[[HUB]]]:5000/$[[[image_name]]] $[[[HUB]]]:5000/$[[[image_name]]]:$DATE
	docker -H $[[[HUB]]] pull $[[[HUB]]]:5000/$[[[image_name]]]
else
	echo "Not found $[[[image_name]]] of $HUB server"
	docker -H $[[[HUB]]] pull $[[[HUB]]]:5000/$[[[image_name]]]
fi
docker logout omhub.neweb.me:5000