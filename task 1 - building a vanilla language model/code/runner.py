from xml.dom import minidom
import random

# ------- Global Variables -------
word_count = 0 #Stores the count of words from the training data corpus
#Stores the unigram,bigram and trigram and their probabilities.
unigram, bigram, trigram = [], [], []
unigram_freq, bigram_freq, trigram_freq = [], [], []

#A recursive functions that gets each word from the corpus sentences into an array of words and returns them.
def getWords(sentence):
    temp_sentence = []
    for word in sentence.childNodes:
        #If the current word is a sub-sentence, get the words within it (recursively) and merge it with the current snetence.
        if(word.tagName != "w" and word.tagName != "c"):
            words = getWords(word)
            temp_sentence = temp_sentence + words
        else:
            #Base case - add it to the current sentence.
            temp_sentence.append(word.firstChild.data)
    return temp_sentence

#A function the builds the N-Gram arrays and sets the word_count to the amount of words in the unigram.
def buildNGrams(sentences):
    #Accessing each sentence.
    for sentence in sentences:
        #Skipping any empty sentences - in case they appear.
        if(len(sentence) != 0):
            #Accessing each word in the current sentence.
            for i,word in enumerate(sentence):
                # ----- Unigram creation -----
                # If the word was already added, increment its frequency.
                if word in unigram:
                    unigram_freq[unigram.index(word)] += 1
                # Else the word is appended to the unigram array and it's frequency is set to 1.
                else:
                    unigram.append(word)
                    unigram_freq.append(1)

                # ----- Bigram creation -----
                # If the bigram word was already added, increment its frequency.
                if len(sentence) > i+1 and [word,sentence[i+1]] in bigram:
                    bigram_freq[bigram.index([word,sentence[i+1]])] += 1
                # Else the bigram word is appended to the bigram array and it's frequency is set to 1.
                elif len(sentence) > i+1:
                    bigram.append([word, sentence[i + 1]])
                    bigram_freq.append(1)
                # If there is no word after it's position (i+1), a bigram cannot be made.

                # ----- Trigram creation
                # If the trigram word was already added, increment its frequency.
                if len(sentence) > i+2 and [word,sentence[i+1],sentence[i+2]] in trigram:
                    trigram_freq[trigram.index([word,sentence[i+1],sentence[i+2]])] += 1
                # Else the trigram word is appended to the trigram array and it's frequency is set to 1.
                elif len(sentence) > i+2:
                    trigram.append([word, sentence[i + 1], sentence[i + 2]])
                    trigram_freq.append(1)
                # If there is no two word after it's position (i+2), a trigram cannot be made.
    global word_count
    word_count = len(unigram)

#A function that calculates the probabilities of each N-Gram model and returns them.
def calculateProb():
    unigram_prob = []
    for i,word in enumerate(unigram):
        # Formula = count(word)/word count
        word_prob = unigram_freq[i]/word_count
        unigram_prob.append(word_prob)

    bigram_prob = []
    for i,word in enumerate(bigram):
        #Gets the frequency of the first word using the unigram arrays.
        freq = unigram_freq[unigram.index(word[0])]
        # Formula = count(bigram word)/count(first word)
        word_prob = bigram_freq[i] / freq
        bigram_prob.append(word_prob)

    trigram_prob = []
    for i,word in enumerate(trigram):
        # Gets the frequency of the first two words using the bigram arrays.
        freq = bigram_freq[bigram.index([word[0], word[1]])]
        # Formula = count(trigram word)/count(first two words)
        word_prob = trigram_freq[i] / freq
        trigram_prob.append(word_prob)

    return unigram_prob,bigram_prob,trigram_prob

#A function to demonstrate the contents of the trigram.
def printTest(trigram_prob):
    for i,word in enumerate(trigram):
        print("P("+ word[len(word)-1] + "|" + word[0] + word[1] + ")=" + str(trigram_prob[i]))

def main():
    doc = minidom.parse('A6U.xml')
    # Store each sentence <s></s> object in an array.
    doc_sentences = doc.getElementsByTagName('s')
    final_sentences = [] #Will store the final array of sentences - consisting of words only.

    #Goes through each sentence DOM object and returns an array of words which is appended to final_sentences.
    for i, sentence in enumerate(doc_sentences):
        final_sentences.append(getWords(sentence))

    #Shuffles the final sentences and takes 80% for training and 20% for evaluation.
    random.shuffle(final_sentences)
    training_sentences = final_sentences[0:round(.8*len(final_sentences))]
    evaluation_sentences = final_sentences[round(.8*len(final_sentences)):len(final_sentences)]

    #Populates the N Grams with the training sentences.
    buildNGrams(training_sentences)
    #Calculates the N-Gram probabilities and returns them.
    unigram_prob, bigram_prob, trigram_prob = calculateProb()
    #A test that prints out the probabilities of the trigam.
    printTest(trigram_prob)

main()

