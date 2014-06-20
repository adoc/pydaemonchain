def update_book(book, address, amount):
    """Given `book`, a dictionary of addresses and balances, increment
    the `address` given by `amount`.
    """

    if address not in book:
        book[address] = 0
    #print(address, book[address], amount)
    assert address == 'coinbase' or book[address] + amount >= 0, "Incorrect parsing. Should not be negative addresses. %s." % address
    book[address] += amount
    if book[address] == 0: # Still zero, delete it.
        del book[address]

def cull_book(book, min=0):
    """Remove all Zero-balance addresses from the book.
    """
    for address, amount in book.items():
        if amount <= min:
            del book[address]
    return book