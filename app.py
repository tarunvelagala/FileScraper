import re
from ssl import CertificateError
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from bs4 import BeautifulSoup
from flask import Flask, redirect, url_for, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'any secret string'
app.static_folder = 'static'


class Searchform(FlaskForm):
    url = URLField(
        validators=[DataRequired(message='Please enter a URL')])

    """def validate_url(self, field):
        try:
            if not re.match('https?://(?:www)?(?:[\w-]{2,255}(?:\.\w{2,6}){1,2})(?:/[\w&%?#-]{1,300})?', field.data):
                raise ValidationError('Please enter a valid URL')
            urlopen(field.data)
        except URLError:
            raise ValidationError('Cannot open the URL ' + field.data)
        except CertificateError:
            raise ValidationError('Please check the URL')"""


@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def hello_world():
    form = Searchform()
    return render_template('index.html', form=form)


def process(url):
    global contents, contents0
    urls_filtered = {}
    pdfs_filtered = {}
    url_name = urlopen(url)
    bsObj = BeautifulSoup(url_name.read(), 'lxml')
    url_parse_obj = urlparse(url)
    url_rel = url_parse_obj.scheme + '://' + url_parse_obj.netloc + '/'
    urls = {link.text.strip().capitalize(): link.get('href') for link in bsObj.find_all('a') if
            link.get('href') != '#' and link.get('href') is not None and str(link.get('href')).find(
                '.pdf') == -1}
    for k, v in sorted(urls.items()):
        if str(v).startswith('https://') or str(v).startswith('http://'):
            urls_filtered.update({k: v})
        else:
            urls_filtered.update({k: url_rel + v})
    pdfs = {link.text.strip().capitalize(): link.get('href') for link in bsObj.find_all('a') if
            link.get('href') != '#' and link.get('href') is not None and str(link.get('href')).find(
                '.pdf') != -1}
    for k, v in sorted(pdfs.items()):
        if str(v).startswith('https://') or str(v).startswith('http://'):
            pdfs_filtered.update({k: v})
        else:
            pdfs_filtered.update({k: url_rel + v})
    urls_filtered_alp = {}
    for k, v in urls_filtered.items():
        if str(k)[:-len(k) + 1].isdigit():
            urls_filtered_alp.setdefault('#', []).append({k: v})
        elif re.match('[@_!+#$%^&*()<>?/|}{~:.]', k[:-len(k) + 1]):
            urls_filtered_alp.setdefault('&', []).append({k: v})
        else:
            urls_filtered_alp.setdefault(str(k)[:-len(k) + 1], []).append({k: v})
    pdfs_filtered_alp = {}
    for k, v in pdfs_filtered.items():
        if str(k)[:-len(k) + 1].isdigit():
            pdfs_filtered_alp.setdefault('#', []).append({k: v})
        elif re.match('[@_!+#$%^&*()<>?/|}{~:.]', k[:-len(k) + 1]):
            urls_filtered_alp.setdefault('&', []).append({k: v})
        else:
            pdfs_filtered_alp.setdefault(str(k)[:-len(k) + 1], []).append({k: v})
    contents0 = [{'urls': urls_filtered}, {'pdfs': pdfs_filtered}]
    contents = [{'urls': urls_filtered_alp}, {'pdfs': pdfs_filtered_alp}]
    return contents0, contents


@app.route('/success', methods=['POST'])
def success():
    form = Searchform()
    if request.method == 'POST':
        url = request.form.get('url')
        if form.validate_on_submit():
            try:
                contents1, contents2 = process(url)
            except (URLError, CertificateError) as e:
                flash(str(e.__class__.__name__) + '.Please enter a valid URL', 'info')
                return redirect(url_for('hello_world'))
            # process(url)
            return render_template('success.html', contents=contents2, contents0=contents1)


if __name__ == '__main__':
    app.run()
