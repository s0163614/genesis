from flask import Flask, render_template, request, redirect, url_for, session
import requests
from bs4 import BeautifulSoup
from flask import send_file
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Не забудьте установить секретный ключ для работы с сессиями

def get_company_info_by_inn(inn):
    url = 'https://www.rusprofile.ru/search'
    params = {'query': inn}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        company_info = {}

        # Извлечение данных из раздела requisites
        requisites_section = soup.find(class_='requisites-ip')
        if requisites_section:
            for dl in requisites_section.find_all('dl'):
                dt = dl.find('dt').text.strip()
                dd = dl.find('dd')
                
                if dd:
                    span = dd.find('span', class_='copy_target')
                    value = span.text.strip() if span else dd.text.strip()
                    company_info[dt] = value

         # Извлечение данных из блока с ОКВЭДами
        okved_tiles = soup.find_all(class_='tile-item okved-tile')
        okved_info = []

        for tile in okved_tiles:
            title = tile.find(class_='tile-item__title')
            if title:
                okved_info.append(title.get_text(strip=True))

            description = tile.find(class_='tile-item__text')
            if description:
                okved_info.append(description.get_text(strip=True))

            main_title = tile.find(class_='tile-item__text-title', string="Основной")
            if main_title:
                main_desc = main_title.find_next('p')
                if main_desc:
                    okved_info.append(f"{main_title.get_text(strip=True)}: {main_desc.get_text(strip=True)}")

            for title in tile.find_all(class_='tile-item__text-title'):
                if title.get_text(strip=True) != "Основной":
                    next_p = title.find_next('p')
                    if next_p:
                        okved_info.append(f"{title.get_text(strip=True)}: {next_p.get_text(strip=True)}")

        company_info['ОКВЭД'] = '<br>'.join(okved_info) if okved_info else 'Дополнительная информация не найдена.'

        return company_info
    else:
        return None  # Если ошибка при запросе

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        inn = request.form.get('inn')
        company_info = get_company_info_by_inn(inn)
        if company_info is None:
            company_info = {'error': 'Компания не найдена или возникла ошибка при запросе.'}
            return render_template('index.html', company_info=company_info)
        else:
            session['company_info'] = company_info
            return redirect(url_for('confirm'))

    return render_template('index.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        if 'confirm' in request.form:
            return redirect(url_for('options'))  # Перейти к выбору из 8 вариантов
        else:
            return redirect(url_for('index'))  # Вернуться на главную страницу

    company_info = session.get('company_info', {})
    return render_template('confirm.html', company_info=company_info)

@app.route('/options', methods=['GET', 'POST'])
def options():
    if request.method == 'POST':
        selected_option = request.form.get('option')
        if selected_option:
            session['selected_option'] = selected_option  # Сохранить выбор пользователя
            return redirect(url_for('radio_selection'))  # Перейти к выбору из 3-х радио-кнопок
        else:
            return redirect(url_for('options'))  # Если ничего не выбрано, остаемся здесь

    return render_template('options.html')

@app.route('/download_file')
def download_file():
    filepath = 'predl.docx'  # Убедитесь, что файл доступен по этому пути
    return send_file(filepath, as_attachment=True)

@app.route('/radio_selection', methods=['GET', 'POST'])
def radio_selection():
    if request.method == 'POST':
        selected_radio_option = request.form.get('radio_option')
        if selected_radio_option:
            session['selected_radio_option'] = selected_radio_option  # Сохранить выбор
            return redirect(url_for('show_selection'))  # Показать результаты
        else:
            return redirect(url_for('radio_selection'))  # Если ничего не выбрано, остаемся здесь

    return render_template('select_option.html')

@app.route('/show_selection', methods=['GET'])
def show_selection():
    selected_option = session.get('selected_option', 'Не выбран')
    selected_radio_option = session.get('selected_radio_option', 'Не выбран')
    company_info = session.get('company_info', {})
    return render_template('result.html', selected_option=selected_option, selected_radio_option=selected_radio_option, company_info=company_info)



if __name__ == '__main__':
    app.run(debug=True)
