import sys
sys.setrecursionlimit(2000)

possible_states = ["O","B-positive","I-positive","B-neutral","I-neutral","B-negative","I-negative"]

class Data_processor:
    def __init__(self,path):
        self.datal= []
        self.data = []
        self.file = open(path,'r',encoding="utf8")
        for i in self.file.read().split("\n\n") :
            sentence = []
            unlabeled = []
            for j in i.split("\n"):
                if j != "":
                    unlabeled.append(j)
                    word = j.split(" ")[0].lower()
                    if len(word) > 5 and word[:4] == "http":
                        word = word[:4]
                    if len(j.split(" ")) >1:
                        sentence.append(word + " " +j.split(" ")[-1])
                    else:
                        sentence.append(word)
            if len(sentence) > 0:
                self.data.append(sentence)
                self.datal.append(unlabeled)
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
                if tweet[j].split(" ")[0] == b:
                    countB +=1
                if tweet[j].split(" ")[1] == a:
                    countA +=1
                    if tweet[j].split(" ")[0] == b:
                        countAB +=1
        if countB == 0:
            result =  float(1/countA)
        else:
            result = float(countAB/countA)
        data_dict[(a,b)] = result
        return result

def transAB_prob(a,b,Data,data_dict):
    if (a,b) in data_dict.keys():
        return data_dict[(a,b)]
    else:
        countAB = 0
        countA = 0
        if a == 'start':
            countA = len(Data.data)
            for tweet in Data.data:
                if len(tweet[0].split(" ")) > 1 and tweet[0].split(" ")[1] == b:
                    countAB += 1
        elif b == 'stop':
            for tweet in Data.data:
                for j in range(len(tweet)):
                    if len(tweet[j].split(" ")) > 1 and tweet[j].split(" ")[1] == a:
                        countA +=1
                        if j == len(tweet)-1:
                            countAB +=1
        elif a == 'stop' or b == 'start':
            data_dict[(a,b)] = 0
            return 0
        else:
            for tweet in Data.data:
                for j in range(len(tweet)-1):
                    if len(tweet[j].split(" ")) > 1 and tweet[j].split(" ")[1] == a:
                        countA +=1
                        if tweet[j+1].split(" ")[1] == b:
                            countAB +=1
        result = float(countAB/countA)
        data_dict[(a,b)] = result
        return result


def trans_prob_ABC(a,b,c,Data,data_dict):
    if (a,b,c) in data_dict.keys():
        return data_dict[(a,b,c)]
    else:
        countABC = 0
        countAB = 0
        if a == "start":
            for tweet in Data.data:
                if len(tweet[0].split(" ")) > 1 and tweet[0].split(" ")[1] == b:
                    countAB += 1
                    if tweet[1].split(" ")[1] == c:
                        countABC +=1
        elif c == "stop":
            for tweet in Data.data:
                for j in range(1,len(tweet)):
                    if len(tweet[j].split(" ")) > 1 and tweet[j].split(" ")[1] == b and tweet[j-1].split(" ")[1] == c:
                        countAB += 1
                        if j == len(tweet)-1:
                            countABC +=1
        elif a=="stop" or b == "stop" or b == "start" or c == "start":
            data_dict[(a,b,c)] = 0
            return 0
        else:
            for tweet in Data.data:
                for j in range(1,len(tweet)-1):
                    if len(tweet[j].split(" ")) > 1 and tweet[j].split(" ")[1] == b and tweet[j-1].split(" ")[1] == a:
                        countAB += 1
                        if tweet[j+1].split(" ")[1] == c:
                            countABC +=1
        if countAB == 0:
            result = 0
        else:
            result = float(countABC/countAB)
        data_dict[(a,b,c)] = result
        return result


