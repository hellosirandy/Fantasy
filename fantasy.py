import requests
import csv


class DraftRecommander:
    def __init__(self):
        self.rawData = {}
        self.remainPool = {}
        self.othersDraftedPool = []
        self.myDraftedPool = []
        self.othersAverageStats = {'FG%': 0, 'FT%': 0, '3PTM': 0, 'PTS': 0, 'REB': 0, 'AST': 0, 'ST': 0, 'BLK': 0, 'TO': 0}
        self.myAverageStats = {'FG%': 0, 'FT%': 0, '3PTM': 0, 'PTS': 0, 'REB': 0, 'AST': 0, 'ST': 0, 'BLK': 0, 'TO': 0}
    def GetData(self):
        url = "http://stats.nba.com/leaders"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'}

        with requests.Session() as session:
            session.headers = headers
            session.get(url, headers=headers)

            params = {
                'LeagueID': '00',
                'PerMode' : 'PerGame',
                'StatCategory': 'PTS',
                'Scope': 'S',
                'Season': '2015-16',
                'SeasonType': 'Regular Season',
            }

            response = session.get('http://stats.nba.com/stats/leagueleaders', params=params)
            results = response.json()
            self.rawData['headers'] = results['resultSet']['headers']
            self.rawData['rows'] = results['resultSet']['rowSet']
    def GetPlayers(self):
        for row in self.rawData['rows']:
            row = dict(zip(self.rawData['headers'], row))
            self.remainPool[str(row['PLAYER'])] = {'FG%': row['FG_PCT'], 'FT%': row['FT_PCT'], '3PTM': row['FG3M']
                , 'PTS': row['PTS'], 'REB': row['REB'], 'AST': row['AST'], 'ST': row['STL'], 'BLK': row['BLK']
                , 'TO': row['TOV']}
    def OutputCSV(self):
        with open('stats.csv', 'w') as csvfile:
            fieldnames = ['Player', 'FG%', 'FT%', '3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK', 'TO']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in self.rawData['rows']:
                row = dict(zip(self.rawData['headers'], row))
                writer.writerow({'Player': row['PLAYER'], 'FG%': row['FG_PCT'], 'FT%': row['FT_PCT'], '3PTM': row['FG3M']
                    , 'PTS': row['PTS'], 'REB': row['REB'], 'AST': row['AST'], 'ST': row['STL'], 'BLK': row['BLK']
                    , 'TO': row['TOV']})
    def PutDraftedPool(self, playerName, identity):
        if identity == 'others':
            self.othersDraftedPool.append(playerName)
        elif identity == 'me':
            self.myDraftedPool.append(playerName)
        self.UpdateAverage(playerName, identity)
        self.remainPool.pop(playerName, None)
    def UpdateAverage(self, playerName, identity):
        if identity == 'others':
            draftedNum = len(self.othersDraftedPool)
            for key, value in self.othersAverageStats.iteritems():
                self.othersAverageStats[key] = (value * (draftedNum - 1) + self.remainPool[playerName][key]) / draftedNum
            print 'others average: ' + str(self.othersAverageStats)
        elif identity == 'me':
            draftedNum = len(self.myDraftedPool)
            print draftedNum
            for key, value in self.myAverageStats.iteritems():
                self.myAverageStats[key] = (value * (draftedNum - 1) + self.remainPool[playerName][key]) / draftedNum
            print 'my average: ' + str(self.myAverageStats)
    def Recommand(self):
        maxInfluence = -100
        losingItems = {}
        recommandPlayer = ''
        for key, value in self.myAverageStats.iteritems():
            myValue = self.myAverageStats[key]
            othersValue = self.othersAverageStats[key]
            if (not key == 'TO' and myValue < othersValue) or (key == 'TO' and myValue > othersValue):
                losingItems[key] = {'my': myValue, 'others': othersValue}
        for rkey, rvalue in self.remainPool.iteritems():
            influence = 0
            for lkey, lvalue in losingItems.iteritems():
                myValue = self.myAverageStats[lkey]
                othersValue = self.othersAverageStats[lkey]
                newPlayerValue = rvalue[lkey]
                influence += (newPlayerValue - myValue) / (othersValue - myValue)
            if influence > maxInfluence:
                maxInfluence = influence
                recommandPlayer = rkey
        print recommandPlayer

