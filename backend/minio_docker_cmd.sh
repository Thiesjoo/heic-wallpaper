docker run -t  -p 9000:9000 -p 9090:9090  --name "minio_local" --rm \
  minio/minio server /data --console-address ":9090"
