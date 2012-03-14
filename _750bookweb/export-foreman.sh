#!/bin/bash
DIR=/home/kevinr/src/750book-web-project/_750bookweb
APP=750book
PORT=8000
USER=kevinr
FOREMAN=/var/lib/gems/1.9.1/bin/foreman

#adduser --system --group --home /home/kevinr/src/750book-web-project/_750bookweb --no-create-home --disabled-login --disabled-password --shell /bin/false sevenfiftybook

rm /etc/init/$APP*.conf

cat > /etc/init/$APP.conf <<EOF
start on runlevel [2345]
stop on runlevel [016]

pre-start script

bash << "EOS"
  mkdir -p /var/log/$APP
  chown -R $USER /var/log/$APP
EOS

end script
EOF

cat > /etc/init/$APP-foreman.conf <<EOF
start on starting $APP
stop on stopping $APP
respawn

exec su - $USER -c 'cd $DIR; $FOREMAN start --port $PORT --app $APP --user $USER'
EOF
