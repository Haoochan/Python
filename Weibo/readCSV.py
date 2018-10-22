import csv


csv_file=csv.reader(open('Keyword.csv','r'))
key_word = []
for keyword in csv_file:
    # print(keyword)
    key_word.append(keyword)

#N维数组
# print(key_word[2][0])
# print(key_word)