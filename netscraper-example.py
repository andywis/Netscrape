#!/usr/bin/env python3

"""
The Netscraper is a Python library that helps you automate reading
something from a website, where submitting forms is necessary.

"""

import os

from NetScraper import NetScraper


def run():
    browser = NetScraper(verbose=True)

    url = os.environ['BASE_URL']
    postcode = os.environ['POSTCODE']
    address = os.environ['ADDRESS']

    # Load the first page
    tree = browser.get(url)

    # Find the correct form and 'Fill it in' (enter the postcode
    # This requires knowledge of the HTML.
    # 'tree' is a 'bs4' object. Use find_all() to find the <form> elements
    # Then use NetScraper.find_form_with_element_matching to find the form
    # that contains an <input> element with a name matching a specific string.
    # We have to do this because the form doesn't have a name or ID.
    forms = tree.find_all('form')
    form = browser.find_form_with_element_matching(forms, '$txtLocation')
    if not form:
        print("Could not find a Form containing $txtLocation")
        return None
    # Populate the form (a 'bs4' object) with the relevant data, returning
    # a dict suitable for passing to 'requests'.
    data = browser.populate_form(form,
                                 fields=[('txtLocation', postcode)],
                                 remove_matching=['pageRatings'])

    # Post the first form.
    # we get a 'bs4' tree object back.
    tree = browser.post(url, data)

    # Find the correct form (again) and choose the address from the dropdown
    forms = tree.find_all('form')
    form = browser.find_form_with_element_matching(forms, '$txtLocation')
    if not form:
        print("Could not find a Form containing $txtLocation")
        return None

    # Choosing from a dropdown isn't (yet) part of populate_form().
    # So we'll do it using the lower-level functions.
    data = browser.convert_form_soup_to_requests(form)
    option = form.find("option", string=address)
    for key in data.keys():
        if 'addrlist' in key:
            data[key] = option.get('value', '')

    # Post the second form
    # this posts both postcode and chosen address, and we get the dates
    # when our rubbish will be collected.
    tree = browser.post(url, data)

    # You can now use BS4 to parse 'tree' for the data you need on the
    # web page
    print(tree)


if __name__ == '__main__':
    run()
