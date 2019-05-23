#!/bin/bash 
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin
#ruibo_mobile_h5
HUB='omhub.neweb.me'
pro_name="ruibo"
_type="mobile"
base_dir="/opt/compose-conf/web/$[[[pro_name]]]/data/$[[[_type]]]"
webfiles="$[[[base_dir]]]/webfiles/"
bak_webfiles="$[[[base_dir]]]/bak_webfiles/"
docker_name="ruibo_mobile_h5"
###get lasttime depoly cstest container###
if [ -d $[[[bak_webfiles]]] ];then
	cd $[[[bak_webfiles]]]
  else
	echo -e "\nerror: $[[[bak_webfiles]]] not exist\n"
	exit 1
fi
lasttime=$(ls -lrt | tail -1|awk '[[[print $NF]]]')
echo -e "\nrollbaktime: $[[[lasttime]]]\n"
rsync -avP --delete $[[[base_dir]]]/bak_webfiles/$[[[lasttime]]]/ $[[[webfiles]]]
docker-enter $[[[docker_name]]] rsync -avP --delete /opt/cpms/ /usr/share/nginx/cpms/
docker-enter $[[[docker_name]]] mkdir /etc/nginx/mod.d
docker-enter $[[[docker_name]]] cp -rfv /opt/conf/mod.conf /etc/nginx/mod.d
docker-enter $[[[docker_name]]] cp -rfv /opt/conf/nginx.conf /etc/nginx/
docker-enter $[[[docker_name]]] cp -rfv /opt/conf/default.conf /etc/nginx/conf.d/
docker-enter $[[[docker_name]]] /etc/init.d/nginx restart
####commit image and push registory######
CT=`docker inspect --format="[[[[[[.Id]]]]]]" $[[[docker_name]]]`
docker login -u omadmin -p "Ad@sn1407" -e om@sinonet.ph omhub.neweb.me:5000
echo -e "commit images.....\n"
docker commit $[[[CT]]] $[[[HUB]]]:5000/$[[[docker_name]]]
docker push $[[[HUB]]]:5000/$[[[docker_name]]]
docker logout omhub.neweb.me:5000