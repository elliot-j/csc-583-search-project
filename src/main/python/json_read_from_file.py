import json


class JSONReadFromFile:
    """
    A class reading the and parsing the JSON data
    """

    def __init__(self, data):
        """
        Constructor to set the fields of the JSON file.
        :param data: The data dictionary containing the fields of the JSON file.
        :type data: dict
        """
        self.id = data['id']
        self.submitter = data['submitter']
        self.authors = data['authors']
        self.title = data['title']
        self.comments = data['comments']
        self.journal_ref = data['journal-ref']
        self.doi = data['doi']
        self.report_no = data['report-no']
        self.categories = data['categories']
        self.license = data['license']
        self.abstract = data['abstract']
        self.versions = data['versions']
        self.update_date = data['update_date']
        self.authors_parsed = data['authors_parsed']

    @staticmethod
    def parse_arxiv_data(json_file: str):
        """
         Parses the given JSON file and returns a list of JSONReadFromFile objects.
         :param json_file: The path to the JSON file to parse.
         :type json_file: str
         :return: A list of JSONReadFromFile objects representing the data in the JSON file.
         :rtype: list of JSONReadFromFile
         """
        documents = []
        with open(json_file, 'r') as f:
            for line in f:
                data = json.loads(line)
                document = JSONReadFromFile(data)
                documents.append(document)
        return documents

    def get_all_attributes(self):
        """
         Returns a dictionary containing all attributes of the JSONReadFromFile object.
         :return: A dictionary containing all attributes of the JSONReadFromFile object.
         :rtype: dict
         """
        return vars(self)
