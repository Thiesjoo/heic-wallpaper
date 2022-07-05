sshfs -o sftp_server='/usr/bin/sudo /usr/lib/openssh/sftp-server',allow_other  thies@raspberrypi.local:/home/thies/prod/heic-wallpaper/static remotestatic/
docker-compose -f remote-worker.yml up --build
sudo umount remotestatic/