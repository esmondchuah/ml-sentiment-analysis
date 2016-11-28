from Data_processor import Data_processor

possible_states = ["O","B-positive","B-negative","B-neutral","I-negative","I-positive","B-neutral"]

def emis_prob(a,b,Data,data_dict):
    # if a not in possible_states:
    #     return "Invalid input"
    if (a,b) in data.dict.keys():
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
    # if a not in possible_states and b not in possible_states:
    #     return "Invalid input"
    if (a,b) in data.dict.keys():
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
                for j in range(len(tweet)-1):
                    if len(tweet[j].split(" ")) > 1 and tweet[j].split(" ")[1] == a:
                        countA +=1
                if tweet[-1] == a:
                    countA += 1
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


def get_Ysequence(tweet,Data):

def viterbiRecursive(sequence,point):
    if len(sequence) == 1:
        maxY = ""
        maxScore = 0
        for i in possible_states:
            score = Trans_dict[('start',i)]*emis_prob()
            if score > maxScore:
                maxY = i
                maxYscore = yscore
