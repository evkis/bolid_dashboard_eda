import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import plotly.express as px
import streamlit as st
import warnings
import datetime as dt


warnings.filterwarnings('ignore')
st.set_page_config(page_title="BOLID EDA", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: ДЭШБОРД ДЛЯ АНАЛИЗА ДАННЫХ БОЛИД")

st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

st.markdown("[сайт компании болид](https://bolid.team )")

def main(df1,df2):    
    df1.columns=df1.columns.str.lower()
    df2.columns=df2.columns.str.lower()
    # translating/renaming columns into english
    df1.rename(columns={'дата/время':'date_time','магазин':'seller','имя кассы':'cashier',\
                       'фп':'ff','номер документа':'doc_number',\
                       'номер смены':'shift_number','номер чека за смену':'check_number',\
                       'признак расчета':'calculation','наличными':'cash',\
                       'электронными':'e_pay','итого':'total_pay','статус':'status','город':'city',},inplace=True)
   # translating/renaming columns into english
    df2.rename(columns={'фп':'ff','номер документа':'doc_number','дата/время':'date_time',\
                        'номер смены':'shift_number',\
                        'наименование':'service','итого по чеку':'final_check',\
                        'наличными по чеку':'cash_check',\
                        'электронными по чеку':'e_pay_check','цена товара':'price',\
                        'количество единиц измерения в чеке':'changes_in_check',\
                        'номер товара в чеке':'position_in_check','сумма товара':'summ',\
                        'название игры':'game_name','группа игры':'group_game'},inplace=True)

    def to_lower_if_string(x):
        if isinstance(x, str):
            return x.lower()
        return x

    df1 = df1.applymap(to_lower_if_string)
    df2 = df2.applymap(to_lower_if_string)
    df2.drop('service',axis=1,inplace=True)
    df=pd.merge(df2,df1, on=['ff','date_time','doc_number','shift_number'],how='left')
    df.drop(['final_check','cash_check','e_pay_check','ff','doc_number','shift_number','check_number','position_in_check','cashier','status'],axis=1,inplace=True)

    df['date_time']= pd.to_datetime(df['date_time'])


    df['game_name']=df['game_name'].str.replace('(',' ')
    df['game_name']=df['game_name'].str.replace(')',' ')
    df['game_name']=df['game_name'].str.strip()
    df['game_name'] = df['game_name'].str.replace('гоу','go')
    df['game_name'] = df['game_name'].str.replace('банки2','банки 2')
    df['game_name']=df['game_name'].str.replace(r'\d{4}$', '', regex=True)
    df['game_name']=df['game_name'].str.replace(r'\d{3}$', '', regex=True)
    df['game_name'] = df['game_name'].str.replace('шутинг гелери','shooting galler')
    df['game_name']=df['game_name'].str.strip()

    st.sidebar.header("Выберите фильтры: ")

    start_date = pd.to_datetime(df["date_time"]).min()
    end_date = pd.to_datetime(df["date_time"]).max()

    date1=pd.to_datetime(st.sidebar.date_input("Начальная Дата", start_date))
    date2=pd.to_datetime(st.sidebar.date_input("Конечная Дата", end_date))
    df = df[(df["date_time"] >= date1) & (df["date_time"] <= date2)].copy()


    city = st.sidebar.multiselect("Выберите город", df["city"].unique())


    if not city:
        df2 = df.copy()
    else:
        df2 = df[df["city"].isin(city)]

    seller = st.sidebar.multiselect("Выберите точку продаж", df2["seller"].unique())              #REGION

    if not seller:
        df3 = df2.copy()
    else:
        df3 = df2[df2["seller"].isin(seller)]

    group_game = st.sidebar.multiselect("Выберите группу игр", df3["group_game"].unique())              #REGION

    if not group_game:
        df4 = df3.copy()
    else:
        df4 = df3[df3["group_game"].isin(group_game)]

    game_name = st.sidebar.multiselect("Выберите игру", df4["game_name"].unique())              #REGION

    if not game_name:
        df5 = df4.copy()
    else:
        df5 = df4[df4["game_name"].isin(game_name)]

    price = st.sidebar.multiselect("Выбирите ценовую категорию:", df5["price"].unique())              #REGION

    if not price:
        df6 = df5.copy()
    else:
        df6 = df5[df5["price"].isin(price)]

    df=df6.copy()


    #общая выручка
    sum=df.summ.sum()

# Количество оказанных услуг
    serv=df.changes_in_check.sum()

# Количество чеков
    check=df.changes_in_check.count()

# операций в чеке
    oper=round(df.changes_in_check.sum()/df.changes_in_check.count(),1)

#средняя стоимость услуги
    av_pr=round(df.summ.sum()/df.changes_in_check.sum())

# procent vozvrata
    ret=round(100*(df.calculation.count()-(df['calculation']== "приход").sum())/df.calculation.count(),2)

    def format_currency(amount):
        return f"{amount:,.0f} ₽"
    def format_per(amount):
        return f"{amount:} %"

    st.markdown("## Основные финансовые показатели:")
    st.write("Возврат учитывается при расчетах только основных показателей.")
    cl1, cl2, cl3 = st.columns((3))

    with cl1:
        st.write("Общая выручка:")
        st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{format_currency(sum)}</p>", unsafe_allow_html=True)

    with cl2:
        st.write("Количество услуг:")
        st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{serv}</p>", unsafe_allow_html=True)
    
    with cl3:
        st.write("Количество чеков:")
        st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{check}</p>", unsafe_allow_html=True)

    cl4, cl5, cl6 =st.columns((3))

    with cl4:
        st.write("Среднее количество операций в чеке:")
        st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{oper}</p>", unsafe_allow_html=True)

    with cl5:
        st.write("Средняя стоимость услуги:")
        st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{format_currency(av_pr)}</p>", unsafe_allow_html=True)
    
    with cl6:
        st.write("Процент возврата:")
        st.markdown(f"<p style='font-size: 24px; font-weight: bold; color: #808080;'>{format_per(ret)}</p>", unsafe_allow_html=True)

    st.markdown("## Категориальные финансовые показатели ₽:")


    city_sales = df.groupby('city')['summ'].sum().reset_index()
    city_sales = city_sales.sort_values(by=['summ'],ascending=False)


#group_game_sales = df.groupby('group_game')['summ'].sum().reset_index()

    seller_sales = df.groupby('seller')['summ'].sum().reset_index()
    seller_sales = seller_sales.sort_values(by=['summ'],ascending=False)

    col1, col2 = st.columns((2))
    with col1:
        st.subheader("Продажи по городам")
        fig = px.bar(city_sales, x='city', y='summ')
        fig.update_xaxes(title='Города')
        fig.update_yaxes(title='Продажи')
        st.plotly_chart(fig,use_container_width=True, height = 300)
    with col2:
        st.subheader("Продажи по точкам продаж")
        fig = px.bar(seller_sales, x='seller', y='summ')
        fig.update_xaxes(title='Точка продаж')
        fig.update_yaxes(title='Продажи')
        st.plotly_chart(fig,use_container_width=True, height = 300)

    cl1, cl2 = st.columns((2))
    with cl1:
        with st.expander("Продажи по городам"):
            st.write(city_sales.style.background_gradient(cmap="Blues"))
            csv = city_sales.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "city_data.csv", mime = "text/csv",
                                help = 'Нажмите, чтобы скачать файл CSV')

    with cl2:
        with st.expander("Продажи по точкам продаж"):
            st.write(seller_sales.style.background_gradient(cmap="Blues"))
            sv = seller_sales.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "seller_data.csv", mime = "text/csv",
                               help = 'Нажмите, чтобы скачать файл CSV')

    group_game_sales = df.groupby('group_game')['summ'].sum().reset_index()
    game_name_sales = df.groupby('game_name')['summ'].sum().reset_index()
    game_name_sales = game_name_sales.sort_values(by=['summ'],ascending=False)


    col1, col2 = st.columns((2))
    with col1:
        st.subheader("Продажи по типам игр")
        fig = px.pie(group_game_sales, values = 'summ', names = 'group_game', hole = 0.5)
        fig.update_traces(text = group_game_sales["group_game"], textposition = "inside")
        st.plotly_chart(fig,use_container_width=True, height = 300)
    
    with col2:
        st.subheader("Продажи по играм")
        fig = px.bar(game_name_sales, x='game_name', y='summ')
        fig.update_xaxes(title='Игра')
        fig.update_yaxes(title='Продажи')
        st.plotly_chart(fig,use_container_width=True, height = 300)

    cl1, cl2 = st.columns((2))
    with cl1:
        with st.expander("Продажи по типам игр"):
            st.write(group_game_sales.style.background_gradient(cmap="Blues"))
            csv = group_game_sales.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "group_game_sales_data.csv", mime = "text/csv",
                                help = 'Нажмите, чтобы скачать файл CSV')

    with cl2:
        with st.expander("Продажи по играм"):
            st.write(game_name_sales.style.background_gradient(cmap="Blues"))
            csv = game_name_sales.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "seller_data.csv", mime = "text/csv",
                                help = 'Нажмите, чтобы скачать файл CSV')
        
