class Data_processor:
    def __init__(self,path):
        self.data= []
        self.file = open(path,'r',encoding="utf8")
        for i in self.file.read().split("\n\n") :
            sentence = []
            for j in i.split("\n"):
                sentence.append(j)
            self.data.append(sentence)



def emisprob(a,b,Data):
    countAB = 0 
    countA = 1
    count = 0
    for tweet in Data.data:
        for j in range(len(tweet)):
            if len(tweet[j].split(" ")) > 1 and tweet[j].split(" ")[1] == a:
                countA +=1
                if tweet[j].split(" ")[0] == b:
                    countAB +=1

    if countAB == 0:
        return float(1/countA)
    return float(countAB/countA)



def transprob(a,b,Data):
    countAB = 0
    countA = 0
    if a == 'start':
        countA = len(Data.data)
        for tweet in Data.data:
            if tweet[0].split(" ")[1] == b:
                countAB += 1
    elif b == 'stop':
        for tweet in Data.data:
            for j in range(len(tweet)-1):
                if tweet[j].split(" ")[1] == a:
                    countA +=1
            if tweet[-1] == a:
                countA += 1
                countAB +=1
    else:               
        for tweet in Data.data:
            for j in range(len(tweet)-1):
                if tweet[j].split(" ")[1] == a:
                    countA +=1
                    if tweet[j+1].split(" ")[1] == b:
                        countAB +=1
    return float(countAB/count)

EN = Data_processor("C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\train")
# for tweet in EN.data:
#     for j in range(len(tweet)):
#         print(tweet[j].split(" ")[1])
print (str(emisprob('O','asjkdfkah',EN)))



    
