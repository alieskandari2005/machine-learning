import numpy as np
import mysql.connector
from sklearn import tree
from sklearn.preprocessing import LabelEncoder
from sklearn import preprocessing
import requests
import re
from bs4 import BeautifulSoup

cnx = mysql.connector.connect(user='root', password='11973560',
                              host='127.0.0.1',
                              database='finalproject')

for page in range(1,20):
    url = ('https://www.truecar.com/used-cars-for-sale/listings/?page=%s&sort[]=created_date_desc'%(page))
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    val = soup.find_all('a', attrs={'data-test': 'vehicleCardLink'})
    for link in val:
        links = ('https://www.truecar.com%s'%(link.get('href')))
        res = requests.get(links)
        soup = BeautifulSoup(res.text, 'html.parser')
        carName = soup.find('h1', attrs={'class':'heading-3 text-truncate margin-right-2 margin-right-sm-3'})
        used = soup.find('span', attrs={'data-test':'usedVdpHeaderMiles'})
        price = soup.find('div', attrs={'class':'label-block-text'})
        if price == None:
            pass
        else:
            carModel = re.findall(r'\d{4}', carName.text)
            carName = re.sub(r'\xa0', ' ', carName.text)
            carName = str(carName)
            carName = re.findall(r'([a-zA-Z]+.*)', carName)
            used = re.sub(r',', '', used.text)
            used = re.findall(r'^\d+', used)
            price = re.sub(r'\$', '', price.text)
            price = re.sub(r',', '', price)
            cursor = cnx.cursor()
            query = 'INSERT INTO car VALUES (\'%s\',\'%i\',\'%i\',\'%i\')'%(carName[0], int(carModel[0]), int(used[0]), int(price))
            cursor.execute(query)
            cnx.commit()

x = []
y = []
car_list = dict()
cursor = cnx.cursor()
query = 'SELECT * FROM car;'
cursor.execute(query)
for line in cursor:
    x.append(line[0:3])
    y.append(line[3])
x1 = np.array(x)
le1 = preprocessing.LabelEncoder()
x1[:,0] = le1.fit_transform(x1[:, 0])
x1 = x1.astype(np.int64)
cnx.close()
for i in range(0,len(x)):
    car_list = {x[i][0]:x1[i][0] for i in range(len(x))}
clf = tree.DecisionTreeClassifier()
clf = clf.fit(x1, y)

new_car = []
name = input('enter car name(the first letters must be capitalized): ')
while name not in car_list:
    name = input('your choice in not in list!!!please try again: ')
else:
    number = car_list[name]
    number1 = number.item()
    new_car += [number1]
new_car += [int(input('enter car model(year of product): '))]
new_car += [int(input('enter car mileage: '))]
answer = clf.predict([new_car])
print(answer[0],'$')
