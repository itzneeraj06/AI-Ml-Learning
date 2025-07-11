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

def get_collection_counts():
    collection_counts = {}
    for name in db.list_collection_names():
        count = db[name].count_documents({})
        collection_counts[name] = count
    return collection_counts

def get_customer_details():
    customerDetails = []
    for customer in db["customers"].find({}, {"email": 1,"phone":1,"_id": 0}):
        name = customer.get("email", "Unknown")
        phone = customer.get("phone", "N/A")
        
        customerDetails.append(f"{name}: {phone}")
    return customerDetails

def get_employee_details():
    employeeDetails = []
    for customer in db["employees"].find({}, {"firstName": 1,"lastName":1,"phoneNumber":1,"email":1,"_id": 0}):
        email = customer.get("email", "Unknown")
        phone = customer.get("phone", "N/A")
        firstName = customer.get("firstName", "")
        lastName = customer.get("lastName", "")
        
        employeeDetails.append(f"{firstName}{lastName}({email}): {phone}")
    return employeeDetails

def get_item_details():
    details = []
    for customer in db["items"].find({}, {"name": 1,"price":1,"_id": 0}):
        name = customer.get("name", "Unknown")
        price = customer.get("price", "N/A")
        
        details.append(f"{name}: {price}")
    return details

def get_order_details():
    details = []
    for customer in db["orders"].find({}, {"customerId": 1,"totalPrice":1,"createdAt":1,"_id": 0}):
        customerId = customer.get("customerId", "Unknown")
        if customerId:
            custom = db["customers"].find_one({"_id": customerId}, {"phone": 1})
            if custom:
                name = custom.get("phone", "Unknown")
        price = customer.get("totalPrice", "N/A")
        date = customer.get("createdAt", "N/A")
        details.append(f"Customer Details:{name}(Order Date:{date}): ₹{price}")
    return details

def get_report_details():
    total_sales = 0
    total_cost = 0

    orders = db["orders"].find({}, {"totalPrice": 1, "items": 1, "_id": 0})
    
    for order in orders:
        price = order.get("totalPrice", 0)
        if price is None:
            price = 0
        total_sales += price

        items = order.get("items", [])
        order_cost = 0
        for item in items:
            cost = item.get("cost", 0)
            quantity = item.get("quantity", 1)
            
            try:
                cost = float(cost)
            except:
                cost = 0

            try:
                quantity = int(quantity)
            except:
                quantity = 1

            order_cost += cost * quantity

        total_cost += order_cost

    total_profit = total_sales - total_cost

    return {
        "totalSales": total_sales,
        "totalCost": total_cost,
        "totalProfit": total_profit
    }

def get_datewise_full_report():
    pipeline = [
        {
            "$lookup": {
                "from": "customers",
                "localField": "customerId",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$unwind": {
                "path": "$customer",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "date": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$createdAt"
                    }
                },
                "totalPrice": 1,
                "customerPhone": "$customer.phone"
            }
        },
        {
            "$group": {
                "_id": "$date",
                "totalSales": {"$sum": "$totalPrice"},
                "orderCount": {"$sum": 1},
                "minOrder": {"$min": "$totalPrice"},
                "maxOrder": {"$max": "$totalPrice"},
                "avgOrder": {"$avg": "$totalPrice"},
                "customers": {"$addToSet": "$customerPhone"}
            }
        },
        {"$sort": {"_id": -1}}
    ]
    
    results = list(db["orders"].aggregate(pipeline))
    
    # Clean output
    report = []
    for doc in results:
        report.append({
            "date": doc["_id"],
            "orderCount": doc["orderCount"],
            "totalSales": doc["totalSales"],
            "minOrder": doc["minOrder"],
            "maxOrder": doc["maxOrder"],
            "avgOrder": round(doc["avgOrder"], 2),
            "customers": doc.get("customers", [])
        })
    return report

