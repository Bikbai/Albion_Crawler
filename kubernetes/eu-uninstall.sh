for f in $(find ./eu-*.yml -maxdepth 1 -type f); do kubectl delete -f $f; done
