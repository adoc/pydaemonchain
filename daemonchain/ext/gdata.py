"""
"""
import datetime
import gdataext.spreadsheet


class Extension(object):
    """Provides data push to Google Docs.
    """
    @classmethod
    def args(cls, parser):
        parser.add_argument('--gdata-user', required=True,
                            help="Google Docs login user/email.")
        parser.add_argument('--gdata-pass', required=True,
                            help="Google Docs login password.")
        parser.add_argument('--gdata-sheetid', required=True,
                            help="Spreadsheet id.")
        parser.add_argument('--gdata-wsheetid', required=True,
                            help="Worksheet id.")
        parser.add_argument('--gdata-push-interval', default="300",
                            help="Push data every N seconds.")

    def __init__(self, config):
        self.__config = config
        client = gdataext.spreadsheet.create_client(LOGIN=config.gdata_user,
                                                     PASSWORD=config.gdata_pass)
        self.__wsheet = gdataext.spreadsheet.Worksheet(client,
                            config.gdata_sheetid, config.gdata_wsheetid)

    def clear(self):
        self.__wsheet.clear_rows()

    def header(self, *vals):
        # Make Header
        for n, val in enumerate(vals):
            self.__wsheet.update_cell(1, n+1, val)

    def push(self, book):
        #print(dir(self.__wsheet._client))
        self.__wsheet.update_title("Updating...")
        self.__wsheet.clear()
        self.header('Address', 'Balance')
        self.__wsheet.batch_add_rows(book)
        now = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
        self.__wsheet.update_title("(Updated %s)" %now)

