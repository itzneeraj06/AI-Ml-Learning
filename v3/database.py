from pymongo import MongoClient
from bson import ObjectId
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["pos-samyotech-in"]

reference_mapping = {
   "expenseNameId": "expensetypes",
   "paymentId": "payments",
   "customerId": "customers",
   "categoryId": "categories",
   "ingredientId": "ingredients",
   "chef":"employees",
   "order": "orders",
   "items[].id"  : "items",
   "orderId": "orders",
   "companyId":"employees"
}

def to_object_id(value):
    try:
        return ObjectId(value)
    except:
        return None
    
def resolve_references_once(document):
    resolved_doc = {}
    for key, value in document.items():
        if isinstance(value, ObjectId) and key in reference_mapping:
            ref_collection = reference_mapping[key]
            ref_doc = db[ref_collection].find_one({'_id': value})
            if ref_doc:
                ref_doc.pop('_id', None)
                # cleaned = {k: v for k, v in ref_doc.items() if not isinstance(v, ObjectId)}
                cleaned = {
                            k: [
                                {
                                    ik: iv for ik, iv in item.items()
                                    if not (isinstance(iv, ObjectId) or (isinstance(iv, str) and to_object_id(iv) is not None))
                                } if isinstance(item, dict) else item
                                for item in v
                            ] if isinstance(v, list) else v
                            for k, v in ref_doc.items()
                            if not (
                                isinstance(v, ObjectId) or
                                (isinstance(v, str) and to_object_id(v) is not None)
                            )}

                resolved_doc[key] = cleaned
        
        elif isinstance(value, list) and key in reference_mapping:
            
            ref_collection = reference_mapping[key]
            resolved_list = []
            for item in value:
                obj_id = item if isinstance(item, ObjectId) else to_object_id(item)
                if isinstance(obj_id, ObjectId):
                    ref_doc = db[ref_collection].find_one({'_id': item})
                    if ref_doc:
                        ref_doc.pop('_id', None)
                        cleaned = {k: v for k, v in ref_doc.items() if not isinstance(v, ObjectId)}
                        resolved_list.append(cleaned)
                else:
                    resolved_list.append(item)
            resolved_doc[key] = resolved_list        
        
        elif isinstance(value, list):
            resolved_items = []
            for item in value:
                if isinstance(item, dict):
                    item_copy = item.copy()
                    for nested_key, ref_collection in reference_mapping.items():
                        if nested_key.startswith(f"{key}[]."):
                            nested_field = nested_key.split("[].")[1]
                            id_val = item.get(nested_field)

                            obj_id = to_object_id(id_val)

                            if isinstance(obj_id, ObjectId):
                                ref_doc = db[ref_collection].find_one({'_id': obj_id})
                                if ref_doc:
                                    ref_doc.pop('_id', None)
                                    cleaned = {k: v for k, v in ref_doc.items() if not isinstance(v, ObjectId) and not (isinstance(v, list) and all(isinstance(i, ObjectId) for i in v))}
                                    item_copy[nested_field] = cleaned
                    resolved_items.append(item_copy)
                else:
                    resolved_items.append(item)
            resolved_doc[key] = resolved_items

        else:
            resolved_doc[key] = value
        
    return resolved_doc

def load_documents():
    all_data = []
    for name in db.list_collection_names():
        for doc in db[name].find({}):
            doc["_collection"] = name
            resolved = resolve_references_once(doc)
            all_data.append(resolved)
    return all_data
