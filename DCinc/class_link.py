class Link:
    def __init__(self, source, destination, distance=0.0):
        self.source = source
        self.destination = destination
        self.distance = distance

    def __repr__(self):
        return f"Link({self.source} -> {self.destination}, Distance={self.distance})"

