# MongoDB setup and connection

class User(db.Document):
    user = db.StringField()
    pwd = db.StringField()  # Remember to hash the password before storing
    images = db.ListField(db.DictField())  # This can contain URLs or IDs pointing to actual images
    pendingDocRequests = db.ListField(db.DictField())
    inboundDocRequests = db.ListField(db.DictField())
    storedDocClasses = db.ListField()
    