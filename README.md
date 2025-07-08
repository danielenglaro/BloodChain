                                                                                                        # Questo è il repository del progetto BloodChain
BloodChain è un progetto che nasce con l'obiettivo di creare un sistema trasparente e affidabile per la gestione delle donazioni sanguigne. Tutti i dati sono gestiti da una BlockChain permissioned basata su Fabric. \
BloodChain dal suo sito vuole fornire uno strumento ad ospedali e donatori. I primi hanno la possibilità di gestire la propria emoteca, mentre i donatori possono avere traccia del proprio contributo alla causa delle donazioni.

## Struttura del progetto
│   ├── routes.py          Tutte le app.route del sito \
|   ├── models.py          Definizione degli oggetti da inviare al database \
│   ├── api.py             Le API verso la blockchain \
│   ├── auth.py            Funzioni per login/registrazione  (auth)\
│   └── utils.py           Funzioni da richiamare

## TODO- Inserire tutti i json payload nel backend flask
- Inserire "sudo usermode -aG docker %USER" (VAR USER) per non avere comandi bloccanti
- Ottimizzare i form  nelle pagine del sito
- Far funzionare effettivamente il login
    -  1. Scrivere sul db
    -  2. Fare il check della riga per entrare
    -  3. Creare il form per la registrazione
- Utilizzare il software Hyperledge explorer che ci ha fatto vedere Alma per dare una proof delle API scambiate con la blockcahin
- Capire se bisogna fare anche gli atlri payload che stanno dentro payload.txt


## TODO da Lezione
- Cifrare i paylaod per interi
- Per fare il login non facciamo il controllo degli hash, mandaimo al db i dati in chiaro e tutto l'hash con sale avviene direttamente li. Quindi quando il backend invoca un controllo fa la chiamata in chiaro, il db prende hasha e controlla.

- Rotazione chiave per i cookie 
- Prendere coordinate open street maps




##Svejate

#Pagina Ospedale
-Implementare il trasferimento
-Implementare il cambio di stato (data una chiave di una sacca possiamo renderla non fruibile)

#Pagina Donatore
-Quando entri viene prima fatta una GetKV, che popola la tabella della dashboard del donatore.
-Inserire un banner con le notifiche mediche