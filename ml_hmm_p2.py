from Data_processor import Data_processor
import sys

possible_states = ["O","B-positive","I-positive","B-neutral","I-neutral","B-negative","I-negative"]

def emis_prob(a,b,Data):
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
    for i in possible_states:
        yscore = emis_prob(i,b,Data)
        if yscore > bestYscore:
            bestYscore = yscore
            optimalY = i
    return optimalY

def label_dev_in(inpath,Datapath,os):
    infile = open(inpath,'r',encoding='utf8')
    Y_dict = {}
    Data = Data_processor(Datapath)
    if os == "W":
        outpath = inpath.rsplit("\\",maxsplit=1)[0] + "\\dev.p2.out"
    else:
        outpath = inpath.rsplit("/",maxsplit=1)[0] + "/dev.p2.out"
    outfile = open(outpath,'w',encoding='utf8')
    # total = len(infile.read().split("\n"))
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
            outfile.write(output)
            # print(inpath.rsplit(str(tweet)+"/"+str(total)+ " done"))
    infile.close()
    outfile.close()


if len(sys.argv)< 4:
    print("Not enought arguments pls input in order:(input data set path, Traning file path, Windows('W') or Linux/Mac('L'))")
    sys.exit()

label_dev_in(sys.argv[1],sys.argv[2],sys.argv[3])
