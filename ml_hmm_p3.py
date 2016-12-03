from Data_processor import Data_processor
import sys
sys.setrecursionlimit(2000)

possible_states = ["O","B-positive","I-positive","B-neutral","I-neutral","B-negative","I-negative"]

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

def trans_prob(a,b,Data,data_dict):
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

# def get_Ysequence(tweet,Data):
#     trans_dict = {}
#     emis_dict = {}
#     score_dict = {}
#     return viterbi_end(tweet,emis_dict,trans_dict,Data,score_dict)

def viterbi_label(inpath,Datapath,os):
    trans_dict = {}
    emis_dict = {}
    Data = Data_processor(Datapath)
    if os == "W":
        outpath = inpath.rsplit("\\",maxsplit=1)[0] + "\\dev.p3.out"
    else:
        outpath = inpath.rsplit("/",maxsplit=1)[0] + "/dev.p3.out"
    outfile = open(outpath,'w',encoding='utf8')
    indata = Data_processor(inpath)
    total = len(indata.data)
    for tweet in range(len(indata.data)):
        score_dict = {}
        opYseq = viterbi_end(indata.data[tweet],emis_dict,trans_dict,Data,score_dict)
        for i in range(len(opYseq[0].split(" "))):
            output = indata.data[tweet][i] + " " + opYseq[0].split(" ")[i] + "\n"
            outfile.write(output)
        outfile.write("\n")
        print(str(tweet+1)+"/"+str(total)+ " done")
    print("done!")
    outfile.close()

def viterbi_start(sequence,i,emis_dict,trans_dict,Data,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        score = trans_prob("start",i,Data,trans_dict)*emis_prob(i,sequence[-1],Data,emis_dict)
        score_dict[(len(sequence),i)] = (i,score)
        return (i,score)

def viterbi_end(sequence,emis_dict,trans_dict,Data,score_dict):
    maxY = ""
    maxScore = 0
    for i in possible_states:
        if len(sequence) == 1:
            previous_max = viterbi_start(sequence,i,emis_dict,trans_dict,Data,score_dict)
        else:
            previous_max = viterbiRecursive(sequence,i,emis_dict,trans_dict,Data,score_dict)
        score = previous_max[1]*trans_prob(i,"stop",Data,trans_dict)
        if score > maxScore:
            maxY = previous_max[0]
            maxScore = score
    if maxY == "":
        previous_O = viterbiRecursive(sequence[:-1],"O",emis_dict,trans_dict,Data,score_dict)
        maxY = previous_O[0]
        maxScore = 0
    return (maxY,maxScore)

def viterbiRecursive(sequence,i,emis_dict,trans_dict,Data,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        maxY = ""
        maxScore = 0
        for j in possible_states:
            if len(sequence) == 2:
                previous_max = viterbi_start(sequence[:-1],j,emis_dict,trans_dict,Data,score_dict)
            else:
                previous_max = viterbiRecursive(sequence[:-1],j,emis_dict,trans_dict,Data,score_dict)
            score = previous_max[1]*trans_prob(j,i,Data,trans_dict)*emis_prob(i,sequence[-1],Data,emis_dict)
            if score > maxScore:
                maxY = previous_max[0] + " " + i
                maxScore = score
        if maxY == "":
            previous_O = viterbiRecursive(sequence[:-1],"O",emis_dict,trans_dict,Data,score_dict)
            maxY = previous_O[0] + " " + i
            maxScore = 0
        score_dict[(len(sequence),i)] = (maxY,maxScore)
        return (maxY,maxScore)

# testtweet = ['"Mike"', 'Update', ':', 'It', 'has', 'been', 'awhile', 'since', 'I', 'spoke', 'of', 'my', 'friend', '"Mike"', '.', '�', 'Things', 'have', 'gotten', 'a', 'little', 'more', 'relaxed', 'sin', '...', 'http://bit.ly/aziC6H']
# testtweet = ["New","Year",",","New","Tech","Writers","Gathering","http://nblo.gs/cR1A1"]
# print(get_Ysequence(testtweet,EN))
if len(sys.argv)< 4:
    print("Not enought arguments pls input in order:(input data set path, Traning file path, Windows('W') or Linux/Mac('L'))")
    sys.exit()

viterbi_label(sys.argv[1],sys.argv[2],sys.argv[3])

# EN = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\train"
# EN_in = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\dev.in"
# ES = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\ES\\train"
# ES_in = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\ES\\dev.in"
#
# viterbi_label(EN_in,EN,"W")
# viterbi_label(ES_in,ES,"W")
