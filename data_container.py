import csv


class DataPoint:
    """
    each DataPoint represents a single ted talk instance
    it holds all the relevant fields for the talk as well
    as its tf-idf vector that will be used for searching
    """

    def __init__(self, title, speaker_1, all_speakers, occupations,
                 about_speakers, views, recorded_date, published_date, event, native_lang,
                 available_lang, comments, duration, topics, related_talks,
                 url, description, transcript):
                self.title = title
                self.speaker_1 = speaker_1
                self.all_speakers = all_speakers
                self.occupations = occupations
                self.about_speakers = about_speakers
                self.views = views
                self.recorded_date = recorded_date
                self.published_date = published_date
                self.event = event
                self.native_lang = native_lang
                self.available_lang = available_lang
                self.comments = comments
                self.duration = duration
                self.topics = topics
                self.related_talks = related_talks
                self.url = url
                self.description = description
                self.transcript = transcript
                self.vector = []

    def set_vector(self):
        # set the tf-idf vector for the description of this ted-talk
        pass



class DataContainer:

    def __init__(self):
        self.data = {}

    def read_data(self):
        columns = []
        rows = []
        with open('ted_talks_en.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            columns = next(csvreader)
            for row in csvreader:
                rows.append(row)
        for row in rows:
            key = int(row[0])
            val = self.__parse_data_point(row)
            self.data[key] = val

    def __parse_data_point(self, data_point):
        """
        parses through a row from the csv and initializes
        the corresponding DataPoint object that will actually
        get stored in the DataContainer
        """
        title = data_point[1]
        speaker_1 = data_point[2]
        all_speakers = self.__parse_str_dict(data_point[3])
        try:
            occupations = self.__parse_str_dict(data_point[4])
        except IndexError:
            occupations = {}
        about_speakers = self.__parse_str_dict(data_point[5])
        views = int(data_point[6])
        recorded_date = data_point[7]
        published_date = data_point[8]
        event = data_point[9]
        native_lang = data_point[10]
        available_lang = self.__parse_str_list(data_point[11])
        try:
            comments = int(data_point[12])
        except ValueError:
            comments = 0
        duration = int(data_point[13])
        topics = self.__parse_str_list(data_point[14])
        related_talks = self.__parse_str_dict(data_point[15])
        url = data_point[16]
        description = data_point[17]
        transcript = data_point[18]
        new_data_point = DataPoint(title, speaker_1, all_speakers, occupations,
                about_speakers, views, recorded_date, published_date, event, 
                native_lang, available_lang, comments, duration, topics,
                related_talks, url, description, transcript)
        return new_data_point

    def __parse_str_dict(self, str_dict):
        """
        parses the string dictionaries that are in the csv
            (for the speakers, occupations, etc.)
        """
        str_dict = str_dict.replace('"', '\'')
        keys = []
        for i in range(len(str_dict) - 1):
            if str_dict[i + 1] == ':':
                # print(str_dict)
                try:
                    keys.append(int(str_dict[i]))
                except ValueError:
                    continue
        vals = []
        for i in range(len(str_dict)):
            if str_dict[i] == ':':
                if str_dict[i + 2] == '[':
                    new_list = []
                    ind = i + 3
                    while str_dict[ind] != ']':
                        if str_dict[ind] == ',':
                            ind += 2
                        inner_ind = ind + 1
                        new_str = ''
                        while str_dict[inner_ind] != '\'':
                            new_str += str_dict[inner_ind]
                            inner_ind += 1
                        new_list.append(new_str)
                        ind = inner_ind + 1
                    vals.append(new_list)
                else:
                    new_str = ''
                    ind = i + 3
                    while str_dict[ind] != '\'':
                        new_str += str_dict[ind]
                        ind += 1
                    vals.append(new_str)
        new_dict = {}
        for i in range(len(keys)):
            new_dict[keys[i]] = vals[i]
        return new_dict

    def __parse_str_list(self, str_list):
        new_list = str_list[1:-1].split(',')
        new_list[0] = ' ' + new_list[0]
        new_list = [item[2:-1] for item in new_list]
        return new_list
