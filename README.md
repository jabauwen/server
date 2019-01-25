0. Install docker
https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-using-the-repository

1. Radarr docker:
sudo ln `pwd`/radarr.service /etc/systemd/system/docker-radarr.service
crontab -e --> * * 1 * * /home/jbauwens/github/server/radarr/automatic_update.sh
