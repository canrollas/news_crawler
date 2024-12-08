from flask import Flask, request, jsonify, render_template
from functools import wraps
import pymongo
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
MONGO_URI = os.getenv('MONGODB_URI', "mongodb://root:example@mongodb:27017/")
API_TOKEN = os.getenv('API_TOKEN')  # Load from environment variable
DEFAULT_LIMIT = 10
MAX_LIMIT = 100

# MongoDB connection
client = pymongo.MongoClient(MONGO_URI)
db = client['news_db']

def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token.split(' ')[-1] != API_TOKEN:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def paginate_results(collection, query=None, sort_by=None):
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', DEFAULT_LIMIT)), MAX_LIMIT)
    offset = (page - 1) * limit

    # Base query
    if query is None:
        query = {}

    # Get total count
    total = collection.count_documents(query)

    # Execute query with pagination
    cursor = collection.find(query)
    
    # Apply sorting if specified
    if sort_by:
        cursor = cursor.sort(sort_by)
    
    # Apply pagination
    cursor = cursor.skip(offset).limit(limit)

    # Convert results to list
    results = list(cursor)
    
    # Convert ObjectId to string for JSON serialization
    for result in results:
        result['_id'] = str(result['_id'])

    return {
        'total': total,
        'page': page,
        'limit': limit,
        'offset': offset,
        'data': results
    }

@app.route('/')
def home():
    # Calculate statistics
    stats = {
        'total_articles': 0,
        'sources_count': 4,  # CNN, El País, Le Monde, Der Spiegel
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    }
    
    # Count total articles
    collections = ['spiegel', 'elpais', 'lemonde', 'cnn']
    for collection_name in collections:
        try:
            collection = db[collection_name]
            stats['total_articles'] += collection.count_documents({})
        except Exception as e:
            app.logger.error(f"Error counting documents in {collection_name}: {str(e)}")
    
    return render_template('index.html', stats=stats)

@app.route('/api/news/german', methods=['GET'])
@require_token
def get_german_news():
    collection = db['spiegel']
    return jsonify(paginate_results(collection, sort_by=[('published_date', -1)]))

@app.route('/api/news/spanish', methods=['GET'])
@require_token
def get_spanish_news():
    collection = db['elpais']
    return jsonify(paginate_results(collection, sort_by=[('published_date', -1)]))

@app.route('/api/news/english', methods=['GET'])
@require_token
def get_english_news():
    collection = db['cnn']
    return jsonify(paginate_results(collection, sort_by=[('published_date', -1)]))  

@app.route('/api/news/french', methods=['GET'])
@require_token
def get_french_news():
    collection = db['lemonde']
    return jsonify(paginate_results(collection, sort_by=[('published_date', -1)]))

@app.route('/api/news/search', methods=['GET'])
@require_token
def search_news():
    keyword = request.args.get('q', '')
    if not keyword:
        return jsonify({'error': 'Search query is required'}), 400

    # Search across all collections
    collections = ['spiegel', 'elpais', 'lemonde', 'cnn']
    results = []
    total = 0

    query = {
        '$or': [
            {'title': {'$regex': keyword, '$options': 'i'}},
            {'content': {'$regex': keyword, '$options': 'i'}}
        ]
    }

    for collection_name in collections:
        collection = db[collection_name]
        collection_results = paginate_results(collection, query)
        total += collection_results['total']
        results.extend(collection_results['data'])

    # Sort combined results by date
    results.sort(key=lambda x: x.get('published_date', ''), reverse=True)

    # Apply pagination to combined results
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', DEFAULT_LIMIT)), MAX_LIMIT)
    offset = (page - 1) * limit
    
    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'offset': offset,
        'data': results[offset:offset+limit]
    })

@app.route('/api/news/recent', methods=['GET'])
@require_token
def get_recent_news():
    try:
        results = []
        total = 0

        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', DEFAULT_LIMIT)), MAX_LIMIT)
        offset = (page - 1) * limit

        # Query each collection for most recent items
        for collection_name in ['spiegel', 'elpais', 'lemonde', 'cnn']:
            try:
                collection = db[collection_name]
                # Get most recent items from each collection
                collection_results = collection.find().sort('datePublished', -1).limit(limit)
                # Convert MongoDB documents to dictionaries and handle ObjectId
                for doc in collection_results:
                    doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
                    results.append(doc)
                total += collection.count_documents({})
            except Exception as e:
                app.logger.error(f"Error querying collection {collection_name}: {str(e)}")
                continue

        # Sort all results by date
        results.sort(key=lambda x: x.get('datePublished', ''), reverse=True)

        # Apply pagination to combined results
        paginated_results = results[offset:offset+limit]

        return jsonify({
            'total': total,
            'page': page, 
            'limit': limit,
            'offset': offset,
            'data': paginated_results
        })

    except Exception as e:
        app.logger.error(f"Error in get_recent_news: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)