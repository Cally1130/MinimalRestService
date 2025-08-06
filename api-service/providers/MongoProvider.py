import json
import os
import pymongo
from bson import ObjectId
from bson.json_util import dumps
from flask import jsonify


class JSONEncoder(json.JSONEncoder):
	"""
	Extend JSON Encoder to support mongoDB id encoding
	"""
	def default(self, o):
		if isinstance(o, ObjectId):
			return str(o)
		return json.JSONEncoder.default(self, o)


class MongoProvider(object):

	def __init__(self):
		"""
		Create the connection with mongoDB
		"""
		# mongodb_uri = os.getenv('MONGODB_URI', default='mongodb://localhost:27017/')

		self.myclient = pymongo.MongoClient(f"mongodb://{os.environ.get('MONGO_URL', 'localhost')}:{os.environ.get('MONGO_PORT', 27017)}/")
		
		# Test the connection
		try:
			self.myclient.server_info()
			print("✅ Connected to MongoDB successfully!")
		except pymongo.errors.ServerSelectionTimeoutError as e:
			print(f"❌ Failed to connect to MongoDB: {e}")
			raise e
		
		self.mydb = self.myclient["team"]
		self.mycollection = self.mydb["user"]


	def create_user(self, newUser):
		self.mycollection.insert_one(newUser)
		return json.loads(JSONEncoder().encode(newUser)), 201

	def read_user(self, user_id):
		
		if user:
			user = JSONEncoder().encode(user)
			return json.loads(user), 200
		else:
			return {"error": "no documents found"}, 404
		
	def read_all_startup_logs(self):
		logs = self.mycollection.find({})
		logs_list = list(logs)
		print(logs_list)
		
		# Use dumps and parse back to dict for consistent return format
		json_string = dumps(logs_list)
		logs_dict = json.loads(json_string)
		return {"logs": logs_dict}, 200

	def update_user(self, payload):
		"""
		Update a user with the information provided in the payload
		:param payload: dict
			Dictionary passed as input
		:return: (dict, int)
			Response JSON, Error code
		"""
		if self.mycollection.count_documents({'id': payload['id']}, limit=1) != 0: # Check if user exists in DB
			print("Found a user in DB with this id")
			user_query = {"id": payload['id']}
			new_values = {"$set": payload}

			x = self.mycollection.update_one(user_query, new_values)
			if x.modified_count != 0:
				return {"message": "Success"}, 201
			else:
				return {"error": "user not modified"}, 403
		else:
			# user not found
			return {"error": "user not found"}, 409

	def delete_user(self, user_id):
		"""
		Delete a user from the database given its id
		:param user_id: int
			Id of the user
		:return: (dict, int)
			Response JSON, Error code
		"""
		user_query = {"id": user_id}
		x = self.mycollection.delete_one(user_query)
		if x.deleted_count != 0:
			return {"message": "Success"}, 200

		else:
			return {"error": "user not found"}, 400
