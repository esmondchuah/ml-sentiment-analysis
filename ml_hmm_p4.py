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

def viterbiTopk_kthlabel(inpath,Datapath,k,os):
    trans_dict = {}
    emis_dict = {}
    Data = Data_processor(Datapath)
    if os == "W":
        outpath = inpath.rsplit("\\",maxsplit=1)[0] + "\\dev.p4.out"
    else:
        outpath = inpath.rsplit("/",maxsplit=1)[0] + "/dev.p4.out"
    outfile = open(outpath,'w',encoding='utf8')
    indata = Data_processor(inpath)
    total = len(indata.data)
    for tweet in range(len(indata.data)):
        score_dict = {}
        TopKlist = viterbiTopk_end(indata.data[tweet],k,emis_dict,trans_dict,Data,score_dict)
        TopKlist = sorted(TopKlist,key=lambda x:x[1])
        Kth_seq = TopKlist[0]
        for i in range(len(Kth_seq[0].split(" "))):
            output = indata.data[tweet][i] + " " + Kth_seq[0].split(" ")[i] + "\n"
            outfile.write(output)
        outfile.write("\n")
        print(str(tweet+1)+"/"+str(total)+ " done")
    print("done!")
    outfile.close()

def viterbiTopK_start(sequence,i,emis_dict,trans_dict,Data,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        score = trans_prob("start",i,Data,trans_dict)*emis_prob(i,sequence[-1],Data,emis_dict)
        score_dict[(len(sequence),i)] = [(i,score)]
        return [(i,score)]

def viterbiTopk_end(sequence,k,emis_dict,trans_dict,Data,score_dict):
    TopKlist = []
    for i in possible_states:
        if len(sequence) == 1:
            previous_list = viterbiTopK_start(sequence,i,emis_dict,trans_dict,Data,score_dict)
        else:
            previous_list = viterbiTopkRecursive(sequence,k,i,emis_dict,trans_dict,Data,score_dict)
        for j in previous_list:
            score = j[1]*trans_prob(i,"stop",Data,trans_dict)
            if score != 0:
                if len(TopKlist) < k:
                    TopKlist.append((j[0],score))
                else:
                    index = 0
                    for l in range(1,len(TopKlist)):
                        if TopKlist[l][1] < TopKlist[index][1]:
                            index = l
                    if score > TopKlist[index][1]:
                        TopKlist[index] = (j[0],score)
    if len(TopKlist) == 0:
        previous_Olist = viterbiTopkRecursive(sequence,k,"O",emis_dict,trans_dict,Data,score_dict)
        TopKlist.append((previous_Olist[0][0],0))
    return TopKlist


def viterbiTopkRecursive(sequence,k,i,emis_dict,trans_dict,Data,score_dict):
    if (len(sequence),i) in score_dict.keys():
        return score_dict[(len(sequence),i)]
    else:
        K_list = []
        for j in possible_states:
            if len(sequence) == 2:
                previous_list = viterbiTopK_start(sequence[:-1],j,emis_dict,trans_dict,Data,score_dict)
            else:
                previous_list = viterbiTopkRecursive(sequence[:-1],k,j,emis_dict,trans_dict,Data,score_dict)
            for z in previous_list:
                score = z[1]*trans_prob(j,i,Data,trans_dict)*emis_prob(i,sequence[-1],Data,emis_dict)
                Yseq = z[0] + " " + i
                if score != 0:
                    if len(K_list) < k:
                        K_list.append((Yseq,score))
                    else:
                        K_index = 0
                        for l in range(1,len(K_list)):
                            if K_list[l][1] < K_list[K_index][1]:
                                K_index = l
                        if score > K_list[K_index][1]:
                            K_list[K_index] = (Yseq,score)
        if len(K_list) == 0:
            previous_Olist = viterbiTopkRecursive(sequence[:-1],k,"O",emis_dict,trans_dict,Data,score_dict)
            Yseq = previous_Olist[0][0] + " " + i
            K_list.append((Yseq,0))
        score_dict[(len(sequence),i)] = K_list
        return K_list

# EN = Data_processor("C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\train")
# EN_in = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\dev.in"
# ES = Data_processor("C:\\Users\\Loo Yi\\Desktop\\ml-project\\ES\\train")
# ES_in = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\ES\\dev.in"

if len(sys.argv)< 5:
    print("Not enought arguments pls input in order:(kvalue,input data set path, Traning file path, Windows('W') or Linux/Mac('L'))")
    sys.exit()

viterbiTopk_kthlabel(sys.argv[2],sys.argv[3],int(sys.argv[1]),sys.argv[4])
