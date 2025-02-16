for f in $(find ./eu-*.yml -maxdepth 1 -type f); do kubectl apply -f $f; done
