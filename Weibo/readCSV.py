import csv


csv_file=csv.reader(open('Keyword.csv','r'))
key_word = []
for keyword in csv_file:
    print(keyword)
    key_word.append(keyword)

for index in range(len(key_word)):
    print(key_word[index])

#N维数组
print(key_word[2][0])