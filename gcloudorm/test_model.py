import unittest2

class TestModel(unittest2.TestCase):
    def testModel(self):
        import model
        import key

        # key name
        m = model.Model(id='bar')
        self.assertEqual(m.key().name(), 'bar')
        self.assertEqual(m.key().kind(), 'Model')

        p = key.Key('ParentModel', 'foo')

        # key name + parent
        m = model.Model(id='bar', parent=p)
        self.assertEqual(m.key().path(), key.Key(flat=('ParentModel', 'foo', 'Model', 'bar')).path())

        # key id
        m = model.Model(id=42)
        self.assertEqual(m.key().id(), 42)

        # key id + parent
        m = model.Model(id=42, parent=p)
        self.assertEqual(m.key().path(), key.Key(flat=('ParentModel', 'foo', 'Model', 42)).path())

        # parent
        m = model.Model(parent=p)
        self.assertEqual(m.key().path(), key.Key(flat=('ParentModel', 'foo', 'Model', None)).path())

    def testBooleanProperty(self):
        import model

        class TestModel(model.Model):
            test_bool = model.BooleanProperty()

        m = TestModel()
        self.assertEqual(m.test_bool, None)
        self.assertEqual(m['test_bool'], None)

        m = TestModel(test_bool=False)
        self.assertEqual(m.test_bool, False)
        self.assertEqual(m['test_bool'], False)

        m.test_bool = True
        self.assertEqual(m.test_bool, True)
        self.assertEqual(m['test_bool'], True)

        class TestModel(model.Model):
            test_bool = model.BooleanProperty(default=True)

        m = TestModel()
        self.assertEqual(m.test_bool, True)
        self.assertEqual(m['test_bool'], True)

    def testIntegerProperty(self):
        import model

        class TestModel(model.Model):
            test_int = model.IntegerProperty()

        m = TestModel()
        self.assertEqual(m.test_int, None)
        self.assertEqual(m['test_int'], None)

        class TestModel(model.Model):
            test_int = model.IntegerProperty(default=3)

        m = TestModel()
        self.assertEqual(m['test_int'], 3)

        m.test_int = 4
        self.assertEqual(m.test_int, 4)
        self.assertEqual(m['test_int'], 4)

    def testFloatproperty(self):
        import model

        class TestModel(model.Model):
            test_float = model.FloatProperty()

        m = TestModel()
        self.assertEqual(m.test_float, None)
        self.assertEqual(m['test_float'], None)

        class TestModel(model.Model):
            test_float = model.FloatProperty(default=0.1)

        m = TestModel()
        self.assertEqual(m['test_float'], 0.1)

        m.test_float = 0.2
        self.assertEqual(m['test_float'], 0.2)

    def testTextProperty(self):
        import model

        class TestModel(model.Model):
            test_text = model.TextProperty()

        m = TestModel()
        self.assertEqual(m.test_text, None)


        class TestModel(model.Model):
            test_text = model.TextProperty(default="")

        m = TestModel()
        self.assertEqual(m['test_text'], "")


    def testStringProperty(self):
        import model

        class TestModel(model.Model):
            test_str = model.StringProperty()

        m = TestModel()
        self.assertEqual(m.test_str, None)
        m.test_str = '123'

        self.assertEqual(m['test_str'], '123')


    def testPickleProperty(self):
        import model

        class TestModel(model.Model):
            test_pickle = model.PickleProperty()

        m = TestModel()
        self.assertEqual(m.test_pickle, None)
        m = TestModel(test_pickle={"123": "456"})
        self.assertEqual(m.test_pickle, {"123": "456"})

        m.test_pickle = {'456': '789'}
        self.assertEqual(m.test_pickle, {'456': '789'})

    def testJsonProperty(self):
        import model

        class TestModel(model.Model):
            test_pickle = model.JsonProperty()

        m = TestModel()
        self.assertEqual(m.test_pickle, None)
        m = TestModel(test_pickle={"123": "456"})
        self.assertEqual(m.test_pickle, {"123": "456"})

        m.test_pickle = {'456': '789'}
        self.assertEqual(m.test_pickle, {'456': '789'})


    def testDataTimeProperty(self):
        import model
        import datetime

        class TestModel(model.Model):
            test_datetime = model.DateTimeProperty()

        m = TestModel()
        self.assertEqual(m.test_datetime, None)

        utcnow = datetime.datetime.utcnow()
        m.test_datetime = utcnow
        self.assertEqual(m.test_datetime, utcnow)


    def testDateProperty(self):
        import model
        import datetime

        class TestModel(model.Model):
            test_date = model.DateProperty()

        m = TestModel()
        self.assertEqual(m.test_date, None)

        today = datetime.date.today()
        m.test_date = today
        self.assertEqual(m.test_date, today)

    def testTimeProperty(self):
        import model
        import datetime

        class TestModel(model.Model):
            test_time = model.TimeProperty()

        m = TestModel()
        self.assertEqual(m.test_time, None)

        t = datetime.time()
        m.test_time = t

        self.assertEqual(m.test_time, t)

    def testInsert(self):
        import model

        connection = _Connection()
        transaction = connection._transaction = _Transaction()
        dataset = _Dataset(connection)
        key = _Key()

        model.Model.dataset = dataset

        class TestModel(model.Model):
            test_value = model.StringProperty()

        entity = TestModel(id=1)
        entity.key(key)
        entity.test_value = '123'
        entity.put()

        self.assertEqual(entity['test_value'], '123')
        self.assertEqual(connection._saved,
                         (_DATASET_ID, 'KEY', {'test_value': '123'}, ()))
        self.assertEqual(key._path, None)


_MARKER = object()
_DATASET_ID = 'DATASET'
_KIND = 'KIND'
_ID = 1234



class _Key(object):
    _MARKER = object()
    _key = 'KEY'
    _partial = False
    _path = None

    def to_protobuf(self):
        return self._key

    def is_partial(self):
        return self._partial

    def path(self, path=_MARKER):
        if path is self._MARKER:
            return self._path
        self._path = path


class _Dataset(dict):

    def __init__(self, connection=None):
        super(_Dataset, self).__init__()
        self._connection = connection

    def id(self):
        return _DATASET_ID

    def connection(self):
        return self._connection

    def get_entity(self, key):
        return self.get(key)


class _Connection(object):
    _transaction = _saved = _deleted = None
    _save_result = True

    def transaction(self):
        return self._transaction

    def save_entity(self, dataset_id, key_pb, properties,
                    exclude_from_indexes=()):
        self._saved = (dataset_id, key_pb, properties,
                       tuple(exclude_from_indexes))
        return self._save_result

    def delete_entities(self, dataset_id, key_pbs):
        self._deleted = (dataset_id, key_pbs)


class _Transaction(object):
    _added = ()

    def __nonzero__(self):
        return True
    __bool__ = __nonzero__

    def add_auto_id_entity(self, entity):
        self._added += (entity,)
