## 1. High-Level Architecture
The system architecture comprises the following components:

Database Layer: Stores all offer listings, seller information, and related metadata.
Application Layer: Contains the business logic for processing requests, applying filters, sorting, and implementing the round-robin distribution.
API Layer: Exposes endpoints for clients to retrieve listings with the desired filters and sorting options.
Caching Layer: Utilizes caching mechanisms to store frequently accessed data and reduce database load.


## 2. Database Schema
The database schema comprises the following tables:

`sellers`: Stores information about sellers, including their ratings, status (active, inactive, or suspended), and timestamps for creation and updates.

`categories`: Maintains the hierarchical structure of item categories, with fields for parent category references, display order, status (active or inactive), and timestamps.

`offers`: Contains listings of items offered by sellers, detailing the seller and category associations, item descriptions, pricing, status (active, inactive, sold, or suspended), engagement metrics (view and sale counts), a rank score for sorting purposes, and timestamps.


## 3. Round-Robin Display Implementation
To implement a round-robin display of offers, the system follows these steps:

`Retrieve Active Sellers`: Execute a SQL query to obtain a list of active sellers within the specified category, applying any provided filters such as price range.

`Fetch Offers`: Construct an Elasticsearch query to retrieve offers from these sellers, incorporating the desired filters and sorting criteria.

`Interleave Offers`: Organize the retrieved offers in a round-robin sequence by interleaving listings from different sellers, ensuring an even distribution across the listing pages.