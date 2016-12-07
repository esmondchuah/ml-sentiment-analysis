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


def viterbi_topK_kth_label(dev_datapath, training_datapath, k, os):
    trans_dict = {}
    emis_dict = {}
    training_data = Data_processor(training_datapath).data

    if os == "W":
        outpath = dev_datapath.rsplit("\\",maxsplit=1)[0] + "\\dev.p4.out"
    else:
        outpath = dev_datapath.rsplit("/",maxsplit=1)[0] + "/dev.p4.out"

    outfile = open(outpath, 'w', encoding='utf8')
    dev_data = Data_processor(dev_datapath).data
    total_tweets = len(dev_data)

    for tweet in range(total_tweets):
        score_dict = {}
        top_k_list = viterbi_topK_end(dev_data[tweet], k, emis_dict, trans_dict, training_data, score_dict)
        top_k_list = sorted(top_k_list, key=lambda x:x[1])
        kth_seq = top_k_list[0]
        tags = kth_seq[0].split(" ")

        for word in range(len(tags)):
            output = dev_data[tweet][word] + " " + tags[word] + "\n"
            outfile.write(output)

        outfile.write("\n")
        print(str(tweet+1) + "/" + str(total_tweets) + " done")

    print("Labelling completed!")
    outfile.close()


def viterbi_topK_start(sequence, state, emis_dict, trans_dict, training_data, score_dict):
    if (len(sequence), state) in score_dict.keys():
        return score_dict[(len(sequence), state)]
    else:
        score = trans_prob("start", state, training_data, trans_dict) * emis_prob(state, sequence[-1], training_data, emis_dict)
        score_dict[(len(sequence), state)] = [(state, score)]
        return [(state, score)]


def viterbi_topK_end(sequence, k, emis_dict, trans_dict, training_data, score_dict):
    top_k_list = []

    for state in possible_states:
        if len(sequence) == 1:
            previous_list = viterbi_topK_start(sequence, state, emis_dict, trans_dict, training_data, score_dict)
        else:
            previous_list = viterbi_topK_recursive(sequence, k, state, emis_dict, trans_dict, training_data, score_dict)

        for j in previous_list:
            score = j[1] * trans_prob(state, "stop", training_data, trans_dict)
            if score != 0:
                if len(top_k_list) < k:
                    top_k_list.append((j[0], score))
                else:
                    index = 0
                    for l in range(1, len(top_k_list)):
                        if top_k_list[l][1] < top_k_list[index][1]:
                            index = l
                    if score > top_k_list[index][1]:
                        top_k_list[index] = (j[0], score)

    if len(top_k_list) == 0:
        previous_O_list = viterbi_topK_recursive(sequence, k, "O", emis_dict, trans_dict, training_data, score_dict)
        top_k_list.append((previous_O_list[0][0],0))
    return top_k_list


def viterbi_topK_recursive(sequence, k, state, emis_dict, trans_dict, training_data, score_dict):
    if (len(sequence), state) in score_dict.keys():
        return score_dict[(len(sequence), state)]
    else:
        k_list = []
        for prev_state in possible_states:
            if len(sequence) == 2:
                previous_list = viterbi_topK_start(sequence[:-1], prev_state, emis_dict, trans_dict, training_data, score_dict)
            else:
                previous_list = viterbi_topK_recursive(sequence[:-1], k, prev_state, emis_dict, trans_dict, training_data, score_dict)

            for z in previous_list:
                score = z[1] * trans_prob(prev_state, state, training_data, trans_dict) * emis_prob(state, sequence[-1], training_data, emis_dict)
                y_seq = z[0] + " " + state
                if score != 0:
                    if len(k_list) < k:
                        k_list.append((y_seq, score))
                    else:
                        k_index = 0
                        for l in range(1, len(k_list)):
                            if k_list[l][1] < k_list[k_index][1]:
                                k_index = l
                        if score > k_list[k_index][1]:
                            k_list[k_index] = (y_seq, score)

        if len(k_list) == 0:
            previous_O_list = viterbi_topK_recursive(sequence[:-1], k, "O", emis_dict, trans_dict, training_data, score_dict)
            y_seq = previous_O_list[0][0] + " " + state
            k_list.append((y_seq, 0))

        score_dict[(len(sequence), state)] = k_list
        return k_list


if len(sys.argv) < 5:
    print("Not enough arguments pls input in order: (k-value, input data file path, training data file path, 'W'(for Windows) or 'L'(for Linux/Mac)")
    sys.exit()

viterbi_topK_kth_label(sys.argv[2],sys.argv[3],int(sys.argv[1]),sys.argv[4])
