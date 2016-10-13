import requests
import csv
import operator
import sys

class Recommender:
    def __init__(self):
        self.rawData = {}
        self.remainPool = {}
        self.othersDraftedPool = []
        self.myDraftedPool = []
        self.othersAverageStats = {'FGM': 0, 'FGA': 0, 'FG%': 0, 'FTM': 0, 'FTA': 0, 'FT%': 0, '3PTM': 0, 'PTS': 0, 'REB': 0, 'AST': 0, 'ST': 0, 'BLK': 0, 'TO': 0}
        self.myAverageStats = {'FGM': 0, 'FGA': 0, 'FG%': 0, 'FTM': 0, 'FTA': 0, 'FT%': 0, '3PTM': 0, 'PTS': 0, 'REB': 0, 'AST': 0, 'ST': 0, 'BLK': 0, 'TO': 0}
    
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
            self.remainPool[str(row['PLAYER'])] = {'FGM': row['FGM'], 'FGA': row['FGA'], 'FG%': row['FG_PCT'], 'FTM': row['FTM'], 'FTA': row['FTA'], 'FT%': row['FT_PCT'], '3PTM': row['FG3M'], 'PTS': row['PTS'], 'REB': row['REB'], 'AST': row['AST'], 'ST': row['STL'], 'BLK': row['BLK'], 'TO': row['TOV']}

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
        elif identity == 'my':
            self.myDraftedPool.append(playerName)
        self.UpdateAverage(playerName, identity)
        self.remainPool.pop(playerName, None)

    def UpdateAverage(self, playerName, identity):
        if identity == 'others':
            draftedNum = len(self.othersDraftedPool)
            for key, value in self.othersAverageStats.iteritems():
                if key == 'FGM' or key == 'FGA' or key == 'FTM' or key == 'FTA':
                    self.othersAverageStats[key] = value + self.remainPool[playerName][key]
                elif not key == 'FG%' and not key == 'FT%':
                    self.othersAverageStats[key] = (value * (draftedNum - 1) + self.remainPool[playerName][key]) / draftedNum
            self.othersAverageStats['FG%'] = self.othersAverageStats['FGM'] / self.othersAverageStats['FGA']
            self.othersAverageStats['FT%'] = self.othersAverageStats['FTM'] / self.othersAverageStats['FTA']
        elif identity == 'my':
            draftedNum = len(self.myDraftedPool)
            for key, value in self.myAverageStats.iteritems():
                if key == 'FGM' or key == 'FGA' or key == 'FTM' or key == 'FTA':
                    self.myAverageStats[key] = value + self.remainPool[playerName][key]
                elif not key == 'FG%' and not key == 'FT%':
                    self.myAverageStats[key] = (value * (draftedNum - 1) + self.remainPool[playerName][key]) / draftedNum
            self.myAverageStats['FG%'] = self.myAverageStats['FGM'] / self.myAverageStats['FGA']
            self.myAverageStats['FT%'] = self.myAverageStats['FTM'] / self.myAverageStats['FTA']

    def Recommend(self):
        rank = {}
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
                singleInfluence = (newPlayerValue - myValue) / (othersValue - myValue)
                if singleInfluence > 1:
                    singleInfluence = 1
                influence += singleInfluence
            rank[rkey] = influence
            if influence > maxInfluence:
                maxInfluence = influence
                recommandPlayer = rkey
        sortedRank = sorted(rank.items(), key = operator.itemgetter(1), reverse = True)

        print '---------- Recommended List ----------'
        for i in range(0, 5):
            print sortedRank[i][0]
        print '--------------------------------------'

    def DumpStats(self, identity):
        identityStats = []
        if identity == 'others':
            identityStats = self.othersAverageStats
        elif identity == 'my':
            identityStats = self.myAverageStats
        print '---------- ' + str(identity) + ' stats ' + '----------'
        for key, value in identityStats.iteritems():
            print str(key) + '\t' + str(value).expandtabs(30)
        print '-----------------------------------'

class UserInterface:
    def __init__(self, recommender):
        self.recommender = recommender
        self.recommender.GetData()
        self.recommender.GetPlayers()
        self.amount = 12
        self.situation = {'now': 0, 'way': True}
    def Start(self):
        self.InputOrder()
        self.Drafting()
    def InputOrder(self):
        order = -1
        while not order > 0 or not order <= self.amount:
            sys.stdout.write('Order: (enter a digit between 1 and ' + str(self.amount) + ') >> ')
            try:
                order = eval(raw_input())
                self.order = order
            except:
                continue
    def Drafting(self):
        self.NextUp()
        while True:
            if  not self.situation['now'] == self.order:
                sys.stdout.write("Number " + str(self.situation['now']) + ": >> ")
                self.InputPlayer('others')
            else:
                self.recommender.Recommend()
                sys.stdout.write("Your turn: >> ")
                self.InputPlayer('my')

    def NextUp(self):
        if self.situation['way']:
            if self.situation['now'] == self.amount:
                self.situation['way'] = False
            else:
                self.situation['now'] += 1
        else:
            if self.situation['now'] == 1:
                self.situation['way'] = True
            else:
                self.situation['now'] -= 1

    def InputPlayer(self, identity):
        name = raw_input()
        if name[0] == '-':
            self.InputCommand(name)
        else:
            try:
                self.recommender.PutDraftedPool(name, identity)
                if not self.situation['now'] == self.order:
                    print 'Number ' + str(self.situation['now']) + ' has choosed ' + name + '.'
                else:
                    print 'You have choosed ' + name + '.'
                self.NextUp()
            except:
                print 'No such player'

    def InputCommand(self, command):
        if command == '-h':
            print ' -do: ' + '\t' + 'dump others stats'.expandtabs(30)
            print ' -dm: ' + '\t' + 'dump my stats'.expandtabs(30)
        elif command == '-do':
            self.recommender.DumpStats('others')
        elif command == '-dm':
            self.recommender.DumpStats('my')


