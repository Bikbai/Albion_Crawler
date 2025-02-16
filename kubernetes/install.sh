for f in $(find ./evp*.yml -maxdepth 1 -type f); do kubectl apply -f $f; done
for f in $(find ./btp*.yml -maxdepth 1 -type f); do kubectl apply -f $f; done
for f in $(find ./*scrape.yml -maxdepth 1 -type f); do kubectl apply -f $f; done
