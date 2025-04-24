'''
    Выведет в консоль массив из имён + фамилий учеников. Вставить в shkolnik_1 в фалйе token
    Таблицы с именами учеников можно попросить у учителей (можно у Буркальцевой Светланы Алексеевны)

'''

import pandas as pd
d = pd.read_excel(f'10А.xlsx')
s = []
for x in d['Unnamed: 1']:
    try:
        x =x.split()
        x = ' '.join([x[1], x[0]])
        s.append(x)
    except Exception as e:
        print(x, str(e))
d = pd.read_excel(f'10Б.xlsx')
for x in d['Unnamed: 1']:
    try:
        x =x.split()
        x = ' '.join([x[1], x[0]])
        s.append(x)
    except Exception as e:

        print(x, str(e))
d = pd.read_excel(f'11Б.xlsx')
for x in d['Unnamed: 1']:
    try:
        x =x.split()
        x = ' '.join([x[1], x[0]])
        s.append(x)
    except Exception as e:
        print(x, str(e))
d = pd.read_excel(f'11А.xlsx')
for x in d['Unnamed: 1']:
    try:
        x =x.split()
        x = ' '.join([x[1], x[0]])
        s.append(x)
    except Exception as e:
        print(x, str(e))
print(s)