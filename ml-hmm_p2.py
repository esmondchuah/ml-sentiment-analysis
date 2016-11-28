from Data_processor import Data_processor

possible_states = ["O","B-positive","I-positive","B-neutral","I-neutral","B-negative","I-negative"]

def emis_prob(a,b,Data):
    # if a not in possible_states:
    #     return "Invalid input"
    countAB = 0
    countA = 1
    countB = 0
    for tweet in Data.data:
        for j in range(len(tweet)):
            if tweet[j].split(" ")[0] == b:
                countB +=1
            if tweet[j].split(" ")[1] == a:
                countA +=1
                if tweet[j].split(" ")[0] == b:
                    countAB +=1
    if countB == 0:
        return float(1/countA)
    return float(countAB/countA)


def optimalY_bycompare(b,Data):
    bestYscore = 0
    optimalY = ""
    # Y_d ={}
    # sumz = 0
    for i in possible_states:
        yscore = emis_prob(i,b,Data)
        # sumz += yscore
        # Y_d[i] = yscore
        if yscore > bestYscore:
            bestYscore = yscore
            optimalY = i
    # print("optimalY : " + optimalY)
    # print("sum = "+str(sumz))
    # print(b + " " + str(Y_d))
    return optimalY

def label_dev_in(Data,inpath):
    infile = open(inpath,'r',encoding='utf8')
    Y_dict = {}
    outpath = inpath.rsplit("\\",maxsplit=1)[0] + "\\dev.p2.out"
    #TO DO: implement path for MACOS
    outfile = open(outpath,'w',encoding='utf8')
    # print(outpath)
    for i in infile.read().split("\n"):
        if i == "":
            outfile.write("\n")
        else:
            if i in Y_dict.keys():
                optimalY = Y_dict[i]
            else:
                optimalY = optimalY_bycompare(i,Data)
                Y_dict[i] = optimalY
            output = i + " " + optimalY + "\n"
            # print(output)
            outfile.write(output)
    infile.close()
    outfile.close()



EN = Data_processor("C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\train")
# print(str(emis_prob('O','a',EN)) + " " + str(emis_prob('O','I-negative',EN)))
# optimalY_bycompare("a",EN)
EN_in = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\dev.in"
label_dev_in(EN,EN_in)
