for f in $(find ./as-*.yml -maxdepth 1 -type f); do kubectl delete -f $f; done
