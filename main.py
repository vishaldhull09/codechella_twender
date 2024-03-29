from flask import Flask, render_template, request, url_for
import tweepy
from datetime import datetime
from datetime import timedelta

from analysis import search
from similar_names import get_names

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'

@app.route("/")
def hello():
    return render_template('index.html')

max_items = 20

@app.route("/feedback", methods=['POST'])
def feedback():

    date = datetime.now()
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    file = open('feedback.csv', 'a')
    file.write(name + ',' + email + ',' + message + ',' + str(date) + '\n')
    return render_template('feedback.html')
   

@app.route("/main")
def main_page():

    global max_items
    query = request.args.get('query')
    # request.args.get('max_items')

    final_list = []
    final_count = []

    query = query.replace('#', '')

    # nltk.download('vader_lexicon')

    dates = []

    for i in range(10):
        N = 10- i
        date_start = datetime.now() - timedelta(days=N)
        date_now = datetime.now() - timedelta(days=N - 1)
        date_until = datetime.now() - timedelta(days=N - 2)

        dates.append(date_now.strftime('%d %b'))

        lis, counts = search(query, max_items, date_start, date_until)

        print("Completed {} of 10".format(i+1))
        final_list.append(lis)
        final_count.append(counts)

    for i in range(len(final_count)):
        temp_list = [final_count[i]['Positive'], final_count[i]['Neutral'] , final_count[i]['Negative']]
        final_count[i] = temp_list

    pos_line_graph_list = []
    neu_line_graph_list = []
    neg_line_graph_list = []

    total_pos = 0
    total_neu = 0
    total_neg = 0

    for i in range(len(final_count)):
        pos_line_graph_list.append(final_count[i][0])
        neu_line_graph_list.append(final_count[i][1])
        neg_line_graph_list.append(final_count[i][2])

        total_pos += final_count[i][0]
        total_neu += final_count[i][1]
        total_neg += final_count[i][2]
    try:
        avg_pos = total_pos/(total_pos + total_neg)
        avg_neg = total_neg/(total_pos + total_neg)
    except ZeroDivisionError:
        return render_template('error.html')

    data = {'tweets': final_list , 'pos_line_data' : pos_line_graph_list
            , 'neu_line_data' : neu_line_graph_list , 'neg_line_data' : neg_line_graph_list
            , 'total_pos' : total_pos , 'total_neu' : total_neu
            , 'total_neg' : total_neg ,'avg_pos' : avg_pos
            , 'avg_neg' : avg_neg ,  'name' : query , 'dates' : dates}

    similar = get_names(query)

    return render_template('main.html', data=data, similar=similar)


@app.route('/compare')
def compare_page():
    global max_items

    btn = request.args.get('btn')
    comp_data = request.args.get('comp_data')
    original = request.args.get('query')

    print("Comparison view")
    print(btn,comp_data,original)

    if len(comp_data.strip()) > 1:
        query = comp_data
    else:
        query = btn


    final_list = []
    final_count = []

    consumer_key = '5iVGW5Q5hU8IQNPlrKFLI1U77'
    consumer_secret = 'usCmpMGbCpvtUWqwkE5r4FnwZgGguOk55TuOwR3epNnGbvV7r5'
    access_token = '1173618983997603841-lFsqOl0zSFO8gMfWqKgTuaN6koRske'
    access_token_secret = 'F2GbdgJD6ewIOIOSvt39mHKxbgYIq7Ap5wAWLCmVaHPWD'
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    dates = []
    for i in range(10):
        N = 10 - i
        date_start = datetime.now() - timedelta(days=N)
        date_now = datetime.now() - timedelta(days=N-1)

        dates.append(date_now.strftime('%d %b'))

        date_until = datetime.now() - timedelta(days=N - 2)

        lis, counts = search(query, max_items, date_start, date_until)

        final_list.append(lis)
        final_count.append(counts)

    for i in range(len(final_count)):
        temp_list = [final_count[i]['Positive'], final_count[i]['Neutral'], final_count[i]['Negative']]
        final_count[i] = temp_list

    pos_line_graph_list = []
    neu_line_graph_list = []
    neg_line_graph_list = []

    total_pos = 0
    total_neu = 0
    total_neg = 0

    for i in range(len(final_count)):
        pos_line_graph_list.append(final_count[i][0])
        neu_line_graph_list.append(final_count[i][1])
        neg_line_graph_list.append(final_count[i][2])

        total_pos += final_count[i][0]
        total_neu += final_count[i][1]
        total_neg += final_count[i][2]
    try:
        avg_pos = total_pos / (total_pos + total_neg)
        avg_neg = total_neg / (total_pos + total_neg)
    except ZeroDivisionError:
        return render_template('error.html')

    data2 = {'tweets': final_list, 'pos_line_data': pos_line_graph_list
        , 'neu_line_data': neu_line_graph_list, 'neg_line_data': neg_line_graph_list
        , 'total_pos': total_pos, 'total_neu': total_neu
        , 'total_neg': total_neg, 'avg_pos': avg_pos
        , 'avg_neg': avg_neg , 'name' : query , 'dates' : dates}

    final_data = {'data2': data2}
    print(original[4:])

    return render_template('compare.html', final_data=final_data, original=original[4:])




if __name__ == '__main__':
    app.run(debug=True)
