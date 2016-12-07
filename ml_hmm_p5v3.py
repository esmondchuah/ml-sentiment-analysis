from Data_processor import Data_processor
import sys
import re
import math
sys.setrecursionlimit(2000)

possible_states = ["O","B-positive","I-positive","B-neutral","I-neutral","B-negative","I-negative"]

# class Data_processor_p5:
#     def __init__(self,path):
#         self.data= []
#         self.file = open(path,'r',encoding="utf8")
#         for i in self.file.read().split("\n\n") :
#             sentence = []
#             for j in i.split("\n"):
#                 if j != "":
#                     matchObj = re.match(r'^\W*(\w+)',j,re.M|re.I)
#                     if matchObj:
#                         word = matchObj.group(1)
#                     else:
#                         word = j
#                     sentence.append((word.lower(),j.split(" ")[-1]))
#             if len(sentence) > 0:
#                 self.data.append(sentence)
#         self.file.close()

# class Data_processor_prepross:
#     def __init__(self,path):
#         self.datalabel= []
#         self.data = []
#         self.file = open(path,'r',encoding="utf8")
#         for i in self.file.read().split("\n\n") :
#             sentencelabel = []
#             sentence = []
#             for j in i.split("\n"):
#                 if j != "":
#                     word = j.split(" ")[0].lower()
#                     sentencelabel.append(word)
#                     sentence.a(j)
#             if len(sentence) > 0:
#                 self.datalabel.append(sentencelabel)
#                 self.data.append(sentence)
#         self.file.close()

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
    # print (feature_dict)
    return feature_dict

def getWeight(Data,iter):
    weight_dict = {}
    for i in range(iter):
        for data in Data.data:
            sequence = []
            label = []
            for word in data:
                # print(word)
                sequence.append(word.split(" ")[0])
                label.append(word.split(" ")[1])
            # print(sequence)
            # print(label)
            predicted_Y = viterbi_end_train(sequence,weight_dict,{})
            print(predicted_Y[0])
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

def viterbi_label(inpath,Datapath,os):
    Data = Data_processor(Datapath)
    weight_dict = getWeight(Data,50)
    print ("training done!")
    if os == "W":
        outpath = inpath.rsplit("\\",maxsplit=1)[0] + "\\dev.p5.out"
    else:
        outpath = inpath.rsplit("/",maxsplit=1)[0] + "/dev.p5.out"
    outfile = open(outpath,'w',encoding='utf8')
    indata = Data_processor(inpath)
    total = len(indata.data)
    for tweet in range(len(indata.data)):
        score_dict = {}
        opYseq = viterbi_end_train(indata.data[tweet],weight_dict,score_dict)
        for i in range(len(opYseq[0].split(" "))):
            output = indata.data[tweet][i] + " " + opYseq[0].split(" ")[i] + "\n"
            outfile.write(output)
        outfile.write("\n")
        print(str(tweet+1)+"/"+str(total)+ " done")
    print("done!")
    outfile.close()

EN = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\train"
EN_in_dev = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\dev.in"

viterbi_label(EN_in_dev,EN,"W")
# EN_D = Data_processor_p5(EN)
# dic = getWeight(EN_D,50)
# print(dic[("O","B-positive")])
# print(dic[("O","B-negative")])
# print(dic[("O","B-neutral")])
# for i in possible_states:
#     print("start" + " "+i+ " " + str(dic[("start",i)]))
#     for j in possible_states:
#         print(i+ " "+j+ " " + str(dic[(i,j)]))
#     print(i +" "+"stop"+ " " + str(dic[(i,"stop")]))