def get_monthwise_full_report():
    pipeline = [
        {
            "$lookup": {
                "from": "customers",
                "localField": "customerId",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$unwind": {
                "path": "$customer",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "month": {
                    "$dateToString": {
                        "format": "%Y-%m",
                        "date": "$createdAt"
                    }
                },
                "totalPrice": 1,
                "customerPhone": "$customer.phone"
            }
        },
        {
            "$group": {
                "_id": "$month",
                "totalSales": {"$sum": "$totalPrice"},
                "orderCount": {"$sum": 1},
                "minOrder": {"$min": "$totalPrice"},
                "maxOrder": {"$max": "$totalPrice"},
                "avgOrder": {"$avg": "$totalPrice"},
                "customers": {"$addToSet": "$customerPhone"}
            }
        },
        {"$sort": {"_id": -1}}
    ]

    results = list(db["orders"].aggregate(pipeline))

    report = []
    for doc in results:
        report.append({
            "month": doc["_id"],
            "orderCount": doc["orderCount"],
            "totalSales": doc["totalSales"],
            "minOrder": doc["minOrder"],
            "maxOrder": doc["maxOrder"],
            "avgOrder": round(doc["avgOrder"], 2),
            "customers": doc.get("customers", [])
        })
    return report

def get_yearwise_full_report():
    pipeline = [
        {
            "$lookup": {
                "from": "customers",
                "localField": "customerId",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {
            "$unwind": {
                "path": "$customer",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "year": {
                    "$dateToString": {
                        "format": "%Y",
                        "date": "$createdAt"
                    }
                },
                "totalPrice": 1,
                "customerPhone": "$customer.phone"
            }
        },
        {
            "$group": {
                "_id": "$year",
                "totalSales": {"$sum": "$totalPrice"},
                "orderCount": {"$sum": 1},
                "minOrder": {"$min": "$totalPrice"},
                "maxOrder": {"$max": "$totalPrice"},
                "avgOrder": {"$avg": "$totalPrice"},
                "customers": {"$addToSet": "$customerPhone"}
            }
        },
        {"$sort": {"_id": -1}}
    ]

    results = list(db["orders"].aggregate(pipeline))

    report = []
    for doc in results:
        report.append({
            "year": doc["_id"],
            "orderCount": doc["orderCount"],
            "totalSales": doc["totalSales"],
            "minOrder": doc["minOrder"],
            "maxOrder": doc["maxOrder"],
            "avgOrder": round(doc["avgOrder"], 2),
            "customers": doc.get("customers", [])
        })
    return report

def load_documents():
    all_data = []
    count=get_collection_counts()
    mail=get_customer_details()
    employee=get_employee_details()
    item=get_item_details()
    order=get_order_details()
    report=get_report_details()
    reportDate=get_datewise_full_report()
    reportMonth=get_monthwise_full_report()
    reportYear=get_yearwise_full_report()
    all_data.append(f"total count of all collections/tables like orders,items etc {count}")
    all_data.append(f"customer details {mail}")
    all_data.append(f"employees details {employee}")
    all_data.append(f"items/product details {item}")
    all_data.append(f"total order details {order}")
    all_data.append(f"total sales ₹{report}")
    all_data.append(f"daily sales/order report {reportDate}")
    all_data.append(f"monthly sales/order report {reportMonth}")
    all_data.append(f"yearly sales/order report {reportYear}")
    
    # collections=['invoices', 'items', 'kitchens', 'blockedroles', 'payments', 'employees', 'modifiers', 'ingredients', 'orders', 'customers', 'expensetypes', 'categories', 'expenses', 'tables']
    collections=['orders','items','customers','employees', 'modifiers', 'ingredients','expensetypes', 'categories', 'expenses', 'tables']
    
    # for name in db.list_collection_names():
    for name in collections:
        for doc in db[name].find({}):
            doc["_collection"] = name
            resolved = resolve_references_once(doc)
            all_data.append(resolved)
    return all_data
