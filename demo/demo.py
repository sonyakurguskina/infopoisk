from flask import Flask, render_template, request, redirect, url_for
from task_5.task_5 import search

app = Flask(__name__)


def convert_search_result_to_links(search_result):
    if search_result is not None and search_result:
        links = []
        for item in search_result:
            name = item.replace("https", "https:").replace("_.html", "").replace('_', '/')
            link = f"{name}"
            links.append(link)
        return links
    else:
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_value = request.form['input_value']
        result = search(input_value)
        links_result = convert_search_result_to_links(result)
        if links_result is not None:
            return redirect(url_for('example', input_value=input_value))
        else:
            return render_template('bad_result.html', input_value=input_value)

    else:
        return '''<html>
                    <head>
                        <title>Страница ввода запроса</title>
                    </head>
                    <body>
                        <form action="/" method="POST">
                            <input type="text" name="input_value" placeholder="Введите запрос">
                            <br><br>
                            <input type="submit" value="Поиск">
                        </form>
                    </body>
                </html>'''


@app.route('/example', methods=['GET'])
def example():
    input_value = request.args.get('input_value')
    result = search(input_value)
    links_result = convert_search_result_to_links(result)

    if links_result is not None:
        total_results = len(links_result)
        results_per_page = 10
        total_pages = (total_results // results_per_page) + 1 if total_results % results_per_page != 0 else total_results // results_per_page
        page = int(request.args.get('page', 1))
        results_start = (page - 1) * results_per_page
        results_end = page * results_per_page
        return render_template('result.html', input_value=input_value, result=links_result, total_pages=total_pages,
                               results_start=results_start, results_end=results_end, total_results=total_results)
    else:
        return render_template('bad_result.html', input_value=input_value)


if __name__ == '__main__':
    app.run()
