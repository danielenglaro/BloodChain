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


##TODO
Modificato il nome del database quindi ricreare il container

##Login
Quando un ospedale si registra viene composto un blocco che contiene i dati dell'ospedale, ADDKV con un payload equivalente alle colonne dell'attuale tabella Dati_Ospedale. Quando un ospedale fa login inserisce username e pw, che rapprensentano la coppia chiave che viene preso per lanciare la GETKV, in modo che nella sessione abbiamo tutte le info dell'ospedale. 
Quando facciamo ad esempio una ADDKV, compone le variabili locali che vengono accodate a tutte le operazioni necessarie, in questo modo la pagina ha il contesto di chi sta utilizzando la pagina.

##Sensore
Prima di accorpare un tot di transazioni, scorriamo il csv a caccia di un eventuale problema di range temperatura, se il test ha successo avviene l'ADDKV (creare Payload adhoc per le temperature) sulla blockchain direttamente.