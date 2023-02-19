
db = db.getSiblingDB('GreekParliamentProceedings');
db.createUser(
    {
        user : "greekparliament",
        pwd : "greekparliament",
        roles: [{
            role : "readWrite",
            db : "GreekParliamentProceedings"
        }]
        
    }
)
