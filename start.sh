if [ "$(uname -m)" = "aarch64" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.arm.yml up --build -d
else
    docker-compose up --build
fi
