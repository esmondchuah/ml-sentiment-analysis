from Data_processor import Data_processor

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
                # print(tweet)
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
        previous_list = viterbiTopkRecursive(sequence,k,i,emis_dict,trans_dict,Data,score_dict)
        print(previous_list,i)
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
        # print((previous_max[0],score))
    # print((maxY,maxScore))
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
        # print((maxY,maxScore,len(sequence),i))
        # print(K_list)
        score_dict[(len(sequence),i)] = K_list
        return K_list

EN = Data_processor("C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\train")
testtweet = ["New","Year",",","New","Tech","Writers","Gathering","http://nblo.gs/cR1A1"]
trans_dict = {}
emis_dict = {}
score_dict = {}
print(viterbiTopk_end(testtweet,5,emis_dict,trans_dict,EN,score_dict))
