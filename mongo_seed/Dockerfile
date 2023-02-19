FROM mongo:5.0
 # Will be set through Environment Files
 ARG DATABASE_URI
 ARG USERNAME
 ARG PASSWORD

 ENV DATABASE_URI ${DATABASE_URI}
 ENV USERNAME ${USERNAME}
 ENV PASSWORD ${PASSWORD}

 COPY DatabaseFinal.json /db.json

 COPY InvertedIndex.json /index.json

 CMD mongoimport --username ${USERNAME} --password ${PASSWORD} --uri ${DATABASE_URI} --collection Database --drop --file /db.json && \
     mongoimport --username ${USERNAME} --password ${PASSWORD} --uri ${DATABASE_URI} --collection InvertedIndex --drop --file /index.json
