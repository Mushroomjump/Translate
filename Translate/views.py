from django.shortcuts import render, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId

# Setup MongoDB connection
connection_string = "mongodb+srv://sbp1784:OBbxnqbZowezp2qX@iwazolab.sksu1fm.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client["fintech"]
originals_collection = db["rawData"]
translations_collection = db["translations"]


def index(request):
    if 'current_id' not in request.session:
        first_document = originals_collection.find_one({}, {'_id': 1})
        request.session['current_id'] = str(first_document['_id']) if first_document else None

    current_id = request.session.get('current_id')
    original = originals_collection.find_one({'_id': ObjectId(current_id)}) if current_id else None

    # Convert ObjectId to string and assign to a new key
    if original:
        original['id_str'] = str(original['_id'])

    return render(request, "index.html", {'original': original})


def navigate(request):
    if request.method == 'POST':
        direction = request.POST.get("direction")
        current_id = ObjectId(request.session['current_id'])
        new_entry = None

        if direction == "next":
            cursor = originals_collection.find({'_id': {'$gt': current_id}}).sort('_id', 1).limit(1)
            new_entry = next(cursor, None)
        elif direction == "prev":
            cursor = originals_collection.find({'_id': {'$lt': current_id}}).sort('_id', -1).limit(1)
            new_entry = next(cursor, None)

        if new_entry:
            request.session['current_id'] = str(new_entry['_id'])
    return redirect('/')

def translate(request):
    if request.method == 'POST':
        original_id = request.POST.get("original_id")
        translation_text = request.POST.get("translation")
        translations_collection.insert_one({"original_id": original_id, "translation": translation_text})
    return redirect('/')