def viterbip5_label(inpathdev,Datapath,filename,os):
    Data = Data_processor(Datapath)
    if os == "W":
        outpathdev = inpathdev.rsplit("\\",maxsplit=1)[0] + "\\" + filename)
    else:
        outpathdev = inpathdev.rsplit("/",maxsplit=1)[0] + "/" + filename

    outfiledev = open(outpathdev,'w',encoding='utf8')
    indatadev = Data_processor(inpathdev)
    totaldev = len(indatadev.data)
    transAB_dict = {}
    transABC_dict = {}
    emis_dict = {}
    for tweet in range(len(indatadev.data)):
        score_dict = {}
        opYseq = viterbiTrigram_end(indatadev.data[tweet],emis_dict,transAB_dict,transABC_dict,Data,score_dict)
        for i in range(len(opYseq[0].split(" "))):
            output = indatadev.datal[tweet][i] + " " + opYseq[0].split(" ")[i] + "\n"
            outfiledev.write(output)
        outfiledev.write("\n")
        print("dev " + str(tweet+1)+"/"+str(totaldev)+ " done")
    print("Labelling done!")
    outfiledev.close()


def viterbiTrigram_start(sequence,i,emis_dict,trans_dict,Data,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        score = transAB_prob("start",i,Data,trans_dict)*emis_prob(i,sequence[-1],Data,emis_dict)
        score_dict[(len(sequence),i)] = [(i,score)]
        return [(i,score)]

def viterbiTrigram_end(sequence,emis_dict,transAB_dict,transABC_dict,Data,score_dict):
    maxY = ""
    maxScore = 0
    for i in possible_states:
        if len(sequence) == 1:
            previous_max = viterbiTrigram_start(sequence,i,emis_dict,transAB_dict,Data,score_dict)
            # print(previous_max)
            score = previous_max[0][1]*transAB_prob(i,"stop",Data,transAB_dict)
            if score > maxScore:
                maxY = previous_max[0][0]
                maxScore = score
        else:
            previous_list = viterbiTrigramRecursive(sequence,i,emis_dict,transAB_dict,transABC_dict,Data,score_dict)
            for j in previous_list:
                score = j[1]*(0.9*transAB_prob(i,"stop",Data,transAB_dict)+0.1*trans_prob_ABC(j[0].split(" ")[-2],j,"stop",Data,transABC_dict))
                if score > maxScore:
                    maxY = j[0]
                    maxScore = score
    if maxY == "":
        previous_O_list = viterbiTrigramRecursive(sequence,"O",emis_dict,transAB_dict,transABC_dict,Data,score_dict)
        maxY = previous_O_list[0][0]
        maxScore = 0
    return (maxY,maxScore)

def viterbiTrigramRecursive(sequence,i,emis_dict,transAB_dict,transABC_dict,Data,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        state_list = []
        for j in possible_states:
            if len(sequence) == 2:
                previous_list = viterbiTrigram_start(sequence[:-1],j,emis_dict,transAB_dict,Data,score_dict)
            else:
                previous_list = viterbiTrigramRecursive(sequence[:-1],j,emis_dict,transAB_dict,transABC_dict,Data,score_dict)
            maxY = ""
            maxScore = 0
            for k in previous_list:
                if len(sequence) == 2:
                    maxScore = k[1]*transAB_prob(j,i,Data,transAB_dict)*emis_prob(i,sequence[-1],Data,emis_dict)
                    maxY = k[0] + " " + i
                else:
                    score = k[1]*(0.9*transAB_prob(j,i,Data,transAB_dict)+0.1*trans_prob_ABC(k[0].split(" ")[-2],j,i,Data,transABC_dict))*emis_prob(i,sequence[-1],Data,emis_dict)
                    if score > maxScore:
                        maxY = k[0] + " " + i
                        maxScore = score
            if maxY == "":
                maxY = previous_list[0][0] + " " + i
            state_list.append((maxY,maxScore))
        score_dict[(len(sequence),i)] = state_list
        return state_list

if len(sys.argv) < 5:
    print("Not enough arguments pls input in order: (input data file path, training data file path, name of file,'W'(for Windows) or 'L'(for Linux/Mac)")
    sys.exit()

viterbip5_label(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
