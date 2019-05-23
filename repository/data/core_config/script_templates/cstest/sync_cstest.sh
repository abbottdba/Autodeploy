#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin
pro_name="{app_name}"
git_name="{git_name}"
_type="web"
base_dir="/opt/compose-conf/web/$[[[pro_name]]]/data/$[[[_type]]]"
pro_dir="$[[[base_dir]]]/$[[[git_name]]]"
webfiles="$[[[base_dir]]]/webfiles"
docker_name="$[[[pro_name]]]_$[[[_type]]]"
git_address="http://om:VA1913wm@git.neweb.me/Domingo/$[[[git_name]]].git"

if [[ -d "$[[[pro_dir]]]" ]]
then
	cd $[[[pro_dir]]]
	git reset --hard HEAD
	git pull $[[[git_address]]]
else
	cd $[[[base_dir]]]
	git clone $[[[git_address]]] -b build
fi

rsync -avP --delete $[[[pro_dir]]]/ $[[[webfiles]]] --exclude=.git* 2>&1 >> /dev/null

docker-enter $[[[docker_name]]] rsync -avP --delete /opt/cpms/ /usr/share/nginx/cpms/
docker-enter $[[[docker_name]]] mkdir /etc/nginx/mod.d
docker-enter $[[[docker_name]]] cp -rfv /opt/conf/mod.conf /etc/nginx/mod.d
docker-enter $[[[docker_name]]] cp -rfv /opt/conf/nginx.conf /etc/nginx/
docker-enter $[[[docker_name]]] cp -rfv /opt/conf/default.conf /etc/nginx/conf.d/
docker-enter $[[[docker_name]]] /etc/init.d/nginx restart