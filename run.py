import requests
from bs4 import BeautifulSoup
import pandas as pd

def recieve_names(url, adds=1):
    global dct
    dct = {}
    
    # Наименования:
    req = requests.get(url)
    text = req.text
    soup = BeautifulSoup(req.text, 'lxml')
    names = soup.find_all("p", class_="bib")
    
    additional = soup.find_all("p", class_="bibc")
    if additional != []:
        print('\n\nВнимание! По данной заявке Роспатентом направлялся запрос об уточнении перечня товаров и/или услуг.\nЭто означает, что в перечень товаров и/или услуг могли быть внесены изменения, которые не отражены в заявке.\n\n')

    if adds == 1:
        result_list = names[-1:]
        result = str(result_list)
        res1 = result.split('\n\t\t\t')
    else:
        result_list = names[-adds:(-adds+1)]
        result = str(result_list)
        res1 = result.split('\n\t\t\t')  
    for i in range(len(res1)-1):
        if i != (len(res1)-2):
            numer = int(res1[i][-2:])
            lst = res1[i+1][3:-17]
            dct[numer] = lst
        else:
            numer = int(res1[i][-2:])
            lst = res1[i+1][3:-11]
            dct[numer] = lst    
    for key in dct.keys():
        dct[key] = dct[key].strip().split('; ')
    
    # Год:
    global year
    date = str(names[3])[-19:-9]
    year = pd.to_datetime(date).year
    return dct

year = 2021
# Функция перевода полученных наименований
def translate_names(dct, year=year, lang='EN'):
    # Current DF
    nums = []
    values = []
    for key in dct.keys():
        for i in dct[key]:
            nums.append(key)
            values.append(i)
    df = pd.DataFrame()
    df['number']=nums
    df['РУС']=values

    # Choose year
    table = pd.read_excel(r'table.xlsm', sheet_name=str(year), header=1)
    table['РУС'] = [x.strip() for x in table['РУС'].values]
    table = table.rename(columns={'Unnamed: 0':'number'})
    table['РУС'] = [x.lower().split('*')[0] for x in table['РУС'].values]
    table['EN'] = [x.lower().split('*')[0] for x in table['EN'].values]
    table['FR'] = [x.lower().split('*')[0] for x in table['FR'].values]
    
    # Merging
    # Final
    final = {}
    if lang == 'EN':
        df = df.merge(table, on='РУС', how='left').drop(['number_y'],axis=1)
        df['EN'] = df['EN'].fillna(df['РУС'])
        new = df.groupby('number_x',as_index=True).agg({'EN':'unique'})

        for index in new.index:
            final[index] = new['EN'][index]
        for key in final.keys():
            final[key] = [str(x) for x in final[key]]
            final[key] = ', '.join(final[key])
    
    elif lang == 'FR':
        df = df.merge(table, on='РУС', how='left').drop(['number_y'],axis=1)
        df['FR'] = df['FR'].fillna(df['РУС'])
        new = df.groupby('number_x',as_index=True).agg({'FR':'unique'})

        for index in new.index:
            final[index] = new['FR'][index]
        for key in final.keys():
            final[key] = [str(x) for x in final[key]]
            final[key] = ', '.join(final[key])
        
    return final

URL = input('Вставь ссылку на патент: ')
a = int(input('Извещения (+1 за каждую запись жирным шрифтом снизу документа; 1 в случае отсутсвия извещений): '))
ans = input('Хотите выбрать год словаря? (Да/Нет): ')
lang = input('Выберите язык для перевода (EN/FR): ')

if ans.lower() == 'да':
    names_list = recieve_names(URL, a)
    year = int(input('Введите нужный год: '))
    print('\n\n',translate_names(names_list, year, lang.upper()))
    
elif ans.lower() == 'нет':
    names_list = recieve_names(URL, a)
    print('\n\n',f'Год был подобран автоматически. Дата подачи заявки: {year}','\n\n')
    print(translate_names(names_list,year, lang.upper()))
    
else:
    print('Некорректный ввод. Перезапустите программу')


