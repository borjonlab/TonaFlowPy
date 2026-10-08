import pickle



class idklol:
    def __init__(self):
        self.property1 = "PROP1"
        self.property2 = "PROP2"
        self.property3 = ["PROP3"]
        self.__hiddenprop__ = "hehe i'm hidden!"

j = idklol()

with open("lol.pkl","wb") as file:
    pickle.dump(j,file)

with open("lol.pkl","rb") as file:
    xd = pickle.load(file)