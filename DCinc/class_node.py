class Node:
    def __init__(self, node_id, name="", neighbors=[], has_wav_conv=False):
        self.node_id = node_id
        self.name = name
        self.neighbors = neighbors
        self.has_wav_conv = True if (has_wav_conv==1.0) else False

    # The __repr__ method just makes printing the object look nice in the console
    def __repr__(self):
        return f"Node(ID={self.node_id}, Name='{self.name}', Neighbors={self.neighbors}, WavConv={self.has_wav_conv})"


