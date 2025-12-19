# repositories/base_repository.py

class BaseRepository:

    def __init__(self, model):
        self.model = model

    def get_all(self):
        """Return all records from the table"""
        return self.model.objects.all()

    def get_by_id(self, pk):
        """Return one record by primary key"""
        return self.model.objects.filter(pk=pk).first()

    def create(self, **kwargs):
        """Insert a new record"""
        return self.model.objects.create(**kwargs)

    def update(self, pk, **kwargs):
        """Update an existing record by ID"""
        obj = self.get_by_id(pk)
        if not obj:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()
        return obj

    def delete(self, pk):
        """Delete record by ID"""
        obj = self.get_by_id(pk)
        if obj:
            obj.delete()
            return True
        return False
