import base64
import json
import os
from datetime import datetime
from enum import Enum

import firebase_admin
from firebase_admin import credentials, firestore

from artist import ARTIST


class Firebase:
    def __init__(self):
        certificate = credentials.Certificate(self.base64_decode(os.environ["FIREBASE_ADMIN_KEY"]))
        firebase_admin.initialize_app(certificate)
        self.__db = firestore.client()

    def get_updated_at(self, artist: ARTIST):
        doc_ref = self.__db.collection("artist").document(artist.value)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()['updated_at']
        else:
            return None

    def set_updated_at(self, artist: ARTIST, updated_at: datetime):
        doc_ref = self.__db.collection("artist").document(artist.value)
        doc_ref.set({
            "updated_at": updated_at
        })

    def base64_decode(self, key) -> dict:
        decoded_bytes = base64.b64decode(key)
        decoded_string = decoded_bytes.decode('utf-8')
        return json.loads(decoded_string)
