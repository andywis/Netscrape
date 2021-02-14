#!/usr/bin/env python3

import re

import bs4  # BeautifulSoup
import requests


class NetScraper:
    """
    A class representing a web browser, for automating form-posting
    Uses Requests to post data and BeautifulSoup to parse HTML forms.

    N.B. This is less useful for parsing a JSON-heavy website, as the
    data is not returned as HTML. In that case, plain old requests will
    be a more appropriate tool

    """
    def __init__(self, verbose=False):
        self.session = requests.Session()
        self.last_response = None
        self.verbose = verbose

    def get(self, url):
        """
        returns a BeautifulSoup object for the whole HTML tree
        """
        response = self.session.get(url)
        if self.verbose:
            print(response.status_code)
        self.last_response = response
        html_tree = bs4.BeautifulSoup(response.text, features="lxml")
        return html_tree

    def post(self, url, data):
        """
        post the data to the URL, and return a BeautifulSoup object for the
        HTML tree we get back
        """
        response = self.session.post(url, data)
        if self.verbose:
            print(response.status_code)
        self.last_response = response
        html_tree = bs4.BeautifulSoup(response.text, features="lxml")
        return html_tree

    @staticmethod
    def find_form_with_element_matching(forms, pattern):
        """ find an HTML form where the name of an <input> element matches
        pattern
        N.B. pattern is an exact string match (e.g. pattern in element.name)
        and is not a regex pattern.

        Args:
            forms: BeautifulSoup object from html_tree.find_all('form')
            pattern: a string which is expected to match an <input> element
                name

        Returns:
            the form in forms where there is a matching <input> element.
        """
        _verbose = False
        for form in forms:
            if _verbose:
                print("Searching form (name=%s) for pattern %r" % (
                    form.get('name', ''), pattern))
            for el in form.find_all('input'):
                # if the element doesn't have a name, ignore it
                if el.get('name', '') == '':
                    continue
                if _verbose:
                    print("looking at <input name=\"%s\"...> " % el['name'])
                if pattern in el['name']:
                    return form
        return None

    @staticmethod
    def print_form_details(form):
        print("Form: ", form.get('name', ''))
        for el in form.find_all('input'):
            print("   ", el.get('name', ''), el.get('value', ''), el['type'])

    @staticmethod
    def convert_form_soup_to_requests(form):
        """
        Args:
            form: a BeautifulSoup object representing a <form>
        Returns:
            a dict representing the form <input> elements, suitable for posting
            back to requests.post()

        Thanks to https://stackoverflow.com/a/23001729
        """
        d = {e.get('name', ''): e.get('value', '') for e in
             form.find_all('input', {'name': True})}

        # If the form has <select> elements, insert these too.
        # Currently, no value is selected by default.
        selects = form.find_all('select')
        if selects:
            d.update({e.get('name', ''): e.get('value', '') for e in selects})
        return d

    @staticmethod
    def populate_form(data, fields, remove_matching=None):
        """
        Args:
            data: either a BS4 'form' or a dict of the form data to be
                posted back using Requests. A dict can be created by
                passing the bs4 form through convert_form_soup_to_requests()

            fields: a  list of tuples (name_pattern, value) of the fields
                to populate in the form

            remove_matching: a list of fields to be removed:
                remove any form data where the dict key matches the things
                in remove_matching. e.g. if remove_matching=['pageRatings'],
                remove any entries from the dict 'data' where the key contains
                the word 'pageRatings'
        Returns:
        """
        if isinstance(data, bs4.element.Tag):
            data = NetScraper.convert_form_soup_to_requests(data)

        if not isinstance(data, dict):
            print(type(data))
            raise ValueError("data is not in a suitable format.")

        # populate the form from 'fields'
        for key in data.keys():
            for name, value in fields:
                if name in key:
                    data[key] = value

        # remove any fields we don't need (see remove_matching)
        if remove_matching:
            for key_pattern_to_delete in remove_matching:
                keys_to_delete = []
                for key in data.keys():
                    if key_pattern_to_delete in key:
                        keys_to_delete.append(key)
                for key in keys_to_delete:
                    del data[key]

        return data


#
#
#
#
#


fixture_1_select = '''
<br><form>
    <input id="EasySitePB" name="EasySitePostBack" type="hidden" value=""/>
    <input id="espr_txtLocation" name="espr$txtLocation" value="AB34 5FG"/>
    <select class="form-group oDataFormInputText" 
        id="espr_ctl00_addrlist" 
        name="espr$ctl00$addrlist" style="display: block">
        <option value="0">Please select ....</option>
        <option value="123456701">2, SOMEWHERE ROAD, ANYTOWN</option>
        <option value="123456702">4, SOMEWHERE ROAD, ANYTOWN</option>
        <option value="123456703">6, SOMEWHERE ROAD, ANYTOWN</option>
        <option value="123456704">8, SOMEWHERE ROAD, ANYTOWN</option>
    </select>
</form><br>'''


def test_add_select_to_dict():
    expected_data = {'EasySitePostBack': '',
                     'espr$txtLocation': 'AB34 5FG',
                     'espr$ctl00$addrlist': ''}
    browser = NetScraper()
    html_tree = bs4.BeautifulSoup(fixture_1_select, features="lxml")
    forms = html_tree.find_all('form')
    form = browser.find_form_with_element_matching(forms, '$txtLocation')

    data_out = browser.convert_form_soup_to_requests(form)
    assert data_out == expected_data


def test_get_value_from_select():
    browser = NetScraper()
    html_tree = bs4.BeautifulSoup(fixture_1_select, features="lxml")
    forms = html_tree.find_all('form')
    form = browser.find_form_with_element_matching(forms, '$txtLocation')

    r = form.find("option", string="4, SOMEWHERE ROAD, ANYTOWN")
    assert r.get('value', '') == '123456702'
