# Data_processor class restructures the raw input data into a two-dimentional array.
class Data_processor:
    def __init__(self, path):
        self.data = []
        self.file = open(path, 'r', encoding="utf8")
        for i in self.file.read().split("\n\n") :
            sentence = []
            for j in i.split("\n"):
                if j != "":
                    sentence.append(j)
            if len(sentence) > 0:
                self.data.append(sentence)
        self.file.close()
