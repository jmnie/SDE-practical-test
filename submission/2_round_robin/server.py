from typing import List, Dict, Optional
from datetime import datetime
import pymysql
from pymysql.cursors import DictCursor
from dataclasses import dataclass, asdict
import redis
from elasticsearch import Elasticsearch
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Database connection configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "g2g_marketplace",
    "cursorclass": DictCursor
}

# Redis configuration
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Elasticsearch configuration
es_client = Elasticsearch(['http://localhost:9200'])

@dataclass
class ListingDTO:
    id: int
    seller_id: int
    title: str
    price: float
    rank_score: float

class DatabaseManager:
    def __init__(self):
        self.db_config = db_config

    def get_connection(self):
        """Establish a new database connection."""
        return pymysql.connect(**self.db_config)

    def execute_query(self, query, params=None):
        """Execute a query and return the results."""
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                return results
        finally:
            connection.close()

class RoundRobinListingService:
    def __init__(self):
        self.db = DatabaseManager()
        self.redis = redis_client
        self.es = es_client
        self.page_size = 20

    def get_active_sellers(self, category_id: int, filters: Optional[Dict]) -> List[int]:
        """Retrieve active seller IDs using raw SQL."""
        query = """
        SELECT DISTINCT seller_id 
        FROM listings 
        WHERE category_id = %s 
        AND status = 'active'
        """
        params = [category_id]

        if filters:
            if 'price_min' in filters:
                query += " AND price >= %s"
                params.append(filters['price_min'])
            if 'price_max' in filters:
                query += " AND price <= %s"
                params.append(filters['price_max'])

        results = self.db.execute_query(query, params)
        return [row['seller_id'] for row in results]

    def get_listings(self, category_id: int, page: int = 1, 
                    filters: Dict = None, sort_by: str = "rank_score",
                    sort_order: str = "desc") -> List[ListingDTO]:
        """Retrieve listings in a round-robin sequence."""
        # Generate cache key
        cache_key = f"listings:{category_id}:{page}:{sort_by}:{sort_order}:{json.dumps(filters or {})}"
        
        # Attempt to retrieve from cache
        cached_results = self.redis.get(cache_key)
        if cached_results:
            return [ListingDTO(**item) for item in json.loads(cached_results)]

        # Retrieve active sellers
        seller_ids = self.get_active_sellers(category_id, filters)
        if not seller_ids:
            return []

        # Build Elasticsearch query
        es_query = self._build_es_query(category_id, seller_ids, filters, sort_by, sort_order)
        
        # Calculate pagination
        offset = (page - 1) * self.page_size
        
        # Execute Elasticsearch query
        es_results = self.es.search(
            index="listings",
            body=es_query,
            size=self.page_size,
            from_=offset
        )

        # Transform results to round-robin order
        listings = self._transform_to_round_robin(es_results)
        
        # Cache the results
        self.redis.setex(cache_key, 300, json.dumps([asdict(l) for l in listings]))
        
        return listings

    def _build_es_query(self, category_id: int, seller_ids: List[int], 
                       filters: Dict, sort_by: str, sort_order: str) -> Dict:
        """Build the Elasticsearch query."""
        must_conditions = [
            {"term": {"category_id": category_id}},
            {"terms": {"seller_id": seller_ids}},
            {"term": {"status": "active"}}
        ]
        
        if filters:
            if 'price_min' in filters:
                must_conditions.append({"range": {"price": {"gte": filters['price_min']}}})
            if 'price_max' in filters:
                must_conditions.append({"range": {"price": {"lte": filters['price_max']}}})

        return {
            "query": {
                "bool": {
                    "must": must_conditions
                }
            },
            "sort": [
                {"seller_id": "asc"},
                {sort_by: {"order": sort_order}}
            ]
        }

    def _transform_to_round_robin(self, es_results) -> List[ListingDTO]:
        """Transform Elasticsearch results to round-robin order."""
        seller_listings: Dict[int, List[ListingDTO]] = {}
        
        for hit in es_results['hits']['hits']:
            source = hit['_source']
            listing = ListingDTO(
                id=source['id'],
                seller_id=source['seller_id'],
                title=source['title'],
                price=float(source['price']),
                rank_score=float(source['rank_score'])
            )
            
            if source['seller_id'] not in seller_listings:
                seller_listings[source['seller_id']] = []
            seller_listings[source['seller_id']].append(listing)

        result = []
        max_listings_per_seller = max(len(listings) for listings in seller_listings.values())
        
        for i in range(max_listings_per_seller):
            for seller_id in sorted(seller_listings.keys()):
                if i < len(seller_listings[seller_id]):
                    result.append(seller_listings[seller_id][i])
                    
                if len(result) >= self.page_size:
                    return result

        return result

# Flask route
@app.route('/api/listings', methods=['GET'])
def get_listings():
    try:
        # Parse query parameters
        category_id = int(request.args.get('category_id', 1))
        page = int(request.args.get('page', 1))
        sort_by = request.args.get('sort_by', 'rank_score')
        sort_order = request.args.get('sort_order', 'desc')

        # Handle filter conditions
        filters = {}
        if request.args.get('price_min'):
            filters['price_min'] = float(request.args.get('price_min'))
        if request.args.get('price_max'):
            filters['price_max'] = float(request.args.get('price_max'))

        # Initialize the service and retrieve listings
        service = RoundRobinListingService()
        listings = service.get_listings(
            category_id=category_id,
            page=page,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # Return success response
        return jsonify({
            'status': 'success',
            'data': [asdict(listing) for listing in listings],
            'page': page,
            'page_size': service.page_size
        })

    except ValueError as ve:
        # Handle invalid input
        return jsonify({
            'status': 'error',
            'message': f"Invalid input: {str(ve)}"
        }), 400

    except Exception as e:
        # Handle general errors
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Flask application entry point
if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)
