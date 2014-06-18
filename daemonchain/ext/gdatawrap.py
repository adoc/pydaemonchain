import string
import gdata.docs.client

try:
    range = xrange
except NameError:
    pass


def CreateClient(config):
    """Create a service client."""
    client = config.SERVICE(source=config.APP_NAME)
    client.http_client.debug = config.DEBUG
    try:
        client.ClientLogin(config.LOGIN, config.PASSWORD,config.APP_NAME)
    except gdata.client.BadAuthentication:
        exit('Invalid user credentials given.')
    except gdata.client.Error:
        exit('Login Error')
    return client


def _search_feed_id(target_id, feed):
    """Search a feed and return the object with the given `target_id`.
    """
    for item in feed.entry:
        id_ = item.id.text.split('/')[-1]
        if id_ == target_id:
            return item


class Worksheet(object):
    def __init__(self, client, sheet_id, wsheet_id):
        """Construct a `Worksheet` object with the given `client`,
        `sheet_id` and 'wsheet_id'.
        """
        self._client = client
        self._sheet_id = sheet_id
        self._wsheet_id = wsheet_id
        self._sheet = _search_feed_id(sheet_id,
                                      client.GetSpreadsheetsFeed())
        self._wsheet = _search_feed_id(wsheet_id,
                                       client.GetWorksheetsFeed(sheet_id))

    def _iter_rows(self):
        """Iterate the rows in this worksheet.
        """
        for row in self._client.GetListFeed(self._sheet_id,
                                            wksht_id=self._wsheet_id).entry:
            yield row

    @property
    def row_count(self):
        """Return a count of the rows.
        # Not in use
        """
        return len(list(self._iter_rows()))

    def clear_sheet(self):
        """Clear the rows of the sheet, not including the Header.
        """
        for row in self._iter_rows():
            self._client.DeleteRow(row)

    def get_row(self, row_idx):
        """Get a row by it's index.
        # Not in use.
        """
        i = 0
        for row in self._iter_rows():
            if i == row_idx:
                return row
            i += 1

    def update_cell(self, row, col, val):
        """Update a cell with the given row and col position. (1 index)
        """
        return self._client.UpdateCell(row, col, val, self._sheet_id,
                                       wksht_id=self._wsheet_id)

    def insert_row(self, data):
        """Inserts a row in to the spreadsheet.
        """
        return self._client.InsertRow(data, self._sheet_id, self._wsheet_id)