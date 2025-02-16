for f in $(find ./evp*.yml -maxdepth 1 -type f); do kubectl delete -f $f; done
