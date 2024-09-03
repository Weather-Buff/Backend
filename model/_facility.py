import datetime

class Facility:

    def __init__(self, name: str, open: bool, last_count: int, percent_occupied: int, last_updated: datetime):
        self.name = name
        self.open = open
        self.last_count = last_count
        self.percent_occupied = percent_occupied
        self.last_updated = last_updated

    def to_dict(self):
        return {
            "name": self.name,
            "open": self.open,
            "last_count": self.last_count,
            "percent_occupied": self.percent_occupied,
            "last_updated": str(self.last_updated)
        }