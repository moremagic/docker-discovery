##Quick-start  
# docker run -d -p 80:80 -p 443:443 -p :22 -e NEXT_HOST=(次段Nginxのホスト名) -e DOCKER_HOST=(Docker Host の内部IPアドレス):2375 docker-discovery  

