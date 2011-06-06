from django.test import TestCase

from backend import SessionStore
from mock import Mock
from redis import Redis
import cPickle
import timeit

class RedisTests(TestCase):
    def setUp(self):
        self.sessionStore = SessionStore()
        self.mock_redis = Mock(Redis)
        # default exists to false
        self.mock_redis.exists.return_value = False
        self.sessionStore._redis = self.mock_redis

    def test_exists_false(self):
        self.assertFalse(self.sessionStore.exists('abc'))
        self.assertTrue(self.mock_redis.exists.called)

    def test_exists_true(self):
        self.mock_redis.exists.return_value = True
        self.assertTrue(self.sessionStore.exists('abc'))
        self.assertTrue(self.mock_redis.exists.called)

    def test_load_non_existent(self):
        self.mock_redis.get.return_value = None
        self.assertEquals({}, self.sessionStore.load())
        self.assertTrue(self.mock_redis.setnx.called)
        self.assertFalse(self.mock_redis.set.called)

    def test_load_exists(self):
        self.sessionStore.session_key = 'abc'
        data = {'a':1}
        self.mock_redis.get.return_value = cPickle.dumps(data)
        self.assertEquals(data, self.sessionStore.load())

    def test_save(self):
        self.sessionStore.session_key = 'abc'
        self.mock_redis.get.return_value = cPickle.dumps({})
        self.sessionStore['key'] = 'val'
        self.sessionStore.save()
        self.mock_redis.set.assert_called_once_with(
            self.sessionStore.session_key, cPickle.dumps({'key':'val'}))

    def test_performance_of_redis_connection_setup(self):
        def new_session_store():
            SessionStore()
        def new_session_store_used():
            SessionStore().exists('abc')

        t1 = timeit.timeit(new_session_store, 'gc.enable()', number=10000)
        t2 = timeit.timeit(new_session_store_used, 'gc.enable()', number=10000)
        print '10,000 instantiations without op: %ss' % t1
        print '10,000 instantiations with exists() op: %ss' % t2
