# Canvas scraper
Forked from [Koenvh1](https://gist.github.com/Koenvh1/6386f8703766c432eb4dfa19acdb0244)

# Please double-check the data
Often professors will embed videos that require authentication to view, etc.
At time of writing, this script does not handle such embeds.
Please make sure you can view all resources offline without connecting to a server
before calling your import done.

# Docker
A Docker image is provided for convenience. You can configure it to write to a
data directory of your choice. To make a data directory named `data` and bind
mount it to the Docker container, perform the following commands:

`mkdir ./data`

```
docker run \
  -u "$(id -u)" \
  -v "$(pwd)"/data:/usr/src/app/data \
  johnhix/scrape-canvas:0.0.1 \
  https://institution.canvas-address.edu \
  canvas-api-key \
  ./data \
  all

```
The last option, `all`, can be replaced with a comma-separated list
of course ids.
