#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
dLNk Production API

This module provides a RESTful API for managing links, designed for serverless deployment.
It includes basic CRUD operations with error handling, logging, and clear documentation.
"""

import logging
import uuid

from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

# In-memory data store to simulate a database-as-a-service
links_db = {}

@app.errorhandler(404)
def not_found(error):
    """Handles 404 Not Found errors with a JSON response."""
    logging.warning(f"404 Not Found: {request.path}")
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(400)
def bad_request(error):
    """Handles 400 Bad Request errors with a JSON response."""
    logging.error(f"400 Bad Request: {error.description}")
    return jsonify({"error": error.description}), 400

@app.route("/links", methods=["POST"])
def create_link():
    """Creates a new link.

    Expects a JSON payload with a "url" key.
    Returns the created link object.
    """
    if not request.json or "url" not in request.json:
        return bad_request(type("BadRequest", (), {"description": "Missing url in request body"})())

    link_id = str(uuid.uuid4())
    link = {"id": link_id, "url": request.json["url"]}
    links_db[link_id] = link

    logging.info(f"Link created: {link_id}")
    return jsonify(link), 201

@app.route("/links/<string:link_id>", methods=["GET"])
def get_link(link_id):
    """Retrieves a single link by its ID."""
    link = links_db.get(link_id)
    if link is None:
        return not_found(None)

    logging.info(f"Link retrieved: {link_id}")
    return jsonify(link)

@app.route("/links", methods=["GET"])
def get_all_links():
    """Retrieves all links."""
    logging.info("All links retrieved")
    return jsonify(list(links_db.values()))

@app.route("/links/<string:link_id>", methods=["PUT"])
def update_link(link_id):
    """Updates an existing link.

    Expects a JSON payload with a "url" key.
    """
    if not request.json or "url" not in request.json:
        return bad_request(type("BadRequest", (), {"description": "Missing url in request body"})())

    link = links_db.get(link_id)
    if link is None:
        return not_found(None)

    link["url"] = request.json["url"]
    links_db[link_id] = link

    logging.info(f"Link updated: {link_id}")
    return jsonify(link)

@app.route("/links/<string:link_id>", methods=["DELETE"])
def delete_link(link_id):
    """Deletes a link by its ID."""
    if link_id not in links_db:
        return not_found(None)

    del links_db[link_id]

    logging.info(f"Link deleted: {link_id}")
    return "", 204

if __name__ == "__main__":
    # This block is for local testing and will not be used in a serverless environment
    app.run(debug=True)
