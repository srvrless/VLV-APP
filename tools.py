from bs4 import BeautifulSoup


def html_parser(html_document):
    try:
        soup = BeautifulSoup(html_document, 'html.parser')
        text = soup.get_text()
        text = text.replace('Описание', '').replace('  ', '')
        return text
    except TypeError: return ''