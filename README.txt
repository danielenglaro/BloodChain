## Creare il container con il Database Mysql, importante prendere la password e vede se su flask è uguale, anche la porta 
docker run --name nome-container -e MYSQL_ROOT_PASSWORD=tuapassword -e MYSQL_DATABASE=Users -p 3306:3306 -d mysql:latest

##Accedere al container
docker exec -it nome-container mysql -u root -p

##TODO
Creare lo yaml nostro mysql per tenere sempre su il container per il DB, per vedere cosa scrivere vedere back-end.yaml