# Группируйте данные по городам и вычислите абсолютные продажи
    price_sales = df.groupby('price')['summ'].sum().reset_index()

    df = df[df['calculation'] == 'приход']
# Сумма оплаты по наличным и электронным деньгам
    cash = df['cash'].sum()
    e_pay = df['e_pay'].sum()

# Создание DataFrame для построения круговой диаграммы
    payment_summary = pd.DataFrame({'Метод оплаты': ['Наличные', 'Электронные'], 'Сумма': [cash, e_pay]})


    col1, col2 = st.columns((2))
    with col1:
        st.subheader("Продажи по ценовой категории")
        fig = px.pie(price_sales, values = 'summ', names = 'price', hole = 0.5)
        fig.update_traces(text = price_sales["price"], textposition = "inside")
        st.plotly_chart(fig,use_container_width=True, height = 300)
    with col2:
        st.subheader("Оплата по методам")
# Построение круговой диаграммы
        fig = px.pie(payment_summary, values='Сумма', names='Метод оплаты', hole=0.5)
        fig.update_traces(text = payment_summary["Сумма"], textposition = "inside")
        st.plotly_chart(fig,use_container_width=True, height = 300)

    cl1, cl2 = st.columns((2))
    with cl1:
        with st.expander("Продажи по ценовой категории"):
            st.write(price_sales.style.background_gradient(cmap="Blues"))
            csv = price_sales.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "price_sales_data.csv", mime = "text/csv",
                                help = 'Нажмите, чтобы скачать файл CSV')

    with cl2:
        with st.expander("Оплата по методам"):
            st.write(payment_summary.style.background_gradient(cmap="Blues"))
            csv = payment_summary.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "payment_summary.csv", mime = "text/csv",
                                help = 'Нажмите, чтобы скачать файл CSV')


    df['date_time'] = pd.to_datetime(df['date_time'])
    df['day_of_week'] = df['date_time'].dt.day_name()
    sales_by_day = df.groupby('day_of_week')['summ'].sum().reset_index()
    fig = px.bar(sales_by_day, x='day_of_week', y='summ', title='Продажи по дням недели')
    fig.update_xaxes(title='Дни недели')
    fig.update_yaxes(title='Продажи')
    st.plotly_chart(fig,use_container_width=True, height = 300)
    with st.expander("Продажи по дням недели"):
            st.write(sales_by_day.style.background_gradient(cmap="Blues"))
            csv = sales_by_day.to_csv(index = False)
            st.download_button("Скачать данные", data = csv, file_name = "psales_by_day.csv", mime = "text/csv",
                                help = 'Нажмите, чтобы скачать файл CSV')

    st.markdown("## Временные финансовые показатели:")

    # Создайте боковую панель для выбора периода и параметров скользящего среднего
    time_interval = st.sidebar.selectbox("Выберите временной интервал", ["Месяц", "Неделя", "День", "Год"])
    rolling_window = st.slider("Выберите окно скользящей средней:", min_value=1, max_value=30, step=1, value=7)
    min_periods = st.slider("Выберите минимальный период времени:", min_value=1, max_value=30, step=1, value=3)

    # Преобразуйте дату в соответствующий временной интервал
    if time_interval == "Месяц":
        df['time_interval'] = df['date_time'].dt.strftime('%Y-%m')# Преобразование в строку формата 'ГГГГ-ММ'
    elif time_interval == "Год":
        df['time_interval'] = df['date_time'].dt.year
    elif time_interval == "Неделя":
        df['time_interval'] = df['date_time'].dt.strftime('%Y-%U')  # Преобразование в строку формата 'ГГГГ-НН'
    else:
        df['time_interval'] = df['date_time'].dt.strftime('%Y-%m-%d')  # Преобразование в строку формата 'ГГГГ-ММ-ДД'

    # Группируйте данные по временному интервалу и суммируйте продажи
    grouped_data = df.groupby('time_interval')['summ'].sum().reset_index()

    # Рассчитайте скользящее среднее и добавьте его в DataFrame
    grouped_data['moving_average'] = grouped_data['summ'].rolling(window=rolling_window, min_periods=min_periods).mean()

    with st.expander("Справка скользящая средняя"):
        st.write('Скользящая средняя (Moving Average, MA) в техническом анализе — индикатор, основанный на среднем значении цены за выбранный промежуток времени. MA относится к трендовым индикаторам, сглаживая волатильность и помогая определить направление цены.')
    
    # Создайте интерактивный график с использованием Plotly Express
    fig = px.line(grouped_data, x='time_interval', y=['summ', 'moving_average'], title='Продажи и скользящая средняя')
    fig.update_xaxes(title='Время')
    fig.update_yaxes(title='Продажи')
    st.plotly_chart(fig,use_container_width=True, height = 300)

    with st.expander("Показать данные"):
        st.write(grouped_data.style.background_gradient(cmap="Blues"))
        csv = grouped_data.to_csv(index=False)
        st.download_button('Скачать Данные', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

    if time_interval == "День":
        time_interval_code = 'D'
    elif time_interval == "Неделя":
        time_interval_code = 'W'
    elif time_interval == "Месяц":
        time_interval_code = 'M'
    elif time_interval == "Год":
        time_interval_code = 'Y'


    grouped_data4 = df.set_index('date_time').resample(time_interval_code).agg({'price': 'mean'})

    fig = px.line(grouped_data4, x=grouped_data4.index, y='price',
                  labels={'price': 'Средняя цена услуги'},
                  title=f"Средняя цена услуги ({time_interval.lower()})")
    fig.update_xaxes(title='Время')
    fig.update_yaxes(title='Цена')
    st.plotly_chart(fig, use_container_width=True, height = 300)

    with st.expander("Показать данные"):
        st.write(grouped_data4.style.background_gradient(cmap="Blues"))
        csv = grouped_data4.to_csv(index=False)
        st.download_button('Скачать данные', data = csv, file_name = "price_mean.csv", mime ='text/csv')



    grouped_data2 = df.set_index('date_time').resample(time_interval_code).agg({'changes_in_check': 'count'})

    fig = px.line(grouped_data2, x=grouped_data2.index, y='changes_in_check',
                  labels={'changes_in_check': 'Количество чеков'},
                  title=f"Сумма чеков по времени ({time_interval.lower()})")
    fig.update_xaxes(title='Время')
    fig.update_yaxes(title='Чеки')
    st.plotly_chart(fig, use_container_width=True, height = 300)

    with st.expander("Показать данные"):
        st.write(grouped_data2.style.background_gradient(cmap="Blues"))
        csv = grouped_data2.to_csv(index=False)
        st.download_button('Скачать Данные', data = csv, file_name = "changes_in_check_count.csv", mime ='text/csv')

    #ДИНАМИКА ПРОДАЖ
    st.markdown("## Динамика продаж:")

    date_city = df.groupby(['city','time_interval']).agg({'summ':'sum'}).reset_index()

    fig=px.line(date_city, x='time_interval', y='summ', color='city',title=f"Динамика продаж по городам ({time_interval.lower()})")
    fig.update_xaxes(title='Время')
    fig.update_yaxes(title='Сумма')
    st.plotly_chart(fig, use_container_width=True, height = 300)

    with st.expander("Показать данные динамики продаж по городам"):
        st.write(date_city.style.background_gradient(cmap="Blues"))
        csv = date_city.to_csv(index=False)
        st.download_button('Скачать Данные', data = csv, file_name = "date_city.csv", mime ='text/csv')

    with st.expander("Показать динамику продаж по точкам продаж"):
         date_seller = df.groupby(['seller','time_interval']).agg({'summ':'sum'}).reset_index()
         fig=px.line(date_seller, x='time_interval', y='summ', color='seller',title=f"Динамика продаж по точкам({time_interval.lower()})")
         fig.update_xaxes(title='Время')
         fig.update_yaxes(title='Сумма')
         st.plotly_chart(fig, use_container_width=True, height = 300)


    with st.expander("Показать данные динамики продаж по точкам продаж"):
        st.write(date_seller.style.background_gradient(cmap="Blues"))
        csv = date_seller.to_csv(index=False)
        st.download_button('Скачать Данные', data = csv, file_name = "date_seller.csv", mime ='text/csv')


    with st.expander("Показать динамику продаж по группам игр"):
         date_group = df.groupby(['group_game','time_interval']).agg({'summ':'sum'}).reset_index()
         fig=px.line(date_group, x='time_interval', y='summ', color='group_game',title=f"Динамика продаж по группам игр ({time_interval.lower()})")
         fig.update_xaxes(title='Время')
         fig.update_yaxes(title='Сумма')
         st.plotly_chart(fig, use_container_width=True, height = 300)

    with st.expander("Показать данные динамики продаж по группам игр"):
         st.write(date_group.style.background_gradient(cmap="Blues"))
         csv = date_group.to_csv(index=False)
         st.download_button('Скачать Данные', data = csv, file_name = "date_group.csv", mime ='text/csv')

    with st.expander("Показать динамику продаж по ценовой категории"):
         price_group = df.groupby(['price','time_interval']).agg({'summ':'sum'}).reset_index()
         fig=px.line(price_group, x='time_interval', y='summ', color='price',title=f"Динамика продаж по ценовой категории ({time_interval.lower()})")
         fig.update_xaxes(title='Время')
         fig.update_yaxes(title='Сумма')
         st.plotly_chart(fig, use_container_width=True, height = 300)

    with st.expander("Показать данные динамики продаж по ценовой категории"):
        st.write(price_group.style.background_gradient(cmap="Blues"))
        csv = price_group.to_csv(index=False)
        st.download_button('Скачать Данные', data = csv, file_name = "price_group.csv", mime ='text/csv')

    st.markdown("## Иерархичечкое представление продаж:")

    fig=px.treemap(df, path=['city','seller','group_game','game_name'],values='summ',hover_data=['summ'], color='game_name')
    fig.update_layout(width=800, height=650)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## ABC анализ игр:")

    with st.expander("Справка abc анализ"):
        st.write('ABC-анализ — анализ товарных запасов путём деления на три категории: А — наиболее ценные, 20 % — ассортимента (номенклатура); 80 % — продаж, В — промежуточные, 30 % — ассортимента; 15 % — продаж, С — наименее ценные, 50 % — ассортимента; 5 % — продаж')

    A_threshold = st.slider("Выберите значении для <A:", min_value=50, max_value=100, step=1, value=85)
    B_threshold = st.slider("Выберите <B:", min_value=50, max_value=100, step=1, value=95)

    service_sales = df.groupby('game_name')['summ'].sum().reset_index()


    service_sales_sorted = service_sales.sort_values(by='game_name', ascending=False)

    service_sales_sorted['cumulative_sales'] = service_sales_sorted['summ'].cumsum()
    service_sales_sorted['cumulative_percentage'] = (service_sales_sorted['cumulative_sales'] / service_sales_sorted['summ'].sum()) * 100

    def classify_abc(row):
        if row['cumulative_percentage'] <= A_threshold:
            return 'A'
        elif A_threshold < row['cumulative_percentage'] <= B_threshold:
            return 'B'
        else:
            return 'C'

    service_sales_sorted['abc_category'] = service_sales_sorted.apply(classify_abc, axis=1)


    fig = px.bar(service_sales_sorted, x='game_name', y='summ', text='cumulative_percentage',
                 labels={'game_name': 'Услуги', 'summ': 'Продажи', 'cumulative_percentage': 'Кумулятивный процент продаж'},
                 title='График ABC анализа')
    fig.update_traces(texttemplate='%{text:.2s}%', textposition='outside')

    st.plotly_chart(fig,use_container_width=True)

    with st.expander("Показать данные ABC анализа"):
        st.write(service_sales_sorted.style.background_gradient(cmap="Blues"))
        csv = service_sales_sorted.to_csv(index=False)
        st.download_button('Скачать Данные', data = csv, file_name = "abc_games.csv", mime ='text/csv')

def file_upload():
    col1, col2 = st.columns((2))
    with col1:
        fl1 = st.file_uploader(":file_folder: ЗАГРУЗИТЕ ФАЙЛ CHECKS",type=(["csv"]))
    with col2:
        fl2 = st.file_uploader(":file_folder: ЗАГРУЗИТЕ ФАЙЛ ITEMS",type=(["csv"]))
    if fl1 is not None and fl2 is not None:
        filename1 = fl1.name
        st.write(filename1)
        df1=pd.read_csv(filename1)
        filename2 = fl2.name
        st.write(filename2)
        df2=pd.read_csv(filename2)
        main(df1,df2)
    else:
       st.warning("Загрузите файлы и дождитесь их загрузки.")

if __name__=='__main__': 
    file_upload()
