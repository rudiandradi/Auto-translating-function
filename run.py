# Импорт библиотек:
import requests
from bs4 import BeautifulSoup
import bs4
import pandas as pd

print(requests.__version__)
print(bs4.__version__)
print(pd.__version__)


# Функция получения наименования товаров и услуг из html страницы
def recieve_names(url, adds=1):
    global dct
    dct = {}

    # Наименования:
    req = requests.get(url)
    text = req.text
    soup = BeautifulSoup(req.text, 'lxml')
    names = soup.find_all("p", class_="bib")

    if adds == 1:
        result_list = names[-1:]
        result = str(result_list)
        res1 = result.split('\n\t\t\t')
    else:
        result_list = names[-adds:(-adds + 1)]
        result = str(result_list)
        res1 = result.split('\n\t\t\t')
    for i in range(len(res1) - 1):
        if i != (len(res1) - 2):
            numer = int(res1[i][-2:])
            lst = res1[i + 1][3:-17]
            dct[numer] = lst
        else:
            numer = int(res1[i][-2:])
            lst = res1[i + 1][3:-11]
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
    df['number'] = nums
    df['РУС'] = values

    # Choose year
    table = pd.read_excel(r'table.xlsm', sheet_name=str(year), header=1)
    table['РУС'] = [x.strip() for x in table['РУС'].values]
    table = table.rename(columns={'Unnamed: 0': 'number'})
    table['РУС'] = [x.lower().split('*')[0] for x in table['РУС'].values]
    table['EN'] = [x.lower().split('*')[0] for x in table['EN'].values]
    table['FR'] = [x.lower().split('*')[0] for x in table['FR'].values]
    # table.head()

    # Merging
    # Final
    global final
    final = {}
    if lang.upper() == 'EN':
        df = df.merge(table, on='РУС', how='left').drop(['number_y'], axis=1)
        df['EN'] = df['EN'].fillna(df['РУС'].apply(lambda x: x.upper()))
        new = df.groupby('number_x', as_index=True).agg({'EN': 'unique'})

        for index in new.index:
            final[index] = new['EN'][index]
        for key in final.keys():
            final[key] = [str(x) for x in final[key]]
            final[key] = ', '.join(final[key])

    elif lang.upper() == 'FR':
        df = df.merge(table, on='РУС', how='left').drop(['number_y'], axis=1)
        df['FR'] = df['FR'].fillna(df['РУС'].apply(lambda x: x.upper()))
        new = df.groupby('number_x', as_index=True).agg({'FR': 'unique'})

        for index in new.index:
            final[index] = new['FR'][index]
        for key in final.keys():
            final[key] = [str(x) for x in final[key]]
            final[key] = ', '.join(final[key])

    for key in final.keys():
        print('\n', key, ' - ', final[key], '\n')


def start():
    global year, URL, a, ans, lang
    lang_list = ['EN', 'FR']
    year_list = ['2016', '2017', '2018', '2019', '2020', '2021']
    URL = input('Вставь ссылку или список: ')
    if URL != '':  # Проверка на наличие ссылки.

        if 'https://www1.fips.ru/registers-doc-view/fips_servlet?DB=RUTM&DocNumber=' in URL:  # Проверка на корректность ссылки.

            a = input('Введите количество жирных шрифтов под перечнем наименований (1 в случае отсутствия): ')

            if a != '':  # Проверка на наличие значения a.
                try:
                    a = int(a)
                except:
                    a = 'ERROR'

                if a != 'ERROR':
                    lang = input('Выберите язык для перевода (EN/FR): ')

                    if lang == '' or lang.upper() in lang_list:
                        ans = input('Хотите выбрать год словаря? (Да/Нет): ')

                        if ans.lower() == 'да':
                            names_list = recieve_names(URL, a)
                            year = input('Введите нужный год: ')
                            if year == '':
                                year = 2021
                                print('\n', f'Год был подобран автоматически. Год словаря: {year}', '\n')
                            else:
                                try:
                                    year = int(year)
                                except:
                                    year = 'ERROR'

                            if year != 'ERROR':
                                if str(year) in year_list:
                                    translate_names(names_list, year, lang)
                                else:
                                    print('Некорректный ввод: введите релевантный год (2016-2021)!')
                                    start()
                            else:
                                print('Некорректный ввод: введите число!')
                                start()

                        elif ans.lower() == 'нет':
                            names_list = recieve_names(URL, a)
                            print('\n', f'Год был подобран автоматически. Используемый словарь: {year}', '\n')
                            translate_names(names_list, year, lang)

                        else:
                            names_list = recieve_names(URL, a)
                            print('\n', f'Год был подобран автоматически. Используемый словарь: {year}', '\n')
                            translate_names(names_list)
                    else:
                        print('Некорректный ввод: введите язык (EN/FR)!')
                        start()
                else:
                    print('Некорректный ввод: введите целое число!')
                    start()
            else:
                print('Некорректный ввод: значение не должно быть пустым!')
                start()
        else:
            def trans_list():
                global dct_from_list
                global URL
                dct_from_list = {}
                n_list = URL.split('.')[:-1]
                for i in n_list:
                    values = i.split(' - ')
                    dct_from_list[values[0]] = values[1].split('; ')
                lang = input('Выберите язык для перевода (EN/FR): ')
                if lang == '' or lang.upper() in lang_list:
                    year = input('Введите нужный год: ')
                    try:
                        year = int(year)
                    except:
                        year = 'ERROR'
                    if year != 'ERROR':
                        if str(year) in year_list:
                            translate_names(dct_from_list, year, lang)
                        else:
                            print('Некорректно введён год. Выберите промежуток 2016-2021!')
                            trans_list()
                    else:
                        print('Некорректно введён год. Введите число!')
                        trans_list()
                else:
                    print('Некорректно введён язык. Выберите из предложенного (EN/FR)!')
                    trans_list()

            try:
                trans_list()
            except:
                print('Вставьте корректную ссылку или правильно скопируйте список!')
                start()

    else:
        print('Некорректный ввод: значение не должно быть пустым!')
        start()

start()


