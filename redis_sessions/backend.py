from django.contrib.sessions.backends.base import SessionBase, CreateError
from tmi.redis_sessions import redis_client

import cPickle

class SessionStore(SessionBase):
    """
    A session store using Redis for storage
    """
    def __init__(self, session_key=None):
        self._redis = redis_client
        super(SessionStore, self).__init__(session_key)

    def load(self):
        pickled_session_data = self._redis.get(self.session_key)
        if pickled_session_data is not None:
            return cPickle.loads(pickled_session_data)
        self.create()
        return {}

    def create(self):
        self.session_key = self._get_new_session_key()
        try:
            self.save(must_create=True)
        except CreateError:
            raise RuntimeError('unable to create session')
        self.modified = True
        return

    def save(self, must_create=False):
        pickled_data = cPickle.dumps(self._get_session(no_load=must_create))
        if must_create:
            func = self._redis.setnx
        else:
            func = self._redis.set
        result = func(self.session_key, pickled_data)
        if must_create and not result:
            raise CreateError
        self._redis.expire(self.session_key, self.get_expiry_age())

    def exists(self, session_key):
        if self._redis.exists(session_key):
            return True
        return False

    def delete(self, session_key=None):
        if session_key is None:
            if self._session_key is None:
                return
            session_key = self._session_key
        self._redis.delete(session_key)

