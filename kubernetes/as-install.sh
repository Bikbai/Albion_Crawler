for f in $(find ./as-*.yml -maxdepth 1 -type f); do kubectl apply -f $f; done
