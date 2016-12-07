from Data_processor import Data_processor
import sys

possible_states = ["O", "B-positive", "I-positive", "B-neutral", "I-neutral", "B-negative", "I-negative"]

def emis_prob(state, word, training_data):
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
        return float(1/count_state)

    return float(count_emission/count_state)

def find_opt_y(word, training_data):
    best_y_score = 0
    opt_y = ""
    for state in possible_states:
        y_score = emis_prob(state, word, training_data)
        if y_score > best_y_score:
            best_y_score = y_score
            opt_y = state
    return opt_y

def label_dev_data(dev_datapath, training_datapath, os):
    y_dict = {} # dictionary storing the optimal state (y) of each word (x)
    dev_data = Data_processor(dev_datapath).data
    training_data = Data_processor(training_datapath).data

    if os == "W":
        outpath = dev_datapath.rsplit("\\",maxsplit=1)[0] + "\\dev.p2.out"
    else:
        outpath = dev_datapath.rsplit("/",maxsplit=1)[0] + "/dev.p2.out"

    outfile = open(outpath, 'w', encoding='utf8')
    total_tweets = len(dev_data)

    for tweet in range(total_tweets):
        for word in dev_data[tweet]:
            if word in y_dict.keys():
                opt_y = y_dict[word]
            else:
                opt_y = find_opt_y(word, training_data)
                y_dict[word] = opt_y
            output = word + " " + opt_y + "\n"
            outfile.write(output)
        outfile.write("\n")
        print(str(tweet+1) + "/" + str(total_tweets) + " done")

    print("Labelling completed!")
    outfile.close()

if len(sys.argv) < 4:
    print("Not enough arguments pls input in order: (input data file path, training data file path, 'W'(for Windows) or 'L'(for Linux/Mac)")
    sys.exit()

label_dev_data(sys.argv[1],sys.argv[2],sys.argv[3])
