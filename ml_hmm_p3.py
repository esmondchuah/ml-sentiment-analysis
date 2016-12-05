from Data_processor import Data_processor
import sys
sys.setrecursionlimit(2000)

possible_states = ["O", "B-positive", "I-positive", "B-neutral", "I-neutral", "B-negative", "I-negative"]

def emis_prob(state, word, training_data, emis_dict):
    if (state, word) in emis_dict.keys():
        return emis_dict[(state, word)]
    else:
        count_emission = 0 # count the emission from state to word
        count_state = 1
        count_word = 0

        for tweet in training_data:
            for j in range(len(tweet)):
                if tweet[j].split(" ")[0] == word:
                    count_word += 1
                if tweet[j].split(" ")[1] == state:
                    count_state += 1
                    if tweet[j].split(" ")[0] == word:
                        count_emission += 1

        if count_word == 0:
            result =  float(1/count_state)
        else:
            result = float(count_emission/count_state)

        emis_dict[(state, word)] = result
        return result

def trans_prob(state1, state2, training_data, trans_dict):
    if (state1, state2) in trans_dict.keys():
        return trans_dict[(state1, state2)]
    else:
        count_transition = 0 # count the transition from state1 to state 2
        count_state1 = 0

        if state1 == 'start':
            count_state1 = len(training_data)
            for tweet in training_data:
                if len(tweet[0].split(" ")) > 1 and tweet[0].split(" ")[1] == state2:
                    count_transition += 1

        elif state2 == 'stop':
            for tweet in training_data:
                for j in range(len(tweet)):
                    if len(tweet[j].split(" ")) > 1  and tweet[j].split(" ")[1] == state1:
                        count_state1 += 1
                        if j == len(tweet) - 1:
                            count_transition += 1

        elif state1 == 'stop' or state2 == 'start':
            trans_dict[(state1, state2)] = 0
            return 0

        else:
            for tweet in training_data:
                for j in range(len(tweet)-1):
                    if len(tweet[j].split(" ")) > 1 and tweet[j].split(" ")[1] == state1:
                        count_state1 += 1
                        if tweet[j+1].split(" ")[1] == state2:
                            count_transition += 1

        result = float(count_transition/count_state1)
        trans_dict[(state1, state2)] = result
        return result

# def get_Ysequence(tweet,Data):
#     trans_dict = {}
#     emis_dict = {}
#     score_dict = {}
#     return viterbi_end(tweet,emis_dict,trans_dict,Data,score_dict)

def viterbi_label(dev_datapath, training_datapath, os):
    trans_dict = {}
    emis_dict = {}
    training_data = Data_processor(training_datapath).data

    if os == "W":
        outpath = dev_datapath.rsplit("\\",maxsplit=1)[0] + "\\dev.p3.out"
    else:
        outpath = dev_datapath.rsplit("/",maxsplit=1)[0] + "/dev.p3.out"

    outfile = open(outpath, 'w', encoding='utf8')
    dev_data = Data_processor(dev_datapath).data
    total_tweets = len(dev_data)

    for tweet in range(total_tweets):
        score_dict = {}
        opt_y_seq = viterbi_end(dev_data[tweet], emis_dict, trans_dict, training_data, score_dict)
        tags = opt_y_seq[0].split(" ")
        for word in range(len(tags)):
            output = dev_data[tweet][word] + " " + tags[word] + "\n"
            outfile.write(output)
        outfile.write("\n")
        print(str(tweet+1) + "/" + str(total_tweets) + " done")

    print("Labelling completed!")
    outfile.close()

def viterbi_start(sentence, state, emis_dict, trans_dict, training_data, score_dict):
    if (len(sentence), state) in score_dict.keys():
        return score_dict[(len(sentence), state)]
    else:
        score = trans_prob("start", state, training_data, trans_dict) * emis_prob(state, sentence[-1], training_data, emis_dict)
        score_dict[(len(sentence), state)] = (state, score)
        return (state, score)

def viterbi_end(sentence, emis_dict, trans_dict, training_data, score_dict):
    max_y = ""
    max_score = 0

    for state in possible_states:
        if len(sentence) == 1:
            previous_max = viterbi_start(sentence, state, emis_dict, trans_dict, training_data, score_dict)
        else:
            previous_max = viterbi_recursive(sentence, state, emis_dict, trans_dict, training_data, score_dict)
        score = previous_max[1] * trans_prob(state, "stop", training_data, trans_dict)
        if score > max_score:
            max_y = previous_max[0]
            max_score = score

    if max_y == "":
        previous_O = viterbi_recursive(sentence[:-1], "O", emis_dict, trans_dict, training_data, score_dict)
        max_y = previous_O[0]
        max_score = 0
    return (max_y, max_score)

def viterbi_recursive(sentence, state, emis_dict, trans_dict, training_data, score_dict):
    if (len(sentence),state) in score_dict.keys():
        return score_dict[(len(sentence), state)]
    else:
        max_y = ""
        max_score = 0

        for prev_state in possible_states:
            if len(sentence) == 2:
                previous_max = viterbi_start(sentence[:-1], prev_state, emis_dict, trans_dict, training_data, score_dict)
            else:
                previous_max = viterbi_recursive(sentence[:-1], prev_state, emis_dict, trans_dict, training_data, score_dict)
            score = previous_max[1] * trans_prob(prev_state, state, training_data, trans_dict) * emis_prob(state, sentence[-1], training_data, emis_dict)

            if score > max_score:
                max_y = previous_max[0] + " " + state
                max_score = score

        if max_y == "":
            previous_O = viterbi_recursive(sentence[:-1], "O", emis_dict, trans_dict, training_data, score_dict)
            max_y = previous_O[0] + " " + state
            max_score = 0

        score_dict[(len(sentence), state)] = (max_y, max_score)
        return (max_y, max_score)

# testtweet = ['"Mike"', 'Update', ':', 'It', 'has', 'been', 'awhile', 'since', 'I', 'spoke', 'of', 'my', 'friend', '"Mike"', '.', '�', 'Things', 'have', 'gotten', 'a', 'little', 'more', 'relaxed', 'sin', '...', 'http://bit.ly/aziC6H']
# testtweet = ["New","Year",",","New","Tech","Writers","Gathering","http://nblo.gs/cR1A1"]
# print(get_Ysequence(testtweet,EN))

if len(sys.argv) < 4:
    print("Not enough arguments pls input in order: (input data file path, training data file path, 'W'(for Windows) or 'L'(for Linux/Mac)")
    sys.exit()

viterbi_label(sys.argv[1], sys.argv[2], sys.argv[3])

# EN = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\train"
# EN_in = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\EN\\dev.in"
# ES = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\ES\\train"
# ES_in = "C:\\Users\\Loo Yi\\Desktop\\ml-project\\ES\\dev.in"
#
# viterbi_label(EN_in,EN,"W")
# viterbi_label(ES_in,ES,"W")
