from Data_processor import Data_processor
import sys
import re
import math
sys.setrecursionlimit(2000)

possible_states = ["O","B-positive","I-positive","B-neutral","I-neutral","B-negative","I-negative"]

class Data_processor_prepross:
    def __init__(self,path):
        self.data= []
        self.file = open(path,'r',encoding="utf8")
        for i in self.file.read().split("\n\n") :
            sentence = []
            for j in i.split("\n"):
                if j != "":
                    word = j.split(" ")[0].lower()
                    if len(j.split(" ")) >1:
                        sentence.append(word + " " +j.split(" ")[-1])
                    else:
                        sentence.append(word)
            if len(sentence) > 0:
                self.data.append(sentence)
        self.file.close()

def emis_prob(a,b,Data,data_dict):
    if (a,b) in data_dict.keys():
        return data_dict[(a,b)]
    else:
        countAB = 0
        countA = 1
        countB = 0
        for tweet in Data.data:
            for j in range(len(tweet)):
                if tweet[j][0] == b:
                    countB +=1
                if tweet[j][1] == a:
                    countA +=1
                    if tweet[j][0] == b:
                        countAB +=1
        if countB == 0:
            result =  math.log(float(1/countA),10)
        else:
            if countAB != 0:
                result = math.log(float(countAB/countA),10)
            else:
                result = 0
        data_dict[(a,b)] = result
        return result

def trans_prob(a,b,Data,data_dict):
    if (a,b) in data_dict.keys():
        return data_dict[(a,b)]
    else:
        countAB = 0
        countA = 0
        if a == 'start':
            countA = len(Data.data)
            for tweet in Data.data:
                if len(tweet[0]) > 1 and tweet[0][1] == b:
                    countAB += 1
        elif b == 'stop':
            for tweet in Data.data:
                for j in range(len(tweet)):
                    if len(tweet[j]) > 1 and tweet[j][1] == a:
                        countA +=1
                        if j == len(tweet)-1:
                            countAB +=1
        elif a == 'stop' or b == 'start':
            data_dict[(a,b)] = 0
            return 0
        else:
            for tweet in Data.data:
                for j in range(len(tweet)-1):
                    if len(tweet[j]) > 1 and tweet[j][1] == a:
                        countA +=1
                        if tweet[j+1][1] == b:
                            countAB +=1
        if countAB != 0:
            result = math.log(float(countAB/countA),10)
        else:
            result = 0
        data_dict[(a,b)] = result
        return result

class Data_processor_p5:
    def __init__(self,path):
        self.data= []
        self.file = open(path,'r',encoding="utf8")
        for i in self.file.read().split("\n\n") :
            sentence = []
            for j in i.split("\n"):
                if j != "":
                    matchObj = re.match(r'^\W*(\w+)',j,re.M|re.I)
                    if matchObj:
                        word = matchObj.group(1)
                    else:
                        word = j
                    sentence.append((word.lower(),j.split(" ")[-1]))
            if len(sentence) > 0:
                self.data.append(sentence)
        self.file.close()

def get_features(X,Y):
    feature_dict = {}
    for i in range(len(Y)+1):
        if i == 0:
            a ="start"
        else:
            a = Y[i-1]
        if i == len(Y):
            b = "stop"
        else:
            b = Y[i]
        if (a,b) in feature_dict.keys():
            feature_dict[(a,b)] += 1
        else:
            feature_dict[(a,b)] = 1
    for j in range(len(Y)):
        y = Y[j]
        x = X[j]
        if (y,x) in feature_dict.keys():
            feature_dict[(y,x)] +=1
        else:
            feature_dict[(y,x)] =1
    return feature_dict

def getWeight(Data,iter):
    weight_dict = {}
    for i in range(iter):
        for data in Data.data:
            sequence = []
            label = []
            for word in data:
                sequence.append(word[0])
                label.append(word[1])
            predicted_Y = viterbi_end_train(sequence,weight_dict,{})
            predicted_Y_dict = get_features(sequence,predicted_Y[0].split(" "))
            prime_Y_dict = get_features(sequence,label)
            for tup in predicted_Y_dict.keys():
                if tup in prime_Y_dict.keys():
                    modif = prime_Y_dict[tup] - predicted_Y_dict[tup]
                else:
                    modif = -predicted_Y_dict[tup]
                if tup in weight_dict.keys():
                    weight_dict[tup] += modif
                else:
                    weight_dict[tup] = modif
            for tup in prime_Y_dict.keys():
                if tup not in predicted_Y_dict.keys():
                    modif = prime_Y_dict[tup]
                if tup in weight_dict.keys():
                    weight_dict[tup] += modif
                else:
                    weight_dict[tup] = modif
    return weight_dict


