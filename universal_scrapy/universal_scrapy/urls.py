
def china(base_url, start, end):
    for page in range(start, end + 1):
        yield base_url.format(page)
