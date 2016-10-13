from fantasy import DraftRecommander
import sys

DR = DraftRecommander()
DR.GetData()
DR.GetPlayers()
while True:
    sys.stdout.write('identity: >> ')
    identity = raw_input()
    if  identity == 'o':         #others
        sys.stdout.write('player name: >> ')
        newDrafted = raw_input()
        DR.PutDraftedPool(newDrafted, 'others')
    elif identity == 'm':       #me
        DR.Recommand()
        try:
            sys.stdout.write('player name: >> ')
            newDrafted = raw_input()
            DR.PutDraftedPool(newDrafted, 'me')
        except:
            print 'No such player'