def viterbi_start_train(sequence,i,weight_dict,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        trans_score = 0
        emis_score = 0
        if ("start",i) in weight_dict.keys():
            trans_score = weight_dict[("start",i)]
        if (i,sequence[-1]) in weight_dict.keys():
            emis_score = weight_dict[(i,sequence[-1])]
        score = trans_score + emis_score
        score_dict[(len(sequence),i)] = (i,score)
        return (i,score)

def viterbi_start(sequence,i,weight_dict,emis_dict,trans_dict,Data,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        trans_score = 0
        emis_score = 0
        if ("start",i) in weight_dict.keys():
            trans_score = weight_dict[("start",i)]
        if (i,sequence[-1]) in weight_dict.keys():
            emis_score = weight_dict[(i,sequence[-1])]
        score = trans_score + emis_score + trans_prob("start",i,Data,trans_dict) + emis_prob(i,sequence[-1],Data,emis_dict)
        score_dict[(len(sequence),i)] = (i,score)
        return (i,score)

def viterbi_end_train(sequence,weight_dict,score_dict):
    maxY = ""
    maxScore = 0
    for i in possible_states:
        if len(sequence) == 1:
            previous_max = viterbi_start_train(sequence,i,weight_dict,score_dict)
        else:
            previous_max = viterbiRecursive_train(sequence,i,weight_dict,score_dict)
        trans_score = 0
        # print (previous_max)
        if (i,"stop") in weight_dict.keys():
            trans_score = weight_dict[(i,"stop")]
        score = previous_max[1] + trans_score
        if score > maxScore:
            maxY = previous_max[0]
            maxScore = score
    if maxY == "":
        previous_O = viterbiRecursive_train(sequence[:-1],"O",weight_dict,score_dict)
        maxY = previous_O[0]
        maxScore = 0
    return (maxY,maxScore)

def viterbiRecursive_train(sequence,i,weight_dict,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        maxY = ""
        maxScore = 0
        for j in possible_states:
            if len(sequence) == 2:
                previous_max = viterbi_start_train(sequence[:-1],j,weight_dict,score_dict)
            else:
                previous_max = viterbiRecursive_train(sequence[:-1],j,weight_dict,score_dict)
            trans_score = 0
            emis_score = 0
            if (j,i) in weight_dict.keys():
                trans_score = weight_dict[(j,i)]
            if (i,sequence[-1]) in weight_dict.keys():
                emis_score = weight_dict[(i,sequence[-1])]
            score = previous_max[1] + trans_score + emis_score
            if score > maxScore:
                maxY = previous_max[0] + " " + i
                maxScore = score
        if maxY == "":
            previous_O = viterbiRecursive_train(sequence[:-1],"O",weight_dict,score_dict)
            maxY = previous_O[0] + " " + i
            maxScore = 0
        score_dict[(len(sequence),i)] = (maxY,maxScore)
        return (maxY,maxScore)

def viterbi_end(sequence,weight_dict,emis_dict,trans_dict,Data,score_dict):
    maxY = ""
    maxScore = 0
    for i in possible_states:
        if len(sequence) == 1:
            previous_max = viterbi_start(sequence,i,weight_dict,emis_dict,trans_dict,Data,score_dict)
        else:
            previous_max = viterbiRecursive(sequence,i,weight_dict,emis_dict,trans_dict,Data,score_dict)
        trans_score = 0
        # print (previous_max)
        if (i,"stop") in weight_dict.keys():
            trans_score = weight_dict[(i,"stop")]
        score = previous_max[1] + trans_score + trans_prob(i,"stop",Data,trans_dict)
        if score > maxScore:
            maxY = previous_max[0]
            maxScore = score
    if maxY == "":
        previous_O = viterbiRecursive(sequence[:-1],"O",weight_dict,emis_dict,trans_dict,Data,score_dict)
        maxY = previous_O[0]
        maxScore = 0
    return (maxY,maxScore)

def viterbiRecursive(sequence,i,weight_dict,emis_dict,trans_dict,Data,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        maxY = ""
        maxScore = 0
        for j in possible_states:
            if len(sequence) == 2:
                previous_max = viterbi_start(sequence[:-1],j,weight_dict,emis_dict,trans_dict,Data,score_dict)
            else:
                previous_max = viterbiRecursive(sequence[:-1],j,weight_dict,emis_dict,trans_dict,Data,score_dict)
            trans_score = 0
            emis_score = 0
            if (j,i) in weight_dict.keys():
                trans_score = weight_dict[(j,i)]
            if (i,sequence[-1]) in weight_dict.keys():
                emis_score = weight_dict[(i,sequence[-1])]
            transprob = trans_prob(j,i,Data,trans_dict)
            emisprob = emis_prob(i,sequence[-1],Data,emis_dict)
            score = previous_max[1] + trans_score + emis_score + transprob + emisprob
            if score > maxScore:
                maxY = previous_max[0] + " " + i
                maxScore = score
        if maxY == "":
            previous_O = viterbiRecursive(sequence[:-1],"O",weight_dict,emis_dict,trans_dict,Data,score_dict)
            maxY = previous_O[0] + " " + i
            maxScore = 0
        score_dict[(len(sequence),i)] = (maxY,maxScore)
        return (maxY,maxScore)


def viterbip5_label(inpathdev,inpathtest,Datapath,os):
    Data = Data_processor_p5(Datapath)
    Datacount = Data_processor_prepross(Datapath)
    weight_map = getWeight(Data,50)
    print ("training done!")
    if os == "W":
        outpathdev = inpathdev.rsplit("\\",maxsplit=1)[0] + "\\dev.p5.out"
        outpathtest = inpathtest.rsplit("\\",maxsplit=1)[0] + "\\test.p5.out"
    else:
        outpathdev = inpathdev.rsplit("/",maxsplit=1)[0] + "/dev.p5.out"
        outpathtest = inpathtest.rsplit("/",maxsplit=1)[0] + "/test.p5.out"
    outfiledev = open(outpathdev,'w',encoding='utf8')
    indatadev = Data_processor_prepross(inpathdev)
    indatadevlabel = Data_processor(inpathdev)
    totaldev = len(indatadev.data)
    trans_dict = {}
    emis_dict = {}
    for tweet in range(len(indatadev.data)):
        score_dict = {}
        opYseq = viterbi_end(indatadev.data[tweet],weight_map,emis_dict,trans_dict,Datacount,score_dict)
        for i in range(len(opYseq[0].split(" "))):
            output = indatadevlabel.data[tweet][i] + " " + opYseq[0].split(" ")[i] + "\n"
            outfiledev.write(output)
        outfiledev.write("\n")
        print("dev " + str(tweet+1)+"/"+str(totaldev)+ " done")
    print("dev done!")
    outfiledev.close()
    outfiletest = open(outpathtest,'w',encoding='utf8')
    indatatest = Data_processor_prepross(inpathtest)
    indatatestlabel = Data_processor(inpathtest)
    totaltest = len(indatatest.data)
    for tweet in range(len(indatatest.data)):
        score_dict = {}
        opYseq = viterbi_end(indatatest.data[tweet],weight_map,emis_dict,trans_dict,Datacount,score_dict)
        for i in range(len(opYseq[0].split(" "))):
            output = indatatestlabel.data[tweet][i] + " " + opYseq[0].split(" ")[i] + "\n"
            outfiletest.write(output)
        outfiletest.write("\n")
        print("test "+ str(tweet+1)+"/"+str(totaltest)+ " done")
    print("test done!")
    outfiletest.close()

testtweet = ["New","Year",",","New","Tech","Writers","Gathering","http://nblo.gs/cR1A1"]
EN = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\train"
EN_in_test = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN_p5\\test.in"
EN_in_dev = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\dev.in"

viterbip5_label(EN_in_dev,EN_in_test,EN,"W")
# if len(sys.argv)< 4:
#     print("Not enought arguments pls input in order:(input data set path, Traning file path, Windows('W') or Linux/Mac('L'))")
#     sys.exit()
#
# viterbi_label(sys.argv[1],sys.argv[2],sys.argv[3])
