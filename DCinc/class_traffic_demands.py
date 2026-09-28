class TrafficDemands:
    # Vectors are the old Queues (Qhp, Qlp)

    def __init__(self, TrafficClassNames, xi):
        self.TrafficClassNames = TrafficClassNames
        self.xi = xi
        
        #23-6-2026
        # Vectors are the old Queues (Qhp, Qlp)
        #if self.TCvectors == "1":
        #    self.VectorNames = ["Single"]
        #elif self.TCvectors == "2":
        #    self.VectorNames = ["High Priority", "Low Priority"]
        #elif self.TCvectors == "2mix":
        #    self.VectorNames = ["High Priority", "Low Priority"]
        #elif self.TCvectors == "2seq":
        #    self.VectorNames = ["High Priority", "Low Priority"]

        self.numTDvectors = len(self.TrafficClassNames) #old self.lenQs

        

        self.X = []
        #original_X = [20, 40, 60, 80, 100, 120]
        #original_X = [20, 40, 60, 80, 100, 120, 160, 320, 640, 960, 1280]
        #original_X = [2, 4, 6, 8, 10, 15, 20] # to measure in the loads of Lee & Rhee paper
        #original_X = [2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 160, 200, 320, 640, 960, 1280]
        self.original_X = [2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 160, 200, 320, 400, 640, 960, 1280]

        for Xitem in self.original_X:
            #X.append(int(Xitem / lenQs)) # den tha xorizo edw ta X sta dyo H oxi analoga me to plithos twn Qs
            self.X.append(int(Xitem)) # o xwrismos analoga me to plithos twn Qs tha ginetai sti synartisi dimiourgias traffic requests

        #other definitions
        #X =  [10, 20, 30, 40, 50, 60]     # since I am using two queues traffic demand range parameter/multiplier is split to half #X for two queues
        #X = [20, 40, 60, 80, 100, 120]   # traffic demand range parameter/multiplier                                              #X for one queue
        self.xiName = self.X[self.xi]
