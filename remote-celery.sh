sshfs -o sftp_server='/usr/bin/sudo /usr/lib/openssh/sftp-server',allow_other  thies@raspberrypi.local:/home/thies/prod/heic-wallpaper/static remotestatic/
docker-compose -f docker-compose-remote-raspberry.yml up --build
sudo umount remotestatic/