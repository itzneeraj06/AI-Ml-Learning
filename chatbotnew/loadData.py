from langchain_community.document_loaders.mongodb import MongodbLoader
loader = MongodbLoader(
    connection_string="mongodb+srv://neerajchouhan:replace@cluster0.h0byp.mongodb.net/",
    db_name="visitorTesting",
    collection_name="visitors",
    field_names=["prefix","firstName","lastName","emailAddress","phoneNumber","visitorType","identityType","identityNumber","gender","address","comment","totalVisit","file","status","verified","active","createdBy","companyId","createdAt"],
)
docs = loader.load()

print(docs[0])