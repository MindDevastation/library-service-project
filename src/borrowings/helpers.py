def complete_return(borrowing):
    """
    Marks the borrowing as returned and updates the associated book's inventory.
    """
    borrowing.status = borrowing.Status.RETURNED
    borrowing.save()
    book = borrowing.book
    book.inventory += 1
    book.save()